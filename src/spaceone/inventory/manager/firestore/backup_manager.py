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
    connector_name = "FirestoreDatabaseConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params) -> Tuple[List[BackupResponse], List]:
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

        _LOGGER.debug(
            f"** Firestore Backup Finished {time.time() - start_time} Seconds **"
        )

        return collected_cloud_services, error_responses

    @staticmethod
    def _extract_location_from_backup_name(backup_name: str) -> str:
        """Extract location ID from backup name"""
        if "/locations/" in backup_name and "/backups/" in backup_name:
            # projects/{project}/locations/{location}/backups/{backup} 형식에서 location 추출
            parts = backup_name.split("/locations/")[1].split("/backups/")[0]
            return parts
        return "global"
