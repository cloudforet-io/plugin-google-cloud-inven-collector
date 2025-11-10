import logging
import time
from typing import List, Tuple

from spaceone.inventory.connector.filestore.snapshot_v1 import (
    FilestoreSnapshotConnector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.filestore.snapshot.cloud_service import (
    FilestoreSnapshotResource,
    FilestoreSnapshotResponse,
)
from spaceone.inventory.model.filestore.snapshot.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.filestore.snapshot.data import FilestoreSnapshotData

_LOGGER = logging.getLogger(__name__)


class FilestoreSnapshotManager(GoogleCloudManager):
    connector_name = "FilestoreSnapshotConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    snapshot_conn = None

    def collect_cloud_service(
        self, params
    ) -> Tuple[List[FilestoreSnapshotResponse], List]:
        _LOGGER.debug("** Filestore Snapshot START **")
        start_time = time.time()

        collected_cloud_services = []
        error_responses = []
        snapshot_id = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        try:
            ##################################
            # 0. Gather All Related Resources
            ##################################
            self.snapshot_conn: FilestoreSnapshotConnector = self.locator.get_connector(
                self.connector_name, **params
            )

            # Get Filestore snapshots (v1 API)
            filestore_snapshots = self.snapshot_conn.list_all_snapshots()

            for filestore_snapshot in filestore_snapshots:
                try:
                    ##################################
                    # 1. Set Basic Information
                    ##################################
                    snapshot_name = filestore_snapshot.get("name", "")
                    snapshot_id = (
                        snapshot_name.split("/")[-1]
                        if "/" in snapshot_name
                        else snapshot_name
                    )
                    location = filestore_snapshot.get("location", "")
                    instance_name = filestore_snapshot.get("instance_name", "")
                    instance_id = (
                        instance_name.split("/")[-1]
                        if "/" in instance_name
                        else instance_name
                    )

                    ##################################
                    # 2. Make Base Data
                    ##################################
                    labels = self.convert_labels_format(
                        filestore_snapshot.get("labels", {})
                    )

                    filestore_snapshot.update(
                        {
                            "name": snapshot_id,
                            "project": project_id,
                            "snapshot_id": snapshot_id,
                            "full_name": snapshot_name,
                            "location": location,
                            "instance_id": instance_id,
                            "labels": labels,
                            "google_cloud_logging": self.set_google_cloud_logging(
                                "Filestore", "Snapshot", project_id, snapshot_id
                            ),
                        }
                    )

                    snapshot_data = FilestoreSnapshotData(
                        filestore_snapshot, strict=False
                    )

                    ##################################
                    # 3. Make Return Resource
                    ##################################
                    snapshot_resource = FilestoreSnapshotResource(
                        {
                            "name": snapshot_id,
                            "account": project_id,
                            "tags": labels,
                            "region_code": location,
                            "data": snapshot_data,
                            "reference": ReferenceModel(snapshot_data.reference()),
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
                        FilestoreSnapshotResponse({"resource": snapshot_resource})
                    )

                except Exception as e:
                    _LOGGER.error(
                        f"Failed to process snapshot {snapshot_id}: {e}",
                        exc_info=True,
                    )
                    error_response = self.generate_resource_error_response(
                        e, "Filestore", "Snapshot", snapshot_id
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(f"Failed to collect Filestore snapshots: {e}", exc_info=True)
            error_response = self.generate_resource_error_response(
                e, "Filestore", "Snapshot", "collection"
            )
            error_responses.append(error_response)

        _LOGGER.debug(
            f"** Filestore Snapshot Finished {time.time() - start_time} Seconds **"
        )
        return collected_cloud_services, error_responses
