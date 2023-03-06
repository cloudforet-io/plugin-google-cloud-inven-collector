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

        cloud_asset_conn: CloudAssetConnector = self.locator.get_connector(CloudAssetConnector, **params)
        assets = cloud_asset_conn.list_assets_in_project()

        asset_types = set()
        asset_resources = set()
        exist_regions = set(REGION_INFO.keys())
        target_regions = set()
        for asset in assets:
            full_asset_type = asset['assetType']
            asset_service, asset_resource = full_asset_type.split('.googleapis.com/')
            print(full_asset_type)
            print(asset['name'])

            asset_types.add(asset_service)
            asset_resources.add(asset_resource)

            for region in exist_regions:
                if region in asset['name']:
                    target_regions.add(region)

        print(target_regions)

        insight_type_map = self._create_insight_type()
        print(insight_type_map)

        # insight_conn: InsightConnector = self.locator.get_connector(self.connector_name, **params)
        # insights = insight_conn.list_insights()
        # print(insights)

        # try:
        #     pass
        # except Exception as e:
        #     _LOGGER.error(f'[collect_cloud_service] => {e}', exc_info=True)
        #     error_response = self.generate_resource_error_response(e, 'Recommender', 'Insight', 1)
        #     error_responses.append(error_response)

        _LOGGER.debug(f'** Recommender Insight Finished {time.time() - start_time} Seconds **')
        return collected_cloud_services, error_responses

    @staticmethod
    def _create_insight_type():
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
        return insight_type_map
