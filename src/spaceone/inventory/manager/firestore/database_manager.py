import logging
import time
from typing import List, Tuple

from spaceone.inventory.connector.firestore.database_v1 import (
    FirestoreDatabaseConnector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.firestore.database.cloud_service import (
    DatabaseResource,
    DatabaseResponse,
)
from spaceone.inventory.model.firestore.database.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.firestore.database.data import Database

_LOGGER = logging.getLogger(__name__)


class FirestoreDatabaseManager(GoogleCloudManager):
    """
    Google Cloud Firestore Database Manager

    Firestore Database 리소스를 수집하고 처리하는 매니저 클래스
    - Database 목록 수집 (FIRESTORE_NATIVE 모드)
    - Database 상세 정보 처리
    - 리소스 응답 생성
    """

    connector_name = "FirestoreDatabaseConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params) -> Tuple[List[DatabaseResponse], List]:
        """
        Firestore Database 리소스를 수집합니다.

        Args:
            params (dict): 수집 파라미터
                - secret_data: 인증 정보
                - options: 옵션 설정

        Returns:
            Tuple[List[DatabaseResponse], List[ErrorResourceResponse]]:
                성공한 리소스 응답 리스트와 에러 응답 리스트
        """
        _LOGGER.debug("** Firestore Database START **")
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
            firestore_conn: FirestoreDatabaseConnector = self.locator.get_connector(
                self.connector_name, **params
            )

            # Get databases (FIRESTORE_NATIVE)
            databases = firestore_conn.list_databases()
            _LOGGER.info(f"Found {len(databases)} Firestore databases")

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
                                "Firestore", "Database", project_id, database_id
                            ),
                        }
                    )

                    database_data = Database(database, strict=False)

                    ##################################
                    # 3. Make Return Resource
                    ##################################
                    database_resource = DatabaseResource(
                        {
                            "name": database_id,
                            "account": project_id,
                            "region_code": region_code,
                            "data": database_data,
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
                        DatabaseResponse({"resource": database_resource})
                    )

                except Exception as e:
                    _LOGGER.error(f"Failed to process database {database_id}: {e}")
                    error_response = self.generate_resource_error_response(
                        e, "Firestore", "Database", database_id
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(f"Failed to collect Firestore databases: {e}")
            error_response = self.generate_resource_error_response(
                e, "Firestore", "Database"
            )
            error_responses.append(error_response)

        # 수집 완료 로깅
        _LOGGER.debug(
            f"** Firestore Database Finished {time.time() - start_time} Seconds **"
        )

        return collected_cloud_services, error_responses
