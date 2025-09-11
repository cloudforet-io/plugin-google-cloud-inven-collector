import logging
import time
from typing import List, Tuple

from spaceone.inventory.connector.firebase.firebase_v1beta1 import FirebaseConnector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel, reset_state_counters, log_state_summary
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResponse
from spaceone.inventory.model.firebase.app.cloud_service import AppResource, AppResponse
from spaceone.inventory.model.firebase.app.cloud_service_type import CLOUD_SERVICE_TYPES
from spaceone.inventory.model.firebase.app.data import App

_LOGGER = logging.getLogger(__name__)


class FirebaseManager(GoogleCloudManager):
    connector_name = "FirebaseConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params) -> Tuple[List[CloudServiceResponse], List]:
        """
        Firebase 앱별로 클라우드 서비스를 수집합니다.

        Args:
            params: 수집 파라미터 (secret_data, options, schema, filter)

        Returns:
            Tuple[List[CloudServiceResponse], List]: (수집된 앱 리소스들, 에러 응답들)
        """
        _LOGGER.debug("** Firebase App START **")
        start_time = time.time()

        # v2.0 로깅 시스템 초기화
        reset_state_counters()

        collected_cloud_services = []
        error_responses = []

        try:
            project_id = params["secret_data"]["project_id"]
            firebase_connector = self._get_connector(params)

            # Firebase 프로젝트 정보 조회 및 앱 목록 직접 추출
            firebase_project_info = firebase_connector.get_firebase_project_info()
            firebase_apps = firebase_project_info.get("firebaseApps", [])
            
            # Firebase 앱이 없으면 Firebase 서비스가 없는 것으로 간주
            if not firebase_apps:
                _LOGGER.debug(f"Project {project_id} has no Firebase apps")
                return collected_cloud_services, error_responses

            _LOGGER.info(f"Found {len(firebase_apps)} Firebase apps to process")

            # 배치 처리로 최적화: 모든 앱의 상세 정보를 한번에 조회
            processed_apps = self._process_apps_in_batch(firebase_connector, firebase_apps, project_id)

            # 각 앱별로 리소스 응답 생성
            for processed_app_data in processed_apps:
                app_id = processed_app_data.get("appId", "unknown")
                try:
                    # Firebase 앱 리소스 생성
                    app_response = self._create_app_response(processed_app_data, project_id)
                    collected_cloud_services.append(app_response)

                    _LOGGER.debug(f"Collected Firebase App: {app_id}")

                except Exception as e:
                    _LOGGER.error(f"Failed to process Firebase App {app_id}: {e}", exc_info=True)
                    error_response = self.generate_resource_error_response(
                        e, "Firebase", "App", app_id
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(f"Failed to collect Firebase apps for {project_id}: {e}", exc_info=True)
            error_response = self.generate_resource_error_response(
                e, "Firebase", "App", project_id
            )
            error_responses.append(error_response)

        finally:
            # v2.0 로깅 시스템: 수집 완료 시 상태 요약 로깅
            log_state_summary()
            _LOGGER.debug(f"** Firebase App END ** ({time.time() - start_time:.2f}s)")
            _LOGGER.info(f"Collected {len(collected_cloud_services)} Firebase Apps")

        return collected_cloud_services, error_responses

    def _get_connector(self, params) -> FirebaseConnector:
        """커넥터 인스턴스를 가져옵니다."""
        return self.locator.get_connector(self.connector_name, **params)

    def _process_apps_in_batch(self, firebase_connector, firebase_apps: list, project_id: str) -> list:
        """
        Firebase 앱들을 배치로 효율적으로 처리합니다.
        
        성능 최적화:
        - 개별 상세 조회 대신 기본 데이터 활용
        - 필요한 경우에만 상세 정보 조회
        - 에러 발생 시 개별 앱 격리
        
        Args:
            firebase_connector: Firebase 커넥터
            firebase_apps: Firebase 앱 목록
            project_id: 프로젝트 ID
            
        Returns:
            list: 처리된 앱 데이터 목록
        """
        processed_apps = []
        
        for app_data in firebase_apps:
            app_id = app_data.get("appId", "unknown")
            try:
                # 기본 데이터를 우선 사용하고, 필요시에만 상세 조회
                processed_app_data = self._process_single_app(
                    firebase_connector, app_data, project_id
                )
                processed_apps.append(processed_app_data)
                
            except Exception as e:
                _LOGGER.error(f"Failed to process Firebase App {app_id}: {e}", exc_info=True)
                # 에러 발생 시 기본 데이터라도 사용
                fallback_data = self._create_fallback_app_data(app_data, project_id)
                processed_apps.append(fallback_data)
        
        return processed_apps

    def _process_single_app(self, firebase_connector, app_data: dict, project_id: str) -> dict:
        """
        단일 Firebase 앱을 처리합니다.
        
        Args:
            firebase_connector: Firebase 커넥터
            app_data: 앱 기본 데이터
            project_id: 프로젝트 ID
            
        Returns:
            dict: 처리된 앱 데이터
        """
        # name 필드에서 실제 프로젝트 ID 추출 (예: "projects/mkkang-project/androidApps/...")
        actual_project_id = self._extract_project_id_from_name(app_data.get("name", ""))
        
        # 추출 실패 시 경고 로그 출력
        if not actual_project_id:
            _LOGGER.warning(f"Failed to extract project ID from name: {app_data.get('name', 'N/A')}, using fallback: {project_id}")
        
        # 불필요한 expire_time 필터링 (기본값인 경우 제거)
        filtered_app_data = self._filter_app_data(app_data)
        
        # 최종 앱 데이터 구성
        return {
            **filtered_app_data,
            "projectId": actual_project_id or project_id,  # name에서 추출 실패 시 폴백 사용
        }


    def _create_fallback_app_data(self, app_data: dict, project_id: str) -> dict:
        """
        에러 발생 시 사용할 기본 앱 데이터를 생성합니다.
        
        Args:
            app_data: 원본 앱 데이터
            project_id: 프로젝트 ID
            
        Returns:
            dict: 기본 앱 데이터
        """
        # name 필드에서 실제 프로젝트 ID 추출
        actual_project_id = self._extract_project_id_from_name(app_data.get("name", ""))
        
        # 추출 실패 시 경고 로그 출력
        if not actual_project_id:
            _LOGGER.warning(f"Failed to extract project ID from name in fallback: {app_data.get('name', 'N/A')}, using fallback: {project_id}")
        
        # 불필요한 expire_time 필터링 (기본값인 경우 제거)
        filtered_app_data = self._filter_app_data(app_data)
        
        return {
            **filtered_app_data,
            "projectId": actual_project_id or project_id,  # name에서 추출 실패 시 폴백 사용
            "error_fallback": True,  # 에러 발생 표시
        }


    def _extract_project_id_from_name(self, name: str) -> str:
        """
        Firebase 앱의 name 필드에서 프로젝트 ID를 추출합니다.
        
        Args:
            name: Firebase 앱의 name (예: "projects/mkkang-project/androidApps/...")
            
        Returns:
            str: 추출된 프로젝트 ID (예: "mkkang-project")
        """
        if not name or not name.startswith("projects/"):
            return ""
        
        try:
            # "projects/{project_id}/..." 형식에서 project_id 추출
            parts = name.split("/")
            if len(parts) >= 2:
                return parts[1]  # projects/ 다음의 프로젝트 ID
        except Exception as e:
            _LOGGER.warning(f"Failed to extract project ID from name '{name}': {e}")
        
        return ""

    def _filter_app_data(self, app_data: dict) -> dict:
        """
        Firebase 앱 데이터에서 불필요한 필드를 필터링합니다.
        
        Args:
            app_data: 원본 앱 데이터
            
        Returns:
            dict: 필터링된 앱 데이터
        """
        filtered_data = dict(app_data)
        
        # expire_time이 기본값(1970-01-01T00:00:00Z)인 경우 제거
        expire_time = filtered_data.get("expireTime", "")
        if expire_time == "1970-01-01T00:00:00Z":
            filtered_data.pop("expireTime", None)
        
        return filtered_data

    def _create_app_response(self, app_data: dict, project_id: str) -> CloudServiceResponse:
        """
        Firebase 앱 응답 객체를 생성합니다.
        
        Args:
            app_data: Firebase 앱 데이터
            project_id: 프로젝트 ID
            
        Returns:
            CloudServiceResponse: 생성된 앱 응답 객체
        """
        try:
            firebase_app = App(app_data)
            
            # 앱의 플랫폼에 따른 지역 코드 결정
            region_code = self._get_app_region_code(app_data)
            
            app_resource = AppResource({
                "name": firebase_app.display_name,
                "data": firebase_app,
                "reference": ReferenceModel(firebase_app.reference()),
                "region_code": region_code,
                "account": project_id,
            })
            
            # 표준 응답 생성 (다른 모듈들과 동일한 방식)
            return AppResponse({"resource": app_resource})
            
        except Exception as e:
            _LOGGER.error(f"Failed to create Firebase app response: {e}", exc_info=True)
            raise e
    
    def _get_app_region_code(self, app_data: dict) -> str:
        """
        Firebase 앱의 지역 코드를 결정합니다.
        
        Args:
            app_data: Firebase 앱 데이터
            
        Returns:
            str: 지역 코드
        """
        # Firebase 앱은 기본적으로 global이지만, 
        # 특정 조건에 따라 다른 지역 코드를 사용할 수 있음
        platform = app_data.get("platform", "")
        
        # 플랫폼별 기본 지역 설정 (향후 확장 가능)
        platform_regions = {
            "WEB": "global",
            "ANDROID": "global", 
            "IOS": "global"
        }
        
        return platform_regions.get(platform, "global")

