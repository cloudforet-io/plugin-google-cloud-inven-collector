import logging
import time
from typing import List, Tuple

from spaceone.inventory.connector.filestore.backup_v1 import (
    FilestoreBackupConnector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.filestore.backup.cloud_service import (
    FilestoreBackupResource,
    FilestoreBackupResponse,
)
from spaceone.inventory.model.filestore.backup.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.filestore.backup.data import FilestoreBackupData

_LOGGER = logging.getLogger(__name__)


class FilestoreBackupManager(GoogleCloudManager):
    connector_name = "FilestoreBackupConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    backup_conn = None

    def collect_cloud_service(
        self, params
    ) -> Tuple[List[FilestoreBackupResponse], List]:
        _LOGGER.debug("** Filestore Backup START **")
        start_time = time.time()

        collected_cloud_services = []
        error_responses = []
        backup_id = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        try:
            ##################################
            # 0. Gather All Related Resources
            ##################################
            self.backup_conn: FilestoreBackupConnector = self.locator.get_connector(
                self.connector_name, **params
            )

            # Get Filestore backups (v1 API)
            filestore_backups = self.backup_conn.list_backups()

            for filestore_backup in filestore_backups:
                try:
                    ##################################
                    # 1. Set Basic Information
                    ##################################
                    backup_name = filestore_backup.get("name", "")
                    backup_id = (
                        backup_name.split("/")[-1]
                        if "/" in backup_name
                        else backup_name
                    )
                    location = filestore_backup.get("location", "")

                    ##################################
                    # 2. Make Base Data
                    ##################################
                    labels = self.convert_labels_format(
                        filestore_backup.get("labels", {})
                    )

                    source_instance = filestore_backup.get("sourceInstance", "")
                    source_instance_id = (
                        source_instance.split("/")[-1]
                        if "/" in source_instance
                        else source_instance
                    )

                    filestore_backup.update(
                        {
                            "project": project_id,
                            "backup_id": backup_id,
                            "full_name": backup_name,
                            "location": location,
                            "source_instance": source_instance,
                            "source_instance_id": source_instance_id,
                            "labels": labels,
                            "google_cloud_logging": self.set_google_cloud_logging(
                                "Filestore", "Backup", project_id, backup_id
                            ),
                        }
                    )

                    backup_data = FilestoreBackupData(filestore_backup, strict=False)

                    ##################################
                    # 3. Make Return Resource
                    ##################################
                    backup_resource = FilestoreBackupResource(
                        {
                            "name": backup_id,
                            "account": project_id,
                            "tags": labels,
                            "region_code": location,
                            "data": backup_data,
                            "reference": ReferenceModel(backup_data.reference()),
                        }
                    )

                    ##################################
                    # 4. Make Collected Region Code
                    ##################################
                    self.set_region_code(location)

                    ##################################
                    # 5. Make Resource Response Object
                    ##################################
                    collected_cloud_services.append(
                        FilestoreBackupResponse({"resource": backup_resource})
                    )

                except Exception as e:
                    _LOGGER.error(
                        f"Failed to process backup {backup_id}: {e}",
                        exc_info=True,
                    )
                    error_response = self.generate_resource_error_response(
                        e, "Filestore", "Backup", backup_id
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(f"Failed to collect Filestore backups: {e}", exc_info=True)
            error_response = self.generate_resource_error_response(
                e, "Filestore", "Backup", "collection"
            )
            error_responses.append(error_response)

        _LOGGER.debug(
            f"** Filestore Backup Finished {time.time() - start_time} Seconds **"
        )
        return collected_cloud_services, error_responses
