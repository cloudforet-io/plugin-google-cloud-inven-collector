import logging
from typing import Dict, List, Optional

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.google_cloud_monitoring import (
    GoogleCloudMonitoringModel,
    GoogleCloudMonitoringFilter,
)
from spaceone.inventory.libs.schema.google_cloud_logging import (
    GoogleCloudLoggingModel,
    GoogleCloudLoggingFilterLabel,
)

_LOGGER = logging.getLogger(__name__)


class FirebaseMonitoringManager(GoogleCloudManager):
    """
    Firebase Google Cloud Monitoring 전용 매니저
    Compute Engine과 동일한 방식으로 Google Cloud Monitoring API 기반 구현
    
    참조 문서: https://cloud.google.com/monitoring/api/metrics_gcp_d_h?hl=ko#gcp-firebaseappcheck
    """

    def create_firebase_monitoring(self, app_data: dict, project_id: str) -> dict:
        """
        Firebase 앱의 Google Cloud Monitoring 설정을 생성합니다.
        
        Args:
            app_data: Firebase 앱 데이터
            project_id: Firebase 프로젝트 ID
            
        Returns:
            dict: Google Cloud Monitoring 설정
        """
        app_id = app_data.get("appId", "")
        platform = app_data.get("platform", "")
        
        if not app_id or not project_id:
            return {}

        try:
            # Firebase 전용 Google Cloud Monitoring 필터 생성
            monitoring_filters = self._create_firebase_monitoring_filters(
                project_id, app_id, platform
            )
            
            return GoogleCloudMonitoringModel({
                "name": f"projects/{project_id}",
                "resource_id": app_id,
                "filters": monitoring_filters
            })
            
        except Exception as e:
            _LOGGER.error(f"Failed to create Firebase monitoring for {app_id}: {e}")
            return {}

    def create_firebase_logging(self, app_data: dict, project_id: str) -> dict:
        """
        Firebase 앱의 Google Cloud Logging 설정을 생성합니다.
        
        Args:
            app_data: Firebase 앱 데이터
            project_id: Firebase 프로젝트 ID
            
        Returns:
            dict: Google Cloud Logging 설정
        """
        app_id = app_data.get("appId", "")
        platform = app_data.get("platform", "")
        
        if not app_id or not project_id:
            return {}

        try:
            # Firebase 전용 Google Cloud Logging 필터 생성
            logging_filters = self._create_firebase_logging_filters(
                project_id, app_id, platform
            )
            
            return GoogleCloudLoggingModel({
                "name": f"projects/{project_id}",
                "resource_id": app_id,
                "filters": logging_filters
            })
            
        except Exception as e:
            _LOGGER.error(f"Failed to create Firebase logging for {app_id}: {e}")
            return {}

    def _create_firebase_monitoring_filters(
        self, project_id: str, app_id: str, platform: str
    ) -> List[GoogleCloudMonitoringFilter]:
        """
        Firebase Google Cloud Monitoring 필터를 생성합니다. (최상위 도메인 사용)
        
        Args:
            project_id: Firebase 프로젝트 ID
            app_id: Firebase 앱 ID
            platform: 플랫폼 (ANDROID, IOS, WEB)
            
        Returns:
            List[GoogleCloudMonitoringFilter]: 모니터링 필터 목록 (간소화)
        """
        filters = []

        # 1. Firebase 전체 메트릭 (최상위 도메인)
        firebase_filter = GoogleCloudMonitoringFilter({
            "metric_type": "firebase.googleapis.com",
            "labels": [
                {"key": "resource.labels.project_id", "value": project_id},
                {"key": "resource.labels.app_id", "value": app_id}
            ]
        })
        filters.append(firebase_filter)

        # 2. FCM 전체 메트릭 (최상위 도메인)
        fcm_filter = GoogleCloudMonitoringFilter({
            "metric_type": "fcm.googleapis.com",
            "labels": [
                {"key": "resource.labels.project_id", "value": project_id}
            ]
        })
        filters.append(fcm_filter)

        return filters

    def _create_firebase_logging_filters(
        self, project_id: str, app_id: str, platform: str
    ) -> List[dict]:
        """
        Firebase Google Cloud Logging 필터를 생성합니다.
        
        Args:
            project_id: Firebase 프로젝트 ID
            app_id: Firebase 앱 ID
            platform: 플랫폼 (ANDROID, IOS, WEB)
            
        Returns:
            List[dict]: 로깅 필터 목록
        """
        filters = []

        # 플랫폼별 리소스 타입 매핑
        platform_resource_map = {
            "ANDROID": "android_app",
            "IOS": "ios_app", 
            "WEB": "web_app"
        }
        
        resource_type = platform_resource_map.get(platform, "firebase_app")

        # 1. Firebase 앱별 로그
        app_filter = {
            "resource_type": resource_type,
            "labels": [
                {"key": "resource.labels.project_id", "value": project_id},
                {"key": "resource.labels.app_id", "value": app_id}
            ]
        }
        filters.append(app_filter)

        # 2. Firebase Auth 로그 (프로젝트 레벨)
        auth_filter = {
            "resource_type": "firebase_auth",
            "labels": [
                {"key": "resource.labels.project_id", "value": project_id}
            ]
        }
        filters.append(auth_filter)

        # 3. Firestore 로그 (프로젝트 레벨)
        firestore_filter = {
            "resource_type": "firestore_instance",
            "labels": [
                {"key": "resource.labels.project_id", "value": project_id},
                {"key": "resource.labels.database_id", "value": "(default)"}
            ]
        }
        filters.append(firestore_filter)

        # 4. Firebase Functions 로그 (프로젝트 레벨)
        functions_filter = {
            "resource_type": "cloud_function",
            "labels": [
                {"key": "resource.labels.project_id", "value": project_id}
            ]
        }
        filters.append(functions_filter)

        return filters

    def get_firebase_metric_types(self) -> Dict[str, List[str]]:
        """
        Firebase에서 사용 가능한 Google Cloud Monitoring 메트릭 타입들을 반환합니다.
        
        Returns:
            Dict[str, List[str]]: 카테고리별 메트릭 타입 목록
        """
        return {
            "analytics": [
                "firebase.googleapis.com/analytics/user_engagement",
                "firebase.googleapis.com/analytics/event_count",
                "firebase.googleapis.com/analytics/session_count",
                "firebase.googleapis.com/analytics/screen_view",
            ],
            "performance": [
                "firebase.googleapis.com/performance/app_start_time",
                "firebase.googleapis.com/performance/screen_rendering_time", 
                "firebase.googleapis.com/performance/network_request_duration",
                "firebase.googleapis.com/performance/trace_duration",
            ],
            "auth": [
                "firebaseauth.googleapis.com/auth/user_count",
                "firebaseauth.googleapis.com/auth/sign_in_count",
            ],
            "messaging": [
                "fcm.googleapis.com/api/request_count",
                "fcm.googleapis.com/message/send_count",
            ],
            "database": [
                "firebase.googleapis.com/database/io/database_load",
                "firebase.googleapis.com/database/io/persisted_bytes",
                "firebase.googleapis.com/database/network/active_connections",
            ],
            "hosting": [
                "firebase.googleapis.com/hosting/bytes_sent",
                "firebase.googleapis.com/hosting/requests",
            ]
        }
