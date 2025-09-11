import logging
import time
from typing import List, Tuple

from spaceone.inventory.connector.firestore.database_v1 import (
    FirestoreDatabaseConnector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.firestore.backup.cloud_service import (
    BackupResource,
    BackupResponse,
)
from spaceone.inventory.model.firestore.backup.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.firestore.backup.data import Backup

_LOGGER = logging.getLogger(__name__)


class FirestoreBackupManager(GoogleCloudManager):
    """
    Google Cloud Firestore Backup Manager

    Firestore Backup 리소스를 수집하고 처리하는 매니저 클래스
    - Backup 목록 수집 (모든 위치에서)
    - Backup 상세 정보 처리
    - 리소스 응답 생성
    """

    connector_name = "FirestoreDatabaseConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params) -> Tuple[List[BackupResponse], List]:
        """
        Firestore Backup 리소스를 수집합니다.

        Args:
            params (dict): 수집 파라미터
                - secret_data: 인증 정보
                - options: 옵션 설정

        Returns:
            Tuple[List[BackupResponse], List[ErrorResourceResponse]]:
                성공한 리소스 응답 리스트와 에러 응답 리스트
        """
        _LOGGER.debug("** Firestore Backup START **")
        start_time = time.time()

        collected_cloud_services = []
        error_responses = []

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        try:
            ##################################
            # 0. Gather All Related Resources
            ##################################
            firestore_conn: FirestoreDatabaseConnector = self.locator.get_connector(
                self.connector_name, **params
            )

            ##################################
            # 1. Set Basic Information & 2. Make Base Data
            ##################################
            backups = firestore_conn.list_all_backups()
            _LOGGER.info(
                f"Found {len(backups)} backups across all locations for project {project_id}"
            )

            for backup in backups:
                try:
                    backup_name = backup.get("name", "")
                    backup_database = backup.get("database", "")
                    backup_database_id = (
                        backup_database.split("/")[-1]
                        if "/" in backup_database
                        else backup_database
                    )
                    backup_id = (
                        backup_name.split("/")[-1]
                        if "/" in backup_name
                        else backup_name
                    )

                    # 백업 이름에서 위치 ID 추출
                    location_id = self._extract_location_from_backup_name(backup_name)

                    backup.update(
                        {
                            "name": backup_id,
                            "full_name": backup_name,
                            "database_id": backup_database_id,
                            "project": project_id,
                        }
                    )
                    backup_data = Backup(backup, strict=False)

                    ##################################
                    # 3. Make Return Resource
                    ##################################
                    backup_resource = BackupResource(
                        {
                            "name": backup_id,
                            "account": project_id,
                            "region_code": location_id,
                            "data": backup_data,
                            "reference": ReferenceModel(backup_data.reference()),
                        }
                    )

                    ##################################
                    # 4. Make Collected Region Code
                    ##################################
                    self.set_region_code(location_id)

                    ##################################
                    # 5. Make Resource Response Object
                    ##################################
                    collected_cloud_services.append(
                        BackupResponse({"resource": backup_resource})
                    )

                except Exception as backup_error:
                    _LOGGER.warning(
                        f"Failed to process backup {backup.get('name', 'unknown')}: {backup_error}"
                    )
                    continue

        except Exception as e:
            _LOGGER.error(f"Failed to collect Firestore backups: {e}")
            error_response = self.generate_resource_error_response(
                e, "Firestore", "Backup"
            )
            error_responses.append(error_response)

        # 수집 완료 로깅
        _LOGGER.debug(
            f"** Firestore Backup Finished {time.time() - start_time} Seconds **"
        )

        return collected_cloud_services, error_responses

    @staticmethod
    def _extract_location_from_backup_name(backup_name: str) -> str:
        """백업 이름에서 위치 ID 추출

        Args:
            backup_name: projects/{project}/locations/{location}/backups/{backup} 형식

        Returns:
            str: 위치 ID (예: us-central1)
        """
        if "/locations/" in backup_name and "/backups/" in backup_name:
            # projects/{project}/locations/{location}/backups/{backup} 형식에서 location 추출
            parts = backup_name.split("/locations/")[1].split("/backups/")[0]
            return parts
        return "global"
