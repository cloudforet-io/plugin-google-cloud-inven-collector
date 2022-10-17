import time
import logging

from spaceone.inventory.connector.pub_sub.snapshot import SnapshotConnector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.model.pub_sub.snapshot.cloud_service_type import CLOUD_SERVICE_TYPES

_LOGGER = logging.getLogger(__name__)


class SnapshotManager(GoogleCloudManager):
    connector_name = 'SnapshotManager'
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
        _LOGGER.debug(f'** Pub/Sub snapshot START **')

        start_time = time.time()
        collected_cloud_services = []
        error_responses = []
        snapshot_id = ""

        secret_data = params['secret_data']
        project_id = secret_data['project_id']

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        snapshot_conn: SnapshotConnector = self.locator.get_connector(self.connector_name, **params)

        _LOGGER.debug(f'** Firewall Finished {time.time() - start_time} Seconds **')
        return collected_cloud_services, error_responses