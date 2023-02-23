import logging
import time

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.connector.recommender.insight import InsightConnector
from spaceone.inventory.model.recommender.insight.cloud_service import InsightResource, InsightResponse
from spaceone.inventory.model.recommender.insight.cloud_service_type import CLOUD_SERVICE_TYPES
from spaceone.inventory.model.recommender.insight.data import Insight
from spaceone.inventory.connector.compute_engine.vm_instance import VMInstanceConnector

_LOGGER = logging.getLogger(__name__)


class InsightManager(GoogleCloudManager):
    connector_name = 'InsightConnector'
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
        _LOGGER.debug(f'** Recommendations BillingAccounts START **')

        start_time = time.time()
        collected_cloud_services = []
        error_responses = []
        schema_id = ""

        secret_data = params['secret_data']
        project_id = secret_data['project_id']

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################

        vm_conn: VMInstanceConnector = self.locator.get_connector(VMInstanceConnector, **params)
        regions_from_vm = vm_conn.list_regions()
        print(regions_from_vm)

        insight_conn: InsightConnector = self.locator.get_connector(self.connector_name, **params)
        insights = insight_conn.list_insights()
