import logging

import googleapiclient

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["FirebaseProjectConnector"]
_LOGGER = logging.getLogger(__name__)


class FirebaseProjectConnector(GoogleCloudConnector):
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
        특정 프로젝트의 Firebase 프로젝트 정보를 조회합니다.
        프로젝트 기준으로 Firebase 서비스 사용 여부를 확인합니다.

        Args:
            **query: 추가 쿼리 파라미터

        Returns:
            dict: Firebase 프로젝트 정보
        """
        try:
            # 1. Resource Manager로 프로젝트 기본 정보 확인
            import googleapiclient.discovery

            resource_manager = googleapiclient.discovery.build(
                "cloudresourcemanager", "v1", credentials=self.credentials
            )

            project_info = (
                resource_manager.projects().get(projectId=self.project_id).execute()
            )

            # 2. Firebase 앱들 조회
            firebase_apps = self.list_firebase_apps()

            # 3. Firebase 프로젝트 정보 구성
            firebase_project = {
                "projectId": self.project_id,
                "displayName": project_info.get("name", ""),
                "projectNumber": project_info.get("projectNumber", ""),
                "state": project_info.get("lifecycleState", "ACTIVE"),
                "name": f"projects/{self.project_id}",
                "firebaseApps": firebase_apps,
                "appCount": len(firebase_apps),
                "hasFirebaseServices": str(len(firebase_apps) > 0),
            }

            # 4. 플랫폼별 앱 통계 추가
            platform_stats = {"IOS": 0, "ANDROID": 0, "WEB": 0}
            for app in firebase_apps:
                platform = app.get("platform", "PLATFORM_UNSPECIFIED")
                if platform in platform_stats:
                    platform_stats[platform] += 1

            firebase_project["platformStats"] = platform_stats

            return firebase_project

        except Exception as e:
            _LOGGER.error(
                f"Failed to get Firebase project info for {self.project_id}: {e}"
            )
            raise e

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
