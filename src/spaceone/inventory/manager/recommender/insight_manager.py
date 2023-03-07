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
from spaceone.inventory.model.recommender.insight.data import Insight

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
        schema_id = ""

        secret_data = params['secret_data']
        project_id = secret_data['project_id']

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        cloud_asset_conn: CloudAssetConnector = self.locator.get_connector(CloudAssetConnector, **params)

        insight_type_map = self._create_insight_type_by_crawling()
        assets = cloud_asset_conn.list_assets_in_project()

        target_insights = self._create_target_parents(assets, insight_type_map)

        # # for test
        # target_insights = {'global': target_insights['global']}
        # print(target_insights)

        insights = self._list_insights(target_insights, params)
        print(insights)

        _LOGGER.debug(f'** Recommender Insight Finished {time.time() - start_time} Seconds **')
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

        return self._transform_insight_type(insight_type_map)

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
