import json
import logging

from spaceone.inventory.connector.kms.keyring_v1 import KMSKeyRingV1Connector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
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

    KMS KeyRing 리소스를 수집하고 처리하는 매니저 클래스
    - KeyRing 목록 수집
    - KeyRing 상세 정보 처리
    - 리소스 응답 생성
    """

    connector_name = "KMSKeyRingV1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    keyring_conn = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "KMS"
        self.cloud_service_type = "KeyRing"

    def collect_cloud_service(self, params):
        """
        KMS KeyRing 리소스를 수집합니다.

        Args:
            params (dict): 수집 파라미터
                - secret_data: 인증 정보
                - options: 옵션 설정

        Returns:
            Tuple[List[KMSKeyRingResponse], List[ErrorResourceResponse]]:
                성공한 리소스 응답 리스트와 에러 응답 리스트
        """
        _LOGGER.debug("** KMS KeyRing START **")

        resource_responses = []
        error_responses = []

        try:
            # Connector 초기화
            self.keyring_conn: KMSKeyRingV1Connector = self.locator.get_connector(
                self.connector_name, **params
            )

            # 모든 KeyRing 조회 (params 전달하여 옵션 적용)
            key_rings = self._list_key_rings(params)
            _LOGGER.info(f"Found {len(key_rings)} KeyRings to process")

            # 각 KeyRing에 대해 리소스 생성
            for keyring_data in key_rings:
                try:
                    resource_response = self._make_keyring_response(
                        keyring_data, params
                    )
                    resource_responses.append(resource_response)
                except Exception as e:
                    keyring_name = keyring_data.get("name", "unknown")
                    _LOGGER.error(f"Failed to process KeyRing {keyring_name}: {e}")
                    error_response = self.generate_error_response(e, "KMS", "KeyRing")
                    error_responses.append(error_response)

            _LOGGER.info(f"Successfully processed {len(resource_responses)} KeyRings")

        except Exception as e:
            _LOGGER.error(f"Failed to collect KMS KeyRings: {e}")
            error_response = self.generate_error_response(e, "KMS", "KeyRing")
            error_responses.append(error_response)

        _LOGGER.debug("** KMS KeyRing END **")
        return resource_responses, error_responses

    def _list_key_rings(self, params=None):
        """
        KMS의 모든 KeyRing을 조회합니다.

        Args:
            params (dict, optional): 수집 파라미터 (옵션 설정 포함)

        Returns:
            List[dict]: KeyRing 정보 목록
        """
        key_rings = []

        try:
            # 옵션에서 location 설정 확인
            options = params.get("options", {}) if params else {}
            target_locations = options.get("kms_locations", None)

            # Location 설정 로깅
            if target_locations:
                _LOGGER.info(f"Using specified KMS locations: {target_locations}")
            else:
                _LOGGER.info("Searching all available KMS locations")

            # 지정된 설정에 따라 KeyRing 조회
            raw_key_rings = self.keyring_conn.list_all_key_rings(
                target_locations=target_locations
            )

            for key_ring in raw_key_rings:
                # 각 KeyRing에 대해 추가 정보 수집
                keyring_data = self._process_keyring_data(key_ring)
                if keyring_data:
                    # KeyRing 내부의 CryptoKey들도 수집
                    crypto_keys = self._collect_crypto_keys(keyring_data["name"])
                    keyring_data["crypto_keys"] = crypto_keys
                    keyring_data["crypto_key_count"] = len(crypto_keys)
                    key_rings.append(keyring_data)

            _LOGGER.info(f"Found {len(key_rings)} key rings")

        except Exception as e:
            _LOGGER.error(f"Error listing key rings: {e}")
            raise e

        return key_rings

    def _collect_crypto_keys(self, keyring_name):
        """
        특정 KeyRing의 CryptoKey들을 수집하고 처리합니다.

        Args:
            keyring_name (str): KeyRing의 전체 이름

        Returns:
            list: 처리된 CryptoKey 정보 목록
        """
        try:
            crypto_keys = self.keyring_conn.list_crypto_keys(keyring_name)
            processed_crypto_keys = []

            for crypto_key in crypto_keys:
                processed_key = self._process_crypto_key_data(crypto_key)
                if processed_key:
                    # CryptoKey 내의 CryptoKeyVersions도 수집
                    crypto_key_versions = self._collect_crypto_key_versions(
                        processed_key["name"]
                    )
                    processed_key["crypto_key_versions"] = crypto_key_versions
                    processed_key["crypto_key_version_count"] = len(crypto_key_versions)
                    processed_crypto_keys.append(processed_key)

            return processed_crypto_keys

        except Exception as e:
            _LOGGER.error(f"Error collecting crypto keys for {keyring_name}: {e}")
            return []

    def _collect_crypto_key_versions(self, crypto_key_name):
        """
        특정 CryptoKey의 CryptoKeyVersion들을 수집하고 처리합니다.

        Args:
            crypto_key_name (str): CryptoKey의 전체 이름

        Returns:
            list: 처리된 CryptoKeyVersion 정보 목록
        """
        try:
            crypto_key_versions = self.keyring_conn.list_crypto_key_versions(
                crypto_key_name
            )
            processed_versions = []

            for version in crypto_key_versions:
                processed_version = self._process_crypto_key_version_data(version)
                if processed_version:
                    processed_versions.append(processed_version)

            return processed_versions

        except Exception as e:
            _LOGGER.error(
                f"Error collecting crypto key versions for {crypto_key_name}: {e}"
            )
            return []

    def _process_crypto_key_version_data(self, version):
        """
        CryptoKeyVersion 데이터를 처리하고 필요한 정보를 추가합니다.

        Args:
            version (dict): 원본 CryptoKeyVersion 데이터

        Returns:
            dict: 처리된 CryptoKeyVersion 데이터
        """
        try:
            # 기본 정보 추출
            name = version.get("name", "")
            state = version.get("state", "")
            protection_level = version.get("protectionLevel", "")
            algorithm = version.get("algorithm", "")
            create_time = version.get("createTime", "")
            generate_time = version.get("generateTime", "")
            destroy_time = version.get("destroyTime", "")
            destroy_event_time = version.get("destroyEventTime", "")
            import_job = version.get("importJob", "")
            import_time = version.get("importTime", "")
            import_failure_reason = version.get("importFailureReason", "")
            reimport_eligible = str(version.get("reimportEligible", False))

            # name에서 Version ID 추출
            # name 형식: projects/{project}/locations/{location}/keyRings/{keyring}/cryptoKeys/{crypto_key}/cryptoKeyVersions/{version_id}
            name_parts = name.split("/")
            if len(name_parts) >= 10:
                version_id = name_parts[9]
            else:
                _LOGGER.warning(f"Invalid CryptoKeyVersion name format: {name}")
                return None

            # 처리된 데이터 구성
            processed_data = {
                "name": name,
                "version_id": version_id,
                "state": state,
                "protection_level": protection_level,
                "algorithm": algorithm,
                "create_time": create_time,
                "generate_time": generate_time,
                "destroy_time": destroy_time,
                "destroy_event_time": destroy_event_time,
                "import_job": import_job,
                "import_time": import_time,
                "import_failure_reason": import_failure_reason,
                "reimport_eligible": reimport_eligible,
                # 원본 데이터를 JSON 문자열로 변환
                "raw_data": json.dumps(version, ensure_ascii=False, indent=2),
            }

            return processed_data

        except Exception as e:
            _LOGGER.error(f"Error processing CryptoKeyVersion data: {e}")
            return None

    def _process_crypto_key_data(self, crypto_key):
        """
        CryptoKey 데이터를 처리하고 필요한 정보를 추가합니다.

        Args:
            crypto_key (dict): 원본 CryptoKey 데이터

        Returns:
            dict: 처리된 CryptoKey 데이터
        """
        try:
            # 기본 정보 추출
            name = crypto_key.get("name", "")
            purpose = crypto_key.get("purpose", "")
            create_time = crypto_key.get("createTime", "")
            next_rotation_time = crypto_key.get("nextRotationTime", "")

            # name에서 CryptoKey ID 추출
            # name 형식: projects/{project_id}/locations/{location}/keyRings/{keyring}/cryptoKeys/{crypto_key_id}
            name_parts = name.split("/")
            if len(name_parts) >= 8:
                crypto_key_id = name_parts[7]
            else:
                _LOGGER.warning(f"Invalid CryptoKey name format: {name}")
                return None

            # Primary key version 정보
            primary = crypto_key.get("primary", {})
            primary_state = primary.get("state", "")
            primary_name = primary.get("name", "")

            # Version template 정보
            version_template = crypto_key.get("versionTemplate", {})
            protection_level = version_template.get("protectionLevel", "")
            algorithm = version_template.get("algorithm", "")

            # 처리된 데이터 구성
            processed_data = {
                "name": name,
                "crypto_key_id": crypto_key_id,
                "purpose": purpose,
                "create_time": create_time,
                "next_rotation_time": next_rotation_time,
                "primary_state": primary_state,
                "primary_name": primary_name,
                "protection_level": protection_level,
                "algorithm": algorithm,
                "display_name": f"{crypto_key_id} ({purpose})",
                # 원본 데이터를 JSON 문자열로 변환
                "raw_data": json.dumps(crypto_key, ensure_ascii=False, indent=2),
            }

            return processed_data

        except Exception as e:
            _LOGGER.error(f"Error processing CryptoKey data: {e}")
            return None

    def _process_keyring_data(self, keyring):
        """
        KeyRing 데이터를 처리하고 필요한 정보를 추가합니다.

        Args:
            keyring (dict): 원본 KeyRing 데이터

        Returns:
            dict: 처리된 KeyRing 데이터
        """
        try:
            # 기본 정보 추출
            name = keyring.get("name", "")
            create_time = keyring.get("createTime", "")
            location_id = keyring.get("location_id", "")
            location_data = keyring.get("location_data", {})

            # name에서 KeyRing ID 추출
            # name 형식: projects/{project_id}/locations/{location}/keyRings/{key_ring_id}
            name_parts = name.split("/")
            if len(name_parts) >= 6:
                project_id = name_parts[1]
                keyring_id = name_parts[5]
            else:
                _LOGGER.warning(f"Invalid KeyRing name format: {name}")
                return None

            # Location 정보 처리
            location_display_name = location_data.get("displayName", location_id)
            location_labels = location_data.get("labels", {})

            # 처리된 데이터 구성
            processed_data = {
                "name": name,
                "keyring_id": keyring_id,
                "project_id": project_id,
                "location_id": location_id,
                "location_display_name": location_display_name,
                "location_labels": location_labels,
                "create_time": create_time,
                "display_name": f"{keyring_id} ({location_display_name})",
                "full_location_path": f"projects/{project_id}/locations/{location_id}",
                # 원본 데이터를 JSON 문자열로 변환
                "raw_data": json.dumps(keyring, ensure_ascii=False, indent=2),
                "location_raw_data": json.dumps(
                    location_data, ensure_ascii=False, indent=2
                ),
            }

            return processed_data

        except Exception as e:
            _LOGGER.error(f"Error processing KeyRing data: {e}")
            return None

    def _make_keyring_response(self, keyring_data, params):
        """
        KeyRing 데이터를 기반으로 리소스 응답을 생성합니다.

        Args:
            keyring_data (dict): KeyRing 데이터
            params (dict): 수집 파라미터

        Returns:
            KMSKeyRingResponse: KeyRing 리소스 응답
        """
        keyring_id = keyring_data["keyring_id"]
        project_id = keyring_data["project_id"]
        location_id = keyring_data["location_id"]

        # 리소스 ID 생성
        resource_id = f"{project_id}:{location_id}:{keyring_id}"

        # 리소스 데이터 생성
        keyring_data_obj = KMSKeyRingData(keyring_data, strict=False)

        # 리소스 생성
        resource = KMSKeyRingResource(
            {
                "name": keyring_data["display_name"],
                "account": project_id,
                "data": keyring_data_obj,
                "region_code": location_id,
                "reference": ReferenceModel(
                    {
                        "resource_id": resource_id,
                        "external_link": f"https://console.cloud.google.com/security/kms/keyring/manage/{location_id}/{keyring_id}?project={project_id}",
                    }
                ),
            }
        )

        # 응답 생성
        return KMSKeyRingResponse({"resource": resource})
