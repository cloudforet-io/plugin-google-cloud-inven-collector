import logging

import google.auth.transport.requests
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

        # 기존 credentials에 스코프 추가
        if hasattr(self.credentials, "with_scopes"):
            self.credentials = self.credentials.with_scopes(firebase_scopes)
            # Firebase API 클라이언트 재생성
            self.client = googleapiclient.discovery.build(
                self.google_client_service, self.version, credentials=self.credentials
            )

    def list_available_projects(self, **query):
        """
        Firebase Management API의 availableProjects 엔드포인트를 호출하여
        사용 가능한 Firebase 프로젝트 목록을 반환합니다.

        Args:
            **query: 추가 쿼리 파라미터 (pageToken, pageSize, showDeleted 등)

        Returns:
            list: 사용 가능한 Firebase 프로젝트 목록
        """
        projects = []
        seen_project_ids = set()

        try:
            # 3. 직접 HTTP 요청으로 다양한 엔드포인트 시도
            import requests

            # Access token 가져오기
            self.credentials.refresh(google.auth.transport.requests.Request())
            access_token = self.credentials.token

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            # Firebase API 엔드포인트 시도
            endpoints = [
                "https://firebase.googleapis.com/v1beta1/projects",
            ]

            for url in endpoints:
                try:
                    response = requests.get(url, headers=headers)

                    if response.status_code == 200:
                        data = response.json()
                        if url.endswith("projects"):
                            results = data.get("results", [])
                            if results:
                                for project in results:
                                    project_id = project.get("projectId")
                                    if (
                                        project_id
                                        and project_id not in seen_project_ids
                                    ):
                                        projects.append(project)
                                        seen_project_ids.add(project_id)
                        else:
                            # 단일 프로젝트 응답
                            if data.get("projectId"):
                                project_id = data.get("projectId")
                                if project_id not in seen_project_ids:
                                    projects.append(data)
                                    seen_project_ids.add(project_id)
                    elif response.status_code == 403:
                        _LOGGER.warning(f"Permission denied for {url}")
                    elif response.status_code == 404:
                        _LOGGER.warning(f"Not found: {url}")
                    else:
                        _LOGGER.warning(
                            f"HTTP {response.status_code} for {url}: {response.text}"
                        )

                except Exception as direct_error:
                    _LOGGER.warning(f"Direct API call to {url} failed: {direct_error}")

            # 4. Resource Manager API로 GCP 프로젝트 확인
            try:
                import googleapiclient.discovery

                resource_manager = googleapiclient.discovery.build(
                    "cloudresourcemanager", "v1", credentials=self.credentials
                )

                projects_response = resource_manager.projects().list().execute()

                gcp_projects = projects_response.get("projects", [])
                for gcp_project in gcp_projects:
                    if gcp_project.get("projectId") == self.project_id:
                        # GCP 프로젝트를 Firebase 형식으로 변환
                        project_id = gcp_project.get("projectId")
                        if project_id not in seen_project_ids:
                            firebase_project = {
                                "projectId": project_id,
                                "displayName": gcp_project.get("name"),
                                "projectNumber": gcp_project.get("projectNumber"),
                                "state": gcp_project.get("lifecycleState", "ACTIVE"),
                                "name": f"projects/{project_id}",
                            }
                            projects.append(firebase_project)
                            seen_project_ids.add(project_id)
                            break

            except Exception as rm_error:
                _LOGGER.warning(f"Resource Manager API failed: {rm_error}")

        except Exception as e:
            _LOGGER.error(f"All Firebase API attempts failed: {e}")
            _LOGGER.error(f"Error type: {type(e)}")
            _LOGGER.error(f"Error details: {str(e)}")
            raise e

        return projects

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
