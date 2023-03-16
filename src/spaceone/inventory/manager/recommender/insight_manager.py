import logging
import time
import requests

from bs4 import BeautifulSoup

from spaceone.inventory.conf.cloud_service_conf import REGION_INFO
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.connector.recommender.insight import InsightConnector
from spaceone.inventory.connector.recommender.cloud_asset import CloudAssetConnector
from spaceone.inventory.model.recommender.insight.cloud_service import InsightResource, InsightResponse
from spaceone.inventory.model.recommender.insight.cloud_service_type import CLOUD_SERVICE_TYPES
from spaceone.inventory.model.recommender.insight.data import Insight, IPAddressInsight
from spaceone.inventory.manager.recommender.recommendation_manager import RecommendationManager

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
        _LOGGER.debug(f'** Recommender START **')

        start_time = time.time()
        collected_cloud_services = []
        error_responses = []

        secret_data = params['secret_data']
        project_id = secret_data['project_id']

        cloud_asset_conn: CloudAssetConnector = self.locator.get_connector(CloudAssetConnector, **params)

        usable_insight_type_map, insight_type_map = self._create_insight_type_by_crawling()
        assets = cloud_asset_conn.list_assets_in_project()

        target_insights = self._create_target_parents(assets, usable_insight_type_map)
        insights = self._list_insights(target_insights, params)

        target_recommendation_names = []
        for insight in insights:
            origin_insights = insight["data"]
            region = insight["region"]
            insight_type = insight["insight_type"]
            for origin_insight in origin_insights:
                try:
                    recommendation_names = []
                    insight_response = self._create_insight_resource(origin_insight, region, insight_type,
                                                                     project_id, insight_type_map)
                    if associated_recommendations := origin_insight.get('associatedRecommendations'):
                        recommendation_names = self._list_recommendation_names(associated_recommendations)

                    collected_cloud_services.append(insight_response)
                    target_recommendation_names.extend(recommendation_names)

                except Exception as e:
                    _LOGGER.error(f'[collect_cloud_service] => {e}', exc_info=True)
                    error_response = self.generate_resource_error_response(e, 'Recommender', 'Insight',
                                                                           origin_insight.get('name'))
                    error_responses.append(error_response)

        _LOGGER.debug(f'** Recommender Insight Finished {time.time() - start_time} Seconds **')

        # collect recommendation
        params['recommendation_names'] = target_recommendation_names
        recommendation_cloud_services, recommendation_errors = RecommendationManager().collect_cloud_service(params)

        collected_cloud_services.extend(recommendation_cloud_services)
        error_responses.extend(recommendation_errors)

        return collected_cloud_services, error_responses

    def _create_insight_type_by_crawling(self):
        res = requests.get("https://cloud.google.com/recommender/docs/insights/insight-types")
        soup = BeautifulSoup(res.content, 'html.parser')
        table = soup.find("table")
        rows = table.find_all("tr")

        insight_type_map = {}
        for row in rows:
            cols = row.find_all("td")
            cols = [ele.text.strip() for ele in cols]
            if cols:
                service, insight_type = cols
                if "\n" in insight_type:
                    insight_type = insight_type.split("\n")
                else:
                    insight_type = [insight_type]
                insight_type_map[service] = insight_type

        return self._transform_insight_type(insight_type_map), self._switch_insight_type_key_to_value(insight_type_map)

    @staticmethod
    def _transform_insight_type(insight_type_map):
        usable_insight_type_map = {}
        for service, insight_type in insight_type_map.items():
            for insight in insight_type:
                try:
                    prefix, svc, resource, _ = insight.split('.', 3)
                except ValueError:
                    prefix, svc, resource = insight.split('.', 2)

                if usable_insight_type_map.get(svc):
                    usable_insight_type_map[svc].append(insight)
                else:
                    usable_insight_type_map[svc] = [insight]

        return usable_insight_type_map

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

    def _create_target_parents(self, assets, insight_type_map):
        target_insights = {}
        for asset in assets:
            full_asset_type = asset['assetType']
            asset_service, asset_resource = full_asset_type.split('.googleapis.com/')
            region = self._check_region(asset['name'])

            if asset_service in insight_type_map:
                if target_insights.get(region):
                    for insight_type in insight_type_map[asset_service]:
                        if insight_type not in target_insights[region]:
                            target_insights[region].append(insight_type)
                else:
                    target_insights[region] = insight_type_map[asset_service]
        return target_insights

    @staticmethod
    def _check_region(asset):
        for region in REGION_INFO:
            if region in asset:
                return region
            else:
                continue
        return 'global'

    def _list_insights(self, target_insights, params):
        insight_conn: InsightConnector = self.locator.get_connector(self.connector_name, **params)

        insights = []
        call_count = 0
        for region, insight_types in target_insights.items():
            for insight_type in insight_types:
                insight = insight_conn.list_insights(region, insight_type)
                call_count += 1
                if insight:
                    data = {'data': insight, 'region': region, 'insight_type': insight_type}
                    insights.append(data)
                time.sleep(0.1)
        _LOGGER.debug(f'[Recommender] list_insights API Call Count: {call_count}')
        return insights

    def _create_insight_resource(self, origin_insight, region, insight_type, project_id, insight_type_map):
        display = {
            'insight_type': insight_type,
            'insight_type_display': insight_type_map[insight_type],
        }
        origin_insight.update({
            'display': display
        })

        if target_resources := origin_insight.get('targetResources'):
            display['target_resources_display'] = self._change_target_resources(target_resources)

        try:
            insight_data = Insight(origin_insight, strict=False)
        except Exception as e:
            insight_data = IPAddressInsight(origin_insight, strict=False)

        insight_resource = InsightResource({
            'name': insight_data.name,
            'account': project_id,
            'tags': {},
            'region_code': region,
            'instance_type': '',
            'instance_size': 0,
            'data': insight_data,
            'reference': ReferenceModel(insight_data.reference())
        })
        return InsightResponse({'resource': insight_resource})

    @staticmethod
    def _list_recommendation_names(recommendations):
        recommendation_names = []
        for recommendation in recommendations:
            recommendation_names.append(recommendation['recommendation'])
        return recommendation_names

    def _change_target_resources(self, resources):
        new_target_resources = []
        for resource in resources:
            new_target_resources.append({'name': self._change_resource_name(resource)})
        return new_target_resources

    @staticmethod
    def _change_resource_name(resource):
        try:
            resource_name = resource.split('/')[-1]
            return resource_name
        except ValueError:
            return resource
