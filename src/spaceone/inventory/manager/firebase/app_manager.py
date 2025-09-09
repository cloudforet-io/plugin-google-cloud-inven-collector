import logging
import time
from typing import List, Tuple

from spaceone.inventory.connector.firebase.firebase_v1beta1 import FirebaseV1Beta1Connector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.firebase.app.cloud_service import AppResource, AppResponse
from spaceone.inventory.model.firebase.app.cloud_service_type import CLOUD_SERVICE_TYPES
from spaceone.inventory.model.firebase.app.data import App

_LOGGER = logging.getLogger(__name__)


class FirebaseAppManager(GoogleCloudManager):
    connector_name = "FirebaseV1Beta1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params) -> Tuple[List[AppResponse], List]:
        """
        Firebase 앱별로 클라우드 서비스를 수집합니다.

        Args:
            params: 수집 파라미터 (secret_data, options, schema, filter)

        Returns:
            Tuple[List[AppResponse], List]: (수집된 앱 리소스들, 에러 응답들)
        """
        _LOGGER.debug("** Firebase App START **")
        start_time = time.time()
        
        # v2.0 로깅 시스템 초기화 (가능한 경우에만)
        if hasattr(self, 'reset_state_counters'):
            self.reset_state_counters()

        collected_cloud_services = []
        error_responses = []

        try:
            project_id = params["secret_data"]["project_id"]
            
            # Firebase 커넥터 초기화
            firebase_conn: FirebaseV1Beta1Connector = self.locator.get_connector(
                self.connector_name, **params
            )

            # Firebase 프로젝트 정보 조회
            firebase_project_info = firebase_conn.get_firebase_project_info()

            # Firebase 서비스가 있는 경우에만 수집
            if not firebase_project_info.get("hasFirebaseServices", False):
                _LOGGER.debug(f"Project {project_id} has no Firebase services")
                return collected_cloud_services, error_responses

            firebase_apps = firebase_project_info.get("firebaseApps", [])
            

            # 각 앱별로 개별 응답 생성
            for app_data in firebase_apps:
                app_id = app_data.get("appId", "unknown")
                try:
                    # 앱 상세 정보 가져오기
                    app_name = app_data.get("name", "")
                    detailed_app_data = firebase_conn.get_app_details(app_name)
                    
                    # 기본 앱 데이터와 상세 정보 병합
                    merged_app_data = {**app_data, **detailed_app_data}

                    # 앱 설정 정보 구성 (플랫폼별)
                    app_config_data = self._build_app_config(merged_app_data)

                    # 최종 앱 데이터 구성
                    enhanced_app_data = {
                        **merged_app_data,
                        "appConfig": app_config_data,
                        "namespace": project_id,  # Firebase 앱의 namespace는 프로젝트 ID
                    }

                    # Firebase 앱 리소스 생성 (v2.0 로깅 포함)
                    app_response = self._create_app_response_with_logging(enhanced_app_data, project_id)
                    collected_cloud_services.append(app_response)

                    _LOGGER.debug(f"Collected Firebase App: {app_id}")

                except Exception as e:
                    _LOGGER.error(f"Failed to process Firebase App {app_id}: {e}", exc_info=True)
                    error_response = self.generate_resource_error_response(
                        e, "Firebase", "App", app_id
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(f"Failed to collect Firebase apps for {project_id}: {e}")
            error_response = self.generate_resource_error_response(
                e, "Firebase", "App", project_id
            )
            error_responses.append(error_response)

        finally:
            # v2.0 로깅 시스템 요약 (가능한 경우에만)
            if hasattr(self, 'log_state_summary'):
                self.log_state_summary()
            _LOGGER.debug(f"** Firebase App END ** ({time.time() - start_time:.2f}s)")
            _LOGGER.debug(f"Collected {len(collected_cloud_services)} Firebase Apps")

        return collected_cloud_services, error_responses

    def _build_app_config(self, app_data: dict) -> dict:
        """플랫폼별 앱 설정 정보를 구성합니다."""
        platform = app_data.get("platform")
        
        if platform == "ANDROID":
            return {"package_name": app_data.get("packageName")}
        elif platform == "IOS":
            return {"bundle_id": app_data.get("bundleId")}
        elif platform == "WEB":
            return {"web_id": app_data.get("webId")}
        
        return {}

    def _create_app_response(self, app_data: dict, project_id: str) -> AppResponse:
        """Firebase 앱 응답 객체를 생성합니다."""
        firebase_app = App(app_data)
        
        app_resource = AppResource({
            "name": firebase_app.display_name,
            "data": firebase_app,
            "reference": ReferenceModel(firebase_app.reference()),
            "region_code": "global",
            "account": project_id,
        })
        
        return AppResponse({"resource": app_resource})

    def _create_app_response_with_logging(self, app_data: dict, project_id: str) -> AppResponse:
        """Firebase 앱 응답 객체를 v2.0 로깅과 함께 생성합니다."""
        try:
            # 기본 응답 생성
            response = self._create_app_response(app_data, project_id)
            
            # v2.0 로깅: SUCCESS 상태 기록
            if hasattr(self, 'update_state_counter'):
                self.update_state_counter("SUCCESS")
            
            return response
            
        except Exception as e:
            # v2.0 로깅: FAILURE 상태 기록
            if hasattr(self, 'update_state_counter'):
                self.update_state_counter("FAILURE")
            raise e
