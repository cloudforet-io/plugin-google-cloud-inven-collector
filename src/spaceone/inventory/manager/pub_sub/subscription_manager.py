import time
import logging

from spaceone.inventory.connector.pub_sub.subscription import SubscriptionConnector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.model.pub_sub.subscription.cloud_service_type import CLOUD_SERVICE_TYPES

_LOGGER = logging.getLogger(__name__)


class SubscriptionManager(GoogleCloudManager):
    connector_name = 'SubscriptionConnector'
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
        _LOGGER.debug(f'** Pub/Sub subscription START **')

        start_time = time.time()
        collected_cloud_services = []
        error_responses = []
        subscription_id = ""

        secret_data = params['secret_data']
        project_id = secret_data['project_id']

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        subscription_conn: SubscriptionConnector = self.locator.get_connector(self.connector_name, **params)

        _LOGGER.debug(f'** Firewall Finished {time.time() - start_time} Seconds **')
        return collected_cloud_services, error_responses