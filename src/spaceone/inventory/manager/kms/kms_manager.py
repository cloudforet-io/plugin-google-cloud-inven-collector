import logging
import re
from typing import Dict, List, Optional, Tuple

from spaceone.inventory.connector.kms.kms_v1 import KMSConnector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel, reset_state_counters, log_state_summary
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResponse
from spaceone.inventory.model.kms.keyring.cloud_service import (
    KMSKeyRingResource,
    KMSKeyRingResponse,
)
from spaceone.inventory.model.kms.keyring.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.kms.keyring.data import KMSKeyRingData

__all__ = ["KMSKeyRingManager"]
_LOGGER = logging.getLogger(__name__)


class KMSKeyRingManager(GoogleCloudManager):
    """
    Google Cloud KMS KeyRing Manager

    KMS KeyRing 리소스를 효율적으로 수집하고 처리하는 매니저 클래스
    - KeyRing 목록 수집
    - KeyRing 상세 정보 처리  
    - 리소스 응답 생성
    """

    connector_name = "KMSConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "KMS"
        self.cloud_service_type = "KeyRing"

    def collect_cloud_service(self, params) -> Tuple[List[CloudServiceResponse], List]:
        """
        KMS KeyRing 리소스를 효율적으로 수집합니다.

        Args:
            params (dict): 수집 파라미터
                - secret_data: 인증 정보
                - options: 옵션 설정

        Returns:
            Tuple[List[CloudServiceResponse], List[ErrorResourceResponse]]:
                성공한 리소스 응답 리스트와 에러 응답 리스트
        """
        _LOGGER.debug("** KMS KeyRing START **")

        # v2.0 로깅 시스템 초기화
        reset_state_counters()

        resource_responses = []
        error_responses = []

        try:
            # Connector 초기화
            kms_connector = self._get_connector(params)

            # 모든 KeyRing 조회
            key_rings = self._list_key_rings(kms_connector, params)
            
            # KeyRing이 없는 경우 적절한 로그 레벨로 처리
            if not key_rings:
                from spaceone.inventory.conf.kms_config import LOG_LEVEL_CONFIG
                log_level = LOG_LEVEL_CONFIG["keyring_not_found"]
                log_method = getattr(_LOGGER, log_level.lower())
                log_method("No KeyRings found in any location")
                return resource_responses, error_responses
            
            _LOGGER.info(f"Found {len(key_rings)} KeyRings to process")

            # 각 KeyRing에 대해 리소스 생성
            for keyring_data in key_rings:
                try:
                    resource_response = self._create_keyring_response(
                        keyring_data, params
                    )
                    resource_responses.append(resource_response)
                except Exception as e:
                    keyring_name = keyring_data.get("name", "unknown")
                    _LOGGER.error(f"Failed to process KeyRing {keyring_name}: {e}", exc_info=True)
                    error_response = self.generate_resource_error_response(
                        e, "KMS", "KeyRing", keyring_name
                    )
                    error_responses.append(error_response)

            _LOGGER.info(f"Successfully processed {len(resource_responses)} KeyRings")

        except Exception as e:
            _LOGGER.error(f"Failed to collect KMS KeyRings: {e}", exc_info=True)
            error_response = self.generate_resource_error_response(
                e, "KMS", "Service", "kms"
            )
            error_responses.append(error_response)

        # v2.0 로깅 시스템: 수집 완료 시 상태 요약 로깅
        log_state_summary()
        _LOGGER.debug("** KMS KeyRing END **")
        _LOGGER.info(f"Collected {len(resource_responses)} KMS KeyRings")
        return resource_responses, error_responses

    def _get_connector(self, params) -> KMSConnector:
        """커넥터 인스턴스를 가져옵니다."""
        return self.locator.get_connector(self.connector_name, **params)

    def _list_key_rings(self, kms_connector: KMSConnector, params: Optional[Dict] = None) -> List[Dict]:
        """
        KMS의 모든 KeyRing을 조회합니다.
        
        성능 최적화:
        - CryptoKey 중첩 조회 제거 (필요시 별도 API로 처리)
        - 메모리 효율적인 데이터 구조 사용

        Args:
            kms_connector: KMS 커넥터 인스턴스
            params: 수집 파라미터 (옵션 설정 포함)

        Returns:
            List[dict]: KeyRing 정보 목록
        """
        try:
            # 옵션에서 location 설정 확인
            options = params.get("options", {}) if params else {}
            specified_locations = options.get("kms_locations", None)

            # Location 설정 로깅
            if specified_locations:
                _LOGGER.info(f"Using specified KMS locations: {specified_locations}")
            else:
                _LOGGER.info("Searching all available KMS locations")

            # KeyRing 기본 정보만 조회 (중첩 조회 제거)
            raw_key_rings = kms_connector.list_all_key_rings(target_locations=specified_locations)
            
            processed_key_rings = []
            for key_ring in raw_key_rings:
                # KeyRing 정보와 CryptoKey 정보 함께 처리
                keyring_data = self._process_keyring_data(key_ring, kms_connector)
                if keyring_data:
                    processed_key_rings.append(keyring_data)

            _LOGGER.info(f"Found {len(processed_key_rings)} key rings")
            return processed_key_rings

        except Exception as e:
            _LOGGER.error(f"Error listing key rings: {e}", exc_info=True)
            raise e

    def _process_keyring_data(self, keyring: Dict, kms_connector: KMSConnector) -> Optional[Dict]:
        """
        KeyRing 데이터를 처리합니다.

        Args:
            keyring: 원본 KeyRing 데이터
            kms_connector: KMS 커넥터 인스턴스

        Returns:
            dict: 처리된 KeyRing 데이터
        """
        try:
            # 기본 정보 추출
            name = keyring.get("name", "")
            create_time = keyring.get("createTime", "")
            location_id = keyring.get("location_id", "")
            location_data = keyring.get("location_data", {})

            # 정규 표현식을 사용한 KeyRing 이름 파싱
            keyring_pattern = r'projects/([^/]+)/locations/([^/]+)/keyRings/([^/]+)'
            match = re.match(keyring_pattern, name)
            
            if match:
                project_id = match.group(1)
                parsed_location_id = match.group(2)
                keyring_id = match.group(3)
                
                # location_id가 없으면 파싱된 값 사용
                if not location_id:
                    location_id = parsed_location_id
            else:
                _LOGGER.warning(f"Invalid KeyRing name format: {name}")
                return None

            # Location 정보 처리 - 설정에서 표시 이름 가져오기
            from spaceone.inventory.conf.kms_config import LOCATION_DISPLAY_NAMES
            location_display_name = LOCATION_DISPLAY_NAMES.get(location_id, 
                                                             location_data.get("displayName", location_id))

            # CryptoKey 정보 조회
            crypto_keys = self.get_crypto_keys_for_keyring(name, kms_connector)
            
            # 데이터 구조 생성
            return {
                "name": name,
                "keyring_id": keyring_id,
                "project_id": project_id,
                "location_id": location_id,
                "location_display_name": location_display_name,
                "create_time": create_time,
                "display_name": f"{keyring_id} ({location_display_name})",
                "full_location_path": f"projects/{project_id}/locations/{location_id}",
                # CryptoKey 정보 포함
                "crypto_keys": crypto_keys,
                "crypto_key_count": len(crypto_keys),
            }

        except Exception as e:
            _LOGGER.error(f"Error processing KeyRing data: {e}", exc_info=True)
            return None


    def _create_keyring_response(
        self, keyring_data: Dict, params: Dict
    ) -> CloudServiceResponse:
        """
        KeyRing 데이터를 기반으로 리소스 응답을 생성합니다.

        Args:
            keyring_data: KeyRing 데이터
            params: 수집 파라미터

        Returns:
            CloudServiceResponse: KeyRing 리소스 응답
        """
        try:
            keyring_id = keyring_data["keyring_id"]
            project_id = keyring_data["project_id"]
            location_id = keyring_data["location_id"]

            # 리소스 ID 생성
            resource_id = f"{project_id}:{location_id}:{keyring_id}"

            # 리소스 데이터 생성
            keyring_data_obj = KMSKeyRingData(keyring_data, strict=False)

            # 리소스 생성
            resource = KMSKeyRingResource({
                "name": keyring_data["display_name"],
                "account": project_id,
                "data": keyring_data_obj,
                "region_code": location_id,
                "reference": ReferenceModel({
                    "resource_id": resource_id,
                    "external_link": f"https://console.cloud.google.com/security/kms/keyring/manage/{location_id}/{keyring_id}?project={project_id}",
                }),
            })

            # 표준 응답 생성 (다른 모듈들과 동일한 방식)
            return KMSKeyRingResponse({"resource": resource})

        except Exception as e:
            keyring_name = keyring_data.get("name", "unknown")
            _LOGGER.error(f"Failed to create KMS KeyRing response for {keyring_name}: {e}", exc_info=True)
            raise e

    # ===== 선택적 상세 정보 조회 메서드들 =====
    # 필요시에만 호출하여 성능 최적화

    def get_crypto_keys_for_keyring(
        self, keyring_name: str, kms_connector: KMSConnector
    ) -> List[Dict]:
        """
        특정 KeyRing의 CryptoKey 기본 정보를 조회합니다.
        
        Args:
            keyring_name: KeyRing의 전체 이름
            kms_connector: KMS 커넥터 인스턴스

        Returns:
            list: CryptoKey 기본 정보 목록
        """
        try:
            crypto_keys = kms_connector.list_crypto_keys(keyring_name)
            processed_crypto_keys = []

            for crypto_key in crypto_keys:
                # 기본 정보만 처리 (Version 조회 제거)
                processed_key = self._process_crypto_key_data(crypto_key)
                if processed_key:
                    processed_crypto_keys.append(processed_key)

            return processed_crypto_keys

        except Exception as e:
            _LOGGER.warning(f"Error collecting crypto keys for {keyring_name}: {e}")
            return []

    def _process_crypto_key_data(self, crypto_key: Dict) -> Optional[Dict]:
        """
        CryptoKey 기본 데이터만 처리합니다 (성능 최적화).

        Args:
            crypto_key: 원본 CryptoKey 데이터

        Returns:
            dict: 처리된 기본 CryptoKey 데이터
        """
        try:
            # 기본 정보 추출
            name = crypto_key.get("name", "")
            purpose = crypto_key.get("purpose", "")
            create_time = crypto_key.get("createTime", "")

            # 정규 표현식을 사용한 CryptoKey 이름 파싱
            crypto_key_pattern = r'projects/([^/]+)/locations/([^/]+)/keyRings/([^/]+)/cryptoKeys/([^/]+)'
            match = re.match(crypto_key_pattern, name)
            
            if match:
                crypto_key_id = match.group(4)
            else:
                _LOGGER.warning(f"Invalid CryptoKey name format: {name}")
                return None

            # Primary key version 정보
            primary = crypto_key.get("primary", {})
            primary_state = primary.get("state", "")

            # Version template 정보
            version_template = crypto_key.get("versionTemplate", {})
            protection_level = version_template.get("protectionLevel", "")
            algorithm = version_template.get("algorithm", "")

            # 최적화된 데이터 구조
            return {
                "name": name,
                "crypto_key_id": crypto_key_id,
                "purpose": purpose,
                "create_time": create_time,
                "primary_state": primary_state,
                "protection_level": protection_level,
                "algorithm": algorithm,
                "display_name": f"{crypto_key_id} ({purpose})",
                # 성능 최적화: Version 정보는 필요시 별도 API로 조회
                "crypto_key_version_count": 0,  # 기본값
            }

        except Exception as e:
            _LOGGER.error(f"Error processing CryptoKey data: {e}", exc_info=True)
            return None

