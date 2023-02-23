import logging
import time

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.connector.recommender.recommendation import RecommendationConnector
# from spaceone.inventory.model.recommendations.schema.cloud_service import SchemaResource, SchemaResponse
# from spaceone.inventory.model.recommendations.schema.cloud_service_type import CLOUD_SERVICE_TYPES
# from spaceone.inventory.model.recommendations.schema.data import Recommendations

_LOGGER = logging.getLogger(__name__)


class RecommendationManager(GoogleCloudManager):
    connector_name = 'RecommendationConnector'
    # cloud_service_types = CLOUD_SERVICE_TYPES

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

        recommendation_conn: RecommendationConnector = self.locator.get_connector(self.connector_name, **params)
        recommendations = recommendation_conn.list_recommendations()
