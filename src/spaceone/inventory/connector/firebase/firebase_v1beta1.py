import logging

import googleapiclient

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["FirebaseV1Beta1Connector"]
_LOGGER = logging.getLogger(__name__)


class FirebaseV1Beta1Connector(GoogleCloudConnector):
    google_client_service = "firebase"
    version = "v1beta1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Firebase Management API에 필요한 스코프 추가
        firebase_scopes = [
            "https://www.googleapis.com/auth/firebase",
            "https://www.googleapis.com/auth/firebase.readonly",
            "https://www.googleapis.com/auth/cloud-platform",
            "https://www.googleapis.com/auth/cloud-platform.read-only",
        ]

        # 기존 credentials에 스코프 추가 (credentials 속성이 있는 경우에만)
        if hasattr(self, "credentials") and hasattr(self.credentials, "with_scopes"):
            self.credentials = self.credentials.with_scopes(firebase_scopes)
            # Firebase API 클라이언트 재생성
            self.client = googleapiclient.discovery.build(
                self.google_client_service, self.version, credentials=self.credentials
            )

    def list_firebase_apps(self, **query):
        """
        특정 프로젝트의 Firebase 앱들을 조회합니다.
        Firebase Management API의 searchApps 엔드포인트를 사용합니다.

        Args:
            **query: 추가 쿼리 파라미터

        Returns:
            list: Firebase 앱 목록
        """
        try:
            # 프로젝트 기준으로 Firebase 앱들 조회
            parent = f"projects/{self.project_id}"
            query.update({"parent": parent})

            apps = []
            request = self.client.projects().searchApps(**query)

            while request is not None:
                response = request.execute()
                for app in response.get("apps", []):
                    apps.append(app)
                request = self.client.projects().searchApps_next(
                    previous_request=request, previous_response=response
                )

            return apps

        except Exception as e:
            _LOGGER.error(
                f"Failed to list Firebase apps for project {self.project_id}: {e}"
            )
            raise e

    def get_firebase_project_info(self, **query):
        """
        Firebase 앱 목록을 조회하고 서비스 사용 여부를 확인합니다.

        Args:
            **query: 추가 쿼리 파라미터

        Returns:
            dict: Firebase 앱 목록과 서비스 사용 여부
        """
        try:
            # Firebase 앱들 조회
            firebase_apps = self.list_firebase_apps()

            return {
                "firebaseApps": firebase_apps,
                "hasFirebaseServices": len(firebase_apps) > 0,
            }

        except Exception as e:
            _LOGGER.error(
                f"Failed to get Firebase apps for {self.project_id}: {e}"
            )
            raise e

    def get_app_details(self, app_name):
        """
        특정 Firebase 앱의 상세 정보를 가져옵니다.

        Args:
            app_name (str): Firebase 앱 이름 (projects/{project}/iosApps/{app-id} 형식)

        Returns:
            dict: 앱 상세 정보
        """
        try:
            # 플랫폼에 따라 다른 API 엔드포인트 사용
            if "/iosApps/" in app_name:
                response = self.client.projects().iosApps().get(name=app_name).execute()
            elif "/androidApps/" in app_name:
                response = (
                    self.client.projects().androidApps().get(name=app_name).execute()
                )
            elif "/webApps/" in app_name:
                response = self.client.projects().webApps().get(name=app_name).execute()
            else:
                # 기본적으로 searchApps로 얻은 정보 반환
                return {}

            return response
        except Exception as e:
            _LOGGER.warning(f"Failed to get app details for {app_name}: {e}")
            return {}

    def get_project(self, project_id):
        """
        특정 Firebase 프로젝트의 상세 정보를 가져옵니다.

        Args:
            project_id (str): Firebase 프로젝트 ID

        Returns:
            dict: 프로젝트 상세 정보
        """
        try:
            response = (
                self.client.projects().get(name=f"projects/{project_id}").execute()
            )
            return response
        except Exception as e:
            _LOGGER.error(f"Failed to get Firebase project {project_id}: {e}")
            raise e
