import logging

from spaceone.inventory.connector.datastore.database_v1 import (
    DatastoreDatabaseV1Connector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.datastore.database.cloud_service import (
    DatastoreDatabaseResource,
    DatastoreDatabaseResponse,
)
from spaceone.inventory.model.datastore.database.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.datastore.database.data import DatastoreDatabaseData

_LOGGER = logging.getLogger(__name__)


class DatastoreDatabaseManager(GoogleCloudManager):
    """
    Google Cloud Datastore Database Manager

    Datastore Database 리소스를 수집하고 처리하는 매니저 클래스
    - Database 목록 수집 (DATASTORE_MODE만)
    - Database 상세 정보 처리
    - 리소스 응답 생성
    """

    connector_name = "DatastoreDatabaseV1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    database_conn = None
    _cached_databases = None  # 데이터베이스 목록 캐시

    def collect_cloud_service(self, params):
        """
        Datastore Database 리소스를 수집합니다.

        Args:
            params (dict): 수집 파라미터
                - secret_data: 인증 정보
                - options: 옵션 설정

        Returns:
            Tuple[List[DatastoreDatabaseResponse], List[ErrorResourceResponse]]:
                성공한 리소스 응답 리스트와 에러 응답 리스트
        """
        _LOGGER.debug("** Datastore Database START **")

        resource_responses = []
        error_responses = []

        try:
            # Connector 초기화
            self.database_conn: DatastoreDatabaseV1Connector = (
                self.locator.get_connector(self.connector_name, **params)
            )

            # 모든 database 조회 및 필터링
            databases = self._list_datastore_databases()

            # 각 database에 대해 리소스 생성
            for database_data in databases:
                try:
                    resource_response = self._make_database_response(
                        database_data, params
                    )
                    resource_responses.append(resource_response)
                except Exception as e:
                    database_name = database_data.get("name", "unknown")
                    _LOGGER.error(f"Failed to process database {database_name}: {e}")
                    error_response = self.generate_error_response(
                        e, "Datastore", "Database", database_name
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(f"Failed to collect Datastore databases: {e}")
            error_response = self.generate_error_response(e, "Datastore", "Database")
            error_responses.append(error_response)

        _LOGGER.debug("** Datastore Database END **")
        return resource_responses, error_responses

    def _get_cached_databases(self):
        """
        캐시된 데이터베이스 목록을 반환하거나, 없으면 새로 조회합니다.

        Returns:
            List[dict]: DATASTORE_MODE 데이터베이스 목록
        """
        if self._cached_databases is None:
            self._cached_databases = self.database_conn.list_databases()
            _LOGGER.info(
                f"Cached {len(self._cached_databases)} DATASTORE_MODE databases"
            )
        return self._cached_databases

    def _list_datastore_databases(self):
        """
        DATASTORE_MODE 타입의 데이터베이스만 조회합니다.

        Returns:
            List[dict]: DATASTORE_MODE 데이터베이스 정보 목록
        """
        databases = []

        try:
            # 캐시된 데이터베이스 목록 사용
            datastore_databases = self._get_cached_databases()

            # 각 데이터베이스에 대해 추가 정보 수집
            for database in datastore_databases:
                try:
                    database_data = self._process_database_data(database)
                    if database_data:
                        databases.append(database_data)
                except Exception as e:
                    database_name = database.get("name", "unknown")
                    _LOGGER.error(f"Error processing database {database_name}: {e}")
                    continue

            _LOGGER.info(f"Found {len(databases)} DATASTORE_MODE databases")

        except Exception as e:
            _LOGGER.error(f"Error listing datastore databases: {e}")
            raise e

        return databases

    def _process_database_data(self, database):
        """
        Database 데이터를 처리하고 필요한 정보를 추가합니다.

        Args:
            database (dict): 원본 database 데이터

        Returns:
            dict: 처리된 database 데이터
        """
        try:
            # 기본 정보 추출
            name = database.get("name", "")
            uid = database.get("uid", "")
            location_id = database.get("locationId", "")
            database_type = database.get("type", "")
            concurrency_mode = database.get("concurrencyMode", "")
            create_time = database.get("createTime", "")
            update_time = database.get("updateTime", "")

            # Database ID 추출 (name에서 마지막 부분)
            database_id = (
                name.split("/")[-1] if name else "(default)"
            )  # 기본 데이터베이스는 (default)

            # 처리된 데이터 구성
            processed_data = {
                "name": name,
                "uid": uid,
                "database_id": database_id,
                "location_id": location_id,
                "type": database_type,
                "concurrency_mode": concurrency_mode,
                "create_time": create_time,
                "update_time": update_time,
                "project_id": self.database_conn.project_id,
                "display_name": f"Database ({database_id})"
                if database_id != "(default)"
                else "Default Database",
                # 원본 데이터도 포함
                "raw_data": database,
            }

            return processed_data

        except Exception as e:
            _LOGGER.error(f"Error processing database data: {e}")
            return None

    def _make_database_response(self, database_data, params):
        """
        Database 데이터를 기반으로 리소스 응답을 생성합니다.

        Args:
            database_data (dict): database 데이터
            params (dict): 수집 파라미터

        Returns:
            DatastoreDatabaseResponse: database 리소스 응답
        """
        project_id = database_data["project_id"]

        # 리소스 데이터 생성
        database_data_obj = DatastoreDatabaseData(database_data, strict=False)

        # 리소스 생성
        resource = DatastoreDatabaseResource(
            {
                "name": database_data["display_name"],
                "account": project_id,
                "data": database_data_obj,
                "region_code": database_data.get("location_id", "global"),
                "reference": ReferenceModel(database_data_obj.reference()),
            }
        )

        # 응답 생성
        return DatastoreDatabaseResponse({"resource": resource})

    def get_datastore_database_ids(self, params):
        """
        DATASTORE_MODE 데이터베이스의 ID 목록을 반환합니다.
        다른 매니저에서 데이터베이스 ID 목록이 필요할 때 사용합니다.

        Args:
            params (dict): 수집 파라미터

        Returns:
            List[str]: 데이터베이스 ID 목록
        """
        try:
            # Connector 초기화 (아직 초기화되지 않은 경우)
            if self.database_conn is None:
                self.database_conn: DatastoreDatabaseV1Connector = (
                    self.locator.get_connector(self.connector_name, **params)
                )

            # 캐시된 데이터베이스 목록 사용
            datastore_databases = self._get_cached_databases()

            # 데이터베이스 ID 목록 추출
            database_ids = []
            for database in datastore_databases:
                name = database.get("name", "")
                database_id = (
                    name.split("/")[-1] if name else "(default)"
                )  # default 처리 복원
                database_ids.append(database_id)

            # 빈 목록인 경우 기본 데이터베이스 추가
            if not database_ids:
                database_ids.append("(default)")  # default를 (default)로 처리

            _LOGGER.info(
                f"Found {len(database_ids)} DATASTORE_MODE database IDs: {database_ids}"
            )
            return database_ids

        except Exception as e:
            _LOGGER.error(f"Error getting datastore database IDs: {e}")
            return ["(default)"]  # 에러 발생 시 기본 데이터베이스 반환 ((default))
