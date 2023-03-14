import logging
import time
import requests

from bs4 import BeautifulSoup
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

        recommendation_type_map = self._create_insight_type_by_crawling()
        recommendation_conn: RecommendationConnector = self.locator.get_connector(RecommendationConnector, **params)

        for recommendation_name in target_recommendation_names:
            try:
                recommendation = recommendation_conn.get_recommendation(recommendation_name)
                recommendation_response = self._create_recommendation_response(recommendation, project_id,
                                                                               recommendation_type_map)
                collected_cloud_services.append(recommendation_response)

            except Exception as e:
                _LOGGER.error(f'[collect_cloud_service] => {e}', exc_info=True)
                error_response = self.generate_resource_error_response(e, 'Recommender', 'Recommendation',
                                                                       recommendation_name)
                error_responses.append(error_response)

        collected_cloud_services.extend(self.cloud_service_types)
        _LOGGER.debug(f'** Recommender Recommendation Finished {time.time() - start_time} Seconds **')
        return collected_cloud_services, error_responses

    @staticmethod
    def _create_insight_type_by_crawling():
        res = requests.get("https://cloud.google.com/recommender/docs/recommenders")
        soup = BeautifulSoup(res.content, 'html.parser')
        table = soup.find("table")
        rows = table.find_all("tr")

        recommendation_type_map = {}
        category = ''
        for row in rows:
            cols = row.find_all("td")
            cols = [ele.text.strip() for ele in cols]
            if cols:
                try:
                    category, name, recommendation_type, short_description = cols
                except ValueError:
                    name, recommendation_type, short_description = cols

                if "\n" in recommendation_type:
                    recommendation_type = recommendation_type.split("\n")
                else:
                    recommendation_type = [recommendation_type]

                for recommend_type in recommendation_type:
                    recommendation_type_map[recommend_type] = {
                        'category': category,
                        'name': name,
                        'short_description': short_description
                    }

        return recommendation_type_map

    @staticmethod
    def _switch_insight_type_key_to_value(insight_type_map):
        new_insight_type_map = {}
        for key, value in insight_type_map.items():
            if isinstance(value, list):
                for element in value:
                    new_insight_type_map[element] = key
            else:
                new_insight_type_map[value] = key
        return new_insight_type_map

    def _create_recommendation_response(self, recommendation, project_id, recommendation_type_map):
        region, instance_type = self._get_region_and_instance_type(recommendation['name'])

        display = {
            'instance_type': instance_type,
            'instance_type_name': recommendation_type_map[instance_type]['name'],
            'instance_type_description': recommendation_type_map[instance_type]['short_description'],
            'priority_display': self.convert_readable_priority(recommendation['priority']),
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

    @staticmethod
    def convert_readable_priority(priority):
        if priority == 'P1':
            return 'Highest'
        elif priority == 'P2':
            return 'Second Highest'
        elif priority == 'P3':
            return 'Second Lowest'
        elif priority == 'P4':
            return 'Lowest'
        else:
            return 'Unspecified'
