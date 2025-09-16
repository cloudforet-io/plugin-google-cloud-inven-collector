import logging
import time

from spaceone.inventory.connector.firebase.firebase_v1beta1 import FirebaseConnector
from spaceone.inventory.libs.manager import GoogleCloudManager

from spaceone.inventory.libs.schema.base import (
    ReferenceModel,
    reset_state_counters,
    log_state_summary,
)

from spaceone.inventory.model.firebase.app.cloud_service import AppResource, AppResponse
from spaceone.inventory.model.firebase.app.cloud_service_type import CLOUD_SERVICE_TYPES
from spaceone.inventory.model.firebase.app.data import App
from spaceone.inventory.libs.schema.cloud_service import ErrorResourceResponse

_LOGGER = logging.getLogger(__name__)


class FirebaseManager(GoogleCloudManager):
    """
    Firebase App Manager (Firestore Database 방식과 동일한 구조)
    """

    connector_name = "FirebaseConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        """Firebase 앱 정보를 수집합니다."""
        _LOGGER.debug("** Firebase App START **")

        reset_state_counters()
        collected_cloud_services = []
        error_responses = []
        start_time = time.time()

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        try:
            # Firebase 커넥터 초기화
            firebase_connector: FirebaseConnector = self.locator.get_connector(
                self.connector_name, **params
            )

            # Firebase 앱 처리 (App Engine 방식과 동일)

            # Firebase 앱 목록 조회
            firebase_apps = firebase_connector.list_firebase_apps()
            _LOGGER.info(f"Found {len(firebase_apps)} Firebase apps to process")

            for app_data in firebase_apps:
                try:
                    # 실제 Google Cloud Monitoring 기반 데이터 수집
                    cloud_service_response = self._process_firebase_app_v2(
                        app_data, project_id, firebase_connector
                    )

                    if cloud_service_response:
                        collected_cloud_services.append(cloud_service_response)

                except Exception as e:
                    app_id = app_data.get("appId", "unknown")
                    _LOGGER.error(f"Failed to process Firebase app {app_id}: {e}")
                    error_response = ErrorResourceResponse(
                        {
                            "provider": "google_cloud",
                            "cloud_service_group": "Firebase",
                            "cloud_service_type": "App",
                            "resource_id": app_id,
                            "error": e,
                        }
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(f"Failed to collect Firebase apps: {e}")

        log_state_summary()
        _LOGGER.debug(f"** Firebase App END ** ({time.time() - start_time:.2f}s)")
        _LOGGER.info(f"Collected {len(collected_cloud_services)} Firebase Apps")

        return collected_cloud_services, error_responses

    def _process_firebase_app_v2(
        self, app_data: dict, project_id: str, firebase_connector: FirebaseConnector
    ) -> AppResponse:
        """
        개별 Firebase 앱을 처리합니다 (Firestore Database 방식과 동일).
        """
        app_id = app_data.get("appId", "")

        try:
            # 플랫폼 기반으로 적절한 service_id 결정 (Firebase App Check 실제 서비스들)
            platform = app_data.get("platform", "WEB")
            service_id_map = {
                "IOS": "oauth2.googleapis.com",  # Google Identity for iOS (공식 지원)
                "ANDROID": "firestore.googleapis.com",  # Cloud Firestore (공식 지원)
                "WEB": "firebasestorage.googleapis.com",  # Cloud Storage for Firebase (공식 지원)
            }
            service_id = service_id_map.get(platform, "firestore.googleapis.com")
            
            app_data.update(
                {
                    "name": app_id,
                    "project": project_id,
                    "full_name": app_data.get("displayName", app_id),
                    "google_cloud_monitoring": self.set_google_cloud_monitoring(
                        project_id,
                        "firebaseappcheck.googleapis.com/resource",
                        app_id,
                        [
                            {
                                "key": "resource.labels.resource_container",
                                "value": project_id,
                            },
                            {
                                "key": "resource.labels.location",
                                "value": "global",
                            },
                            {
                                "key": "resource.labels.service_id",
                                "value": service_id,
                            },
                            {
                                "key": "resource.labels.target_resource",
                                "value": app_id,
                            },
                        ],
                    ),
                    "google_cloud_logging": self.set_google_cloud_logging(
                        "Firebase", "App", project_id, app_id
                    ),
                }
            )

            # 4. App 모델 생성
            app_model = App(app_data, strict=False)

            # 5. CloudService 리소스 생성 (Filestore 방식과 동일)
            app_resource = AppResource(
                {
                    "name": app_data.get("displayName", app_id),
                    "account": project_id,
                    "data": app_model,
                    "reference": ReferenceModel(
                        {
                            "resource_id": app_id,
                            "external_link": f"https://console.firebase.google.com/project/{project_id}/settings/general/{app_id}",
                        }
                    ),
                    "region_code": "global",
                }
            )

            return AppResponse({"resource": app_resource})

        except Exception as e:
            _LOGGER.error(f"Failed to process Firebase app {app_id}: {e}")
            raise


