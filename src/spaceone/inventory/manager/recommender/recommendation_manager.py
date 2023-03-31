import logging
import time
import requests
import json

from bs4 import BeautifulSoup

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.connector.recommender.cloud_asset import CloudAssetConnector
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.recommender.recommendation.cloud_sevice_type import CLOUD_SERVICE_TYPES
from spaceone.inventory.model.recommender.recommendation.cloud_service import RecommendationResource, \
    RecommendationResponse
from spaceone.inventory.model.recommender.recommendation.data import Recommendation
from spaceone.inventory.model.recommender.recommendation.recommender_data import Recommender
from spaceone.inventory.connector import RecommendationConnector, InsightConnector

_LOGGER = logging.getLogger(__name__)

_RECOMMENDATION_TYPE_DOCS_URL = 'https://cloud.google.com/recommender/docs/recommenders'

_UNAVAILABLE_RECOMMENDER_IDS = [
    'google.cloudbilling.commitment.SpendBasedCommitmentRecommender',
    'google.accounts.security.SecurityKeyRecommender',
    'google.cloudfunctions.PerformanceRecommender'
]

_COST_RECOMMENDER_IDS = [
    'google.bigquery.capacityCommitments.Recommender',
    'google.cloudsql.instance.IdleRecommender',
    'google.cloudsql.instance.OverprovisionedRecommender',
    'google.compute.commitment.UsageCommitmentRecommender',
    'google.cloudbilling.commitment.SpendBasedCommitmentRecommender',
    'google.compute.image.IdleResourceRecommender',
    'google.compute.address.IdleResourceRecommender',
    'google.compute.disk.IdleResourceRecommender',
    'google.compute.instance.IdleResourceRecommender'
]


class RecommendationManager(GoogleCloudManager):
    connector_name = 'RecommendationConnector'
    cloud_service_types = CLOUD_SERVICE_TYPES
    project_id = None
    recommender_map = {}

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
        self.project_id = secret_data['project_id']
        self.recommender_map = self._create_recommendation_id_map_by_crawling()

        cloud_asset_conn: CloudAssetConnector = self.locator.get_connector(CloudAssetConnector, **params)
        assets = cloud_asset_conn.list_assets_in_project()
        asset_names = [asset['name'] for asset in assets]
        target_locations = self._create_target_locations(asset_names)

        recommendation_parents = self._create_recommendation_parents(target_locations)

        recommendation_conn: RecommendationConnector = self.locator.get_connector(RecommendationConnector, **params)

        preprocessed_recommendations = []
        for recommendation_parent in recommendation_parents:
            recommendations = recommendation_conn.list_recommendations(recommendation_parent)
            for recommendation in recommendations:
                try:
                    region, recommender_id = self._get_region_and_recommender_id(recommendation['name'])

                    display = {
                        'recommender_id': recommender_id,
                        'recommender_id_name': self.recommender_map[recommender_id]['name'],
                        'recommender_id_description': self.recommender_map[recommender_id]['short_description'],
                        'priority_display': self.convert_readable_priority(recommendation['priority']),
                        'overview': json.dumps(recommendation['content']['overview']),
                        'operations': json.dumps(recommendation['content']['operationGroups']),
                        'operation_actions': self._get_actions(recommendation['content']),
                        'location': self._get_location(recommendation_parent)
                    }

                    if resource := recommendation['content']['overview'].get('resourceName'):
                        display['resource'] = self._change_resource(resource)

                    if cost_info := recommendation['primaryImpact'].get('costProjection'):
                        cost = cost_info.get('cost', {})
                        display['cost'], display['cost_description'] = self._change_cost_to_description(cost)

                    if insights := recommendation['associatedInsights']:
                        insight_conn: InsightConnector = self.locator.get_connector(InsightConnector, **params)
                        related_insights = self._list_insights(insights, insight_conn)
                        display['insights'] = self._change_insights(related_insights)

                    recommendation.update({
                        'display': display
                    })

                    recommendation_data = Recommendation(recommendation, strict=False)
                    preprocessed_recommendations.append(recommendation_data.to_primitive())

                except Exception as e:
                    _LOGGER.error(f'[collect_cloud_service] => {e}', exc_info=True)
                    error_response = self.generate_resource_error_response(e, 'Recommender',
                                                                           'Recommendation', recommendation)
                    error_responses.append(error_response)

        recommenders = self._create_recommenders(preprocessed_recommendations)
        merged_recommenders = self._merge_recommenders(recommenders)
        for recommender in merged_recommenders:
            try:
                total_cost = 0
                resource_count = 0
                total_priority_level = {
                    'Lowest': 0,
                    'Second Lowest': 0,
                    'Highest': 0,
                    'Second Highest': 0
                }
                for recommendation in recommender['recommendations']:
                    if recommender['category'] == 'COST':
                        total_cost += recommendation.get('cost', 0)

                    if recommendation.get('affected_resource'):
                        resource_count += 1

                    total_priority_level[recommendation.get('priority_level')] += 1

                if total_cost:
                    recommender['cost_savings'] = f'Total ${round(total_cost, 2)}/month'
                if resource_count:
                    recommender['resource_count'] = resource_count

                recommender['state'], recommender['primary_priority_level'] = self._get_state_and_priority(
                    total_priority_level)

                recommender_data = Recommender(recommender, strict=False)

                recommender_resource = RecommendationResource({
                    'name': recommender_data.name,
                    'account': self.project_id,
                    'tags': {},
                    'region_code': 'global',
                    'instance_type': '',
                    'instance_size': 0,
                    'data': recommender_data,
                    'reference': ReferenceModel(recommender_data.reference())
                })
                recommendation_response = RecommendationResponse({'resource': recommender_resource})
                collected_cloud_services.append(recommendation_response)

            except Exception as e:
                _LOGGER.error(f'[collect_cloud_service] => {e}', exc_info=True)
                error_response = self.generate_resource_error_response(e, 'Recommender',
                                                                       'Recommendation', recommender)
                error_responses.append(error_response)

        _LOGGER.debug(f'** Recommender Recommendation Finished {time.time() - start_time} Seconds **')
        return collected_cloud_services, error_responses

    @staticmethod
    def _create_recommendation_id_map_by_crawling():
        res = requests.get(_RECOMMENDATION_TYPE_DOCS_URL)
        soup = BeautifulSoup(res.content, 'html.parser')
        table = soup.find("table")
        rows = table.find_all("tr")

        recommendation_id_map = {}
        category = ''
        for row in rows:
            cols = row.find_all("td")
            cols = [ele.text.strip() for ele in cols]
            if cols:
                try:
                    category, name, recommender_id, short_description = cols
                except ValueError:
                    name, recommender_id, short_description = cols

                if recommender_id.count('google.') > 1:
                    recommender_ids = []
                    re_ids = recommender_id.split('google.')[1:]
                    for re_id in re_ids:
                        re_id = 'google.' + re_id
                        if re_id not in _UNAVAILABLE_RECOMMENDER_IDS:
                            recommender_ids.append(re_id)
                else:
                    if recommender_id not in _UNAVAILABLE_RECOMMENDER_IDS:
                        recommender_ids = [recommender_id]
                    else:
                        continue

                for recommender_id in recommender_ids:
                    recommendation_id_map[recommender_id] = {
                        'category': category,
                        'name': name,
                        'short_description': short_description
                    }

        return recommendation_id_map

    @staticmethod
    def _create_target_locations(asset_names):
        locations = []
        for asset_name in asset_names:
            if 'locations/' in asset_name or 'regions/' in asset_name and 'subnetworks' not in asset_name:
                try:
                    prefix, sub_asset = asset_name.split('locations/')
                    location, _ = sub_asset.split('/', 1)

                    if location not in locations:
                        locations.append(location)

                except ValueError:
                    prefix, sub_asset = asset_name.split('regions/')
                    location, _ = sub_asset.split('/', 1)

                    if location not in locations:
                        locations.append(location)
        return locations

    def _create_recommendation_parents(self, locations):
        recommendation_parents = []
        for location in locations:
            for recommender_id in self.recommender_map.keys():
                if recommender_id in _COST_RECOMMENDER_IDS and location != 'global' \
                        and location[-2:] not in ['-a', '-b', '-c']:
                    regions_and_zones = [location, f'{location}-a', f'{location}-b', f'{location}-c']
                    for region_or_zone in regions_and_zones:
                        recommendation_parents.append(
                            f'projects/{self.project_id}/locations/{region_or_zone}/recommenders/{recommender_id}'
                        )
                else:
                    recommendation_parents.append(
                        f'projects/{self.project_id}/locations/{location}/recommenders/{recommender_id}'
                    )

        return recommendation_parents

    @staticmethod
    def _get_region_and_recommender_id(recommendation_name):
        try:
            project_id, resource = recommendation_name.split('locations/')
            region, _, instance_type, _ = resource.split('/', 3)
            return region, instance_type

        except Exception as e:
            _LOGGER.error(f'[_get_region] recommendation passing error (data: {recommendation_name}) => {e}',
                          exc_info=True)

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

    @staticmethod
    def _change_resource(resource):
        try:
            resource_name = resource.split('/')[-1]
            return resource_name
        except ValueError:
            return resource

    @staticmethod
    def _change_cost_to_description(cost):
        currency = cost.get('currencyCode', 'USD')
        total_cost = 0

        if nanos := cost.get('nanos', 0):
            if nanos < 0:
                nanos = -nanos / 1000000000
            else:
                nanos = nanos / 1000000000
            total_cost += nanos

        if units := int(cost.get('units', 0)):
            if units < 0:
                units = -units
            total_cost += units

        total_cost = round(total_cost, 2)
        description = f'{total_cost}/month'

        if 'USD' in currency:
            currency = '$'
            description = f'{currency}{description}'

        return total_cost, description

    @staticmethod
    def _list_insights(insights, insight_conn):
        related_insights = []
        for insight in insights:
            insight_name = insight['insight']
            insight = insight_conn.get_insight(insight_name)
            related_insights.append(insight)
        return related_insights

    def _change_insights(self, insights):
        changed_insights = []
        for insight in insights:
            changed_insights.append({
                'name': insight['name'],
                'description': insight['description'],
                'last_refresh_time': insight['lastRefreshTime'],
                'observation_period': insight['observationPeriod'],
                'state': insight['stateInfo']['state'],
                'category': insight['category'],
                'insight_subtype': insight['insightSubtype'],
                'severity': insight['severity'],
                'etag': insight['etag'],
                'target_resources': self._change_target_resources(insight['targetResources'])
            })
        return changed_insights

    def _change_target_resources(self, resources):
        new_target_resources = []
        for resource in resources:
            new_target_resources.append({'name': resource,
                                         'display_name': self._change_resource_name(resource)})
        return new_target_resources

    @staticmethod
    def _change_resource_name(resource):
        try:
            resource_name = resource.split('/')[-1]
            return resource_name
        except ValueError:
            return resource

    @staticmethod
    def _get_location(recommendation_parent):
        try:
            project_id, parent_info = recommendation_parent.split('locations/')
            location, _ = parent_info.split('/', 1)
            return location
        except Exception as e:
            _LOGGER.error(f'[get_location] recommendation passing error (data: {recommendation_parent}) => {e}',
                          exc_info=True)

    @staticmethod
    def _get_actions(content):
        overview = content.get('overview', {})
        operation_groups = content.get('operationGroups', [])
        actions = ''

        if recommended_action := overview.get('recommendedAction'):
            return recommended_action

        else:
            for operation_group in operation_groups:
                operations = operation_group.get('operations', [])
                for operation in operations:
                    action = operation.get('action', 'test')
                    first, others = action[0], action[1:]
                    action = first.upper() + others

                    if action == 'Test':
                        continue
                    elif actions:
                        actions += f' and {action}'
                    else:
                        actions += action

            return actions

    @staticmethod
    def _create_recommenders(preprocessed_recommendations):
        recommenders = []
        for pre_recommendation in preprocessed_recommendations:

            redefined_insights = []
            if insights := pre_recommendation['display']['insights']:
                for insight in insights:
                    redefined_insights.append({
                        'description': insight['description'],
                        'severity': insight['severity'],
                        'category': insight['category']
                    })

            redefined_recommendations = [{
                'description': pre_recommendation['description'],
                'state': pre_recommendation['state_info']['state'],
                'affected_resource': pre_recommendation['display']['resource'],
                'location': pre_recommendation['display']['location'],
                'priority_level': pre_recommendation['display']['priority_display'],
                'operations': pre_recommendation['display']['operation_actions'],
                'cost': pre_recommendation['display']['cost'],
                'cost_savings': pre_recommendation['display']['cost_description'],
                'insights': redefined_insights
            }]

            recommender = {
                'name': pre_recommendation['display']['recommender_id_name'],
                'id': pre_recommendation['display']['recommender_id'],
                'description': pre_recommendation['display']['recommender_id_description'],
                'category': pre_recommendation['primary_impact']['category'],
                'recommendations': redefined_recommendations
            }

            recommenders.append(recommender)
        return recommenders

    def _merge_recommenders(self, recommenders):
        merged_recommenders = []
        for recommender in recommenders:
            recommender_id = recommender['id']
            if 'recommendations' not in self.recommender_map[recommender_id]:
                self.recommender_map[recommender_id].update(recommender)
            else:
                for recommendation in recommender['recommendations']:
                    self.recommender_map[recommender_id]['recommendations'].append(recommendation)
            merged_recommenders.append(self.recommender_map[recommender_id])
        return merged_recommenders

    @staticmethod
    def _get_state_and_priority(total_priority_level):
        if total_priority_level['Highest'] > 0:
            return 'error', 'Highest'

        if total_priority_level['Second Highest'] > 0:
            return 'warning', 'Second Highest'

        if total_priority_level['Second Lowest'] > 0:
            return 'ok', 'Second Lowest'
        else:
            return 'ok', 'Lowest'
