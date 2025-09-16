import logging
import time

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
        start_time = time.time()

        collected_cloud_services = []
        error_responses = []
        database_name = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        try:
            ##################################
            # 0. Gather All Related Resources
            ##################################
            database_conn: DatastoreDatabaseV1Connector = self.locator.get_connector(
                self.connector_name, **params
            )

            # Get databases (DATASTORE_MODE)
            databases = database_conn.list_databases()
            _LOGGER.info(f"Found {len(databases)} DATASTORE_MODE databases")

            for database in databases:
                try:
                    ##################################
                    # 1. Set Basic Information
                    ##################################
                    database_name = database.get("name", "")
                    database_id = (
                        database_name.split("/")[-1]
                        if "/" in database_name
                        else database_name
                    )
                    region_code = database.get("locationId", "global")

                    ##################################
                    # 2. Make Base Data
                    ##################################
                    database.update(
                        {
                            "name": database_id,
                            "project": project_id,
                            "full_name": database_name,
                            "google_cloud_monitoring": self.set_google_cloud_monitoring(
                                project_id,
                                "firestore.googleapis.com",
                                database_id,
                                [
                                    {
                                        "key": "resource.labels.database_id",
                                        "value": database_id,
                                    }
                                ],
                            ),
                            "google_cloud_logging": self.set_google_cloud_logging(
                                "Datastore", "Database", project_id, database_id
                            ),
                        }
                    )

                    database_data = DatastoreDatabaseData(database, strict=False)

                    ##################################
                    # 3. Make Return Resource
                    ##################################
                    database_resource = DatastoreDatabaseResource(
                        {
                            "name": database_id,
                            "account": project_id,
                            "data": database_data,
                            "region_code": region_code,
                            "reference": ReferenceModel(database_data.reference()),
                        }
                    )

                    ##################################
                    # 4. Make Collected Region Code
                    ##################################
                    self.set_region_code(region_code)

                    ##################################
                    # 5. Make Resource Response Object
                    ##################################
                    collected_cloud_services.append(
                        DatastoreDatabaseResponse({"resource": database_resource})
                    )

                except Exception as e:
                    _LOGGER.error(f"Failed to process database {database_name}: {e}")
                    error_response = self.generate_resource_error_response(
                        e, "Datastore", "Database", database_name
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(f"Failed to collect Datastore databases: {e}")
            error_response = self.generate_resource_error_response(
                e, "Datastore", "Database"
            )
            error_responses.append(error_response)

        # 수집 완료 로깅
        _LOGGER.debug(
            f"** Datastore Database Finished {time.time() - start_time} Seconds **"
        )

        return collected_cloud_services, error_responses
