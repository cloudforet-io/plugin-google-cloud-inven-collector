import logging
import time

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.recommender.recommendation.cloud_sevice_type import CLOUD_SERVICE_TYPES
from spaceone.inventory.model.recommender.recommendation.cloud_service import RecommendationResource, \
    RecommendationResponse
from spaceone.inventory.model.recommender.recommendation.data import Recommendation
from spaceone.inventory.connector import RecommendationConnector

_LOGGER = logging.getLogger(__name__)


class RecommendationManager(GoogleCloudManager):
    connector_name = 'RecommendationConnector'
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
        _LOGGER.debug(f'** Recommendation START **')

        start_time = time.time()
        collected_cloud_services = []
        error_responses = []

        secret_data = params['secret_data']
        project_id = secret_data['project_id']
        target_recommendation_names = params['recommendation_names']

        recommendation_conn: RecommendationConnector = self.locator.get_connector(RecommendationConnector, **params)

        for recommendation_name in target_recommendation_names:
            try:
                recommendation = recommendation_conn.get_recommendation(recommendation_name)
                recommendation_response = self._create_recommendation_response(recommendation, project_id)
                collected_cloud_services.append(recommendation_response)

            except Exception as e:
                _LOGGER.error(f'[collect_cloud_service] => {e}', exc_info=True)
                error_response = self.generate_resource_error_response(e, 'Recommender', 'Recommendation',
                                                                       recommendation_name)
                error_responses.append(error_response)

        _LOGGER.debug(f'** Recommender Recommendation Finished {time.time() - start_time} Seconds **')
        return collected_cloud_services, error_responses

    def _create_recommendation_response(self, recommendation, project_id):
        region, instance_type = self._get_region_and_instance_type(recommendation['name'])

        display = {
            'instance_type': instance_type
        }

        recommendation.update({
            'display': display
        })

        recommendation_data = Recommendation(recommendation, strict=False)
        recommendation_resource = RecommendationResource({
            'name': recommendation_data.get('name', 'Unknown'),
            'account': project_id,
            'tags': {},
            'region_code': region,
            'instance_type': '',
            'instance_size': 0,
            'data': recommendation_data,
            'reference': ReferenceModel(recommendation_data.reference())
        })

        return RecommendationResponse({'resource': recommendation_resource})

    @staticmethod
    def _get_region_and_instance_type(name):
        try:
            project_id, resource = name.split('locations/')
            region, _, instance_type, _ = resource.split('/', 3)
            return region, instance_type

        except Exception as e:
            _LOGGER.error(f'[_get_region] recommendation passing error (data: {name}) => {e}', exc_info=True)
