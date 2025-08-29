import logging
import time

from spaceone.inventory.connector.pub_sub.snapshot import SnapshotConnector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.pub_sub.snapshot.cloud_service import (
    SnapshotResource,
    SnapshotResponse,
)
from spaceone.inventory.model.pub_sub.snapshot.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.pub_sub.snapshot.data import Snapshot

_LOGGER = logging.getLogger(__name__)


class SnapshotManager(GoogleCloudManager):
    connector_name = "PubSubSnapshotConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        """
        Args:
            params:
                - options
                - schema
                - secret_data
                - filter
                - zones
        Response:
            CloudServiceResponse/ErrorResourceResponse
        """
        _LOGGER.debug("** PubSub Snapshot START **")

        start_time = time.time()
        collected_cloud_services = []
        error_responses = []
        snapshot_id = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        snapshot_conn: SnapshotConnector = self.locator.get_connector(
            self.connector_name, **params
        )
        snapshots = snapshot_conn.list_snapshots()

        for snapshot in snapshots:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                snapshot_name = snapshot.get("name")
                snapshot_id = self._make_snapshot_id(snapshot_name, project_id)

                ##################################
                # 2. Make Base Data
                ##################################

                ##################################
                # 3. Make snapshot data
                ##################################
                snapshot.update(
                    {
                        "id": snapshot_id,
                        "project": project_id,
                    }
                )

                snapshot.update(
                    {
                        "google_cloud_logging": self.set_google_cloud_logging(
                            "PubSub", "Snapshot", project_id, snapshot_name
                        )
                    }
                )

                snapshot_data = Snapshot(snapshot, strict=False)

                ##################################
                # 4. Make SubscriptionResource Code
                ##################################
                snapshot_resource = SnapshotResource(
                    {
                        "name": snapshot_name,
                        "account": project_id,
                        "tags": snapshot_data.labels,
                        "region_code": "Global",
                        "instance_type": "",
                        "instance_size": 0,
                        "data": snapshot_data,
                        "reference": ReferenceModel(snapshot_data.reference()),
                    }
                )

                ##################################
                # 5. Make Resource Response Object
                ##################################
                collected_cloud_services.append(
                    SnapshotResponse({"resource": snapshot_resource})
                )

            except Exception as e:
                _LOGGER.error(f"[collect_cloud_service] => {e}", exc_info=True)
                error_response = self.generate_resource_error_response(
                    e, "PubSub", "Snapshot", snapshot_id
                )
                error_responses.append(error_response)

        _LOGGER.debug(
            f"** PubSub Snapshot Finished {time.time() - start_time} Seconds **"
        )
        return collected_cloud_services, error_responses

    @staticmethod
    def _make_snapshot_id(snapshot_name, project_id):
        path, snapshot_id = snapshot_name.split(f"projects/{project_id}/snapshots/")
        return snapshot_id
