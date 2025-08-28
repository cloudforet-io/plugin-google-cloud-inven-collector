import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

_LOGGER = logging.getLogger(__name__)


class DatastoreIndexV1Connector(GoogleCloudConnector):
    """
    Google Cloud Datastore Index Connector

    Datastore Index 관련 API 호출을 담당하는 클래스
    - Index 목록 조회 (프로젝트 레벨)

    API 버전: v1
    참고: https://cloud.google.com/datastore/docs/reference/admin/rest/v1/projects.indexes/list
    """

    google_client_service = "datastore"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_indexes(self):
        """
        프로젝트의 모든 Datastore Index를 조회합니다.

        API 응답 구조:
        {
          "indexes": [
            {
              "indexId": string,
              "kind": string,
              "ancestor": enum (Ancestor),
              "properties": [
                {
                  "name": string,
                  "direction": enum (Direction)
                }
              ],
              "state": enum (State)
            }
          ]
        }

        Returns:
            list: 프로젝트의 모든 index 목록
        """
        try:
            request = self.client.projects().indexes().list(projectId=self.project_id)

            response = request.execute()
            _LOGGER.debug(f"Index list response: {response}")

            # indexes 필드에서 index 목록 추출, 없으면 빈 리스트 반환
            indexes = response.get("indexes", [])
            _LOGGER.info(f"Retrieved {len(indexes)} total indexes")

            return indexes

        except Exception as e:
            _LOGGER.error(f"Error listing indexes: {e}")
            raise e
