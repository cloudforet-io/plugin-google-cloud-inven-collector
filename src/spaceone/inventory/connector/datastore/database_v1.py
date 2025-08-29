import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

_LOGGER = logging.getLogger(__name__)


class DatastoreDatabaseV1Connector(GoogleCloudConnector):
    """
    Google Cloud Datastore Database Connector

    Datastore Database 관련 API 호출을 담당하는 클래스
    - Database 목록 조회 (DATASTORE_MODE만 필터링)

    API 버전: v1
    참고: https://cloud.google.com/firestore/docs/reference/rest/v1/projects.databases
    """

    google_client_service = "firestore"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_databases(self):
        """
        프로젝트의 DATASTORE_MODE 타입 데이터베이스만 조회합니다.

        API 응답 구조:
        {
          "databases": [
            {
              "name": string,
              "uid": string,
              "createTime": string,
              "updateTime": string,
              "locationId": string,
              "type": enum (Type),
              "concurrencyMode": enum (ConcurrencyMode),
              "versionRetentionPeriod": string,
              "earliestVersionTime": string,
              "pointInTimeRecoveryEnablement": enum (PointInTimeRecoveryEnablement),
              "appEngineIntegrationMode": enum (AppEngineIntegrationMode),
              "keyPrefix": string,
              "deleteProtectionState": enum (DeleteProtectionState),
              "cmekConfig": {
                object (CmekConfig)
              },
              "etag": string
            }
          ]
        }

        Returns:
            list: DATASTORE_MODE 타입의 데이터베이스 목록
        """
        try:
            parent = f"projects/{self.project_id}"
            request = self.client.projects().databases().list(parent=parent)

            response = request.execute()
            _LOGGER.debug(f"Database list response: {response}")

            # databases 필드에서 데이터베이스 목록 추출, 없으면 빈 리스트 반환
            all_databases = response.get("databases", [])
            _LOGGER.info(f"Retrieved {len(all_databases)} total databases")

            # DATASTORE_MODE 타입만 필터링
            datastore_databases = list(
                filter(lambda db: db.get("type") == "DATASTORE_MODE", all_databases)
            )

            _LOGGER.info(
                f"Filtered {len(datastore_databases)} DATASTORE_MODE databases"
            )

            return datastore_databases

        except Exception as e:
            _LOGGER.error(f"Error listing databases: {e}")
            raise e
