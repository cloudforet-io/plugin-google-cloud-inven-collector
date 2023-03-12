import os

from spaceone.inventory.libs.common_parser import get_data_from_yaml
from spaceone.inventory.libs.schema.cloud_service_type import *
from spaceone.inventory.libs.schema.metadata.dynamic_widget import CardWidget, ChartWidget
from spaceone.inventory.libs.schema.metadata.dynamic_field import EnumDyField, TextDyField, SizeField, SearchField, \
    DateTimeDyField
from spaceone.inventory.conf.cloud_service_conf import *

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, 'widget/total_count.yml')
count_by_region_conf = os.path.join(current_dir, 'widget/count_by_region.yml')
count_by_project_conf = os.path.join(current_dir, 'widget/count_by_project.yml')

cst_recommendation = CloudServiceTypeResource()
cst_recommendation.name = 'Recommendation'
cst_recommendation.provider = 'google_cloud'
cst_recommendation.group = 'Recommender'
cst_recommendation.service_code = 'Recommender'
cst_recommendation.labels = ['Application Integration']
cst_recommendation.is_primary = True
cst_recommendation.is_major = True
cst_recommendation.tags = {
    'spaceone:icon': f'{ASSET_URL}/Google-cloud-platform-icon.svg',
    'spaceone:display_name': 'Recommender'
}

cst_recommendation._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source('description', 'data.description'),
        TextDyField.data_source('Recommendation action', 'data.content.overview.recommendedAction'),
        EnumDyField.data_source('State', 'data.state_info.state', default_state={
            'safe': ['ACTIVE', 'SUCCEEDED'],
            'disable': ['CLAIMED'],
            'alert': ['STATE_UNSPECIFIED', 'DISMISSED', 'FAILED'],
        }),
        EnumDyField.data_source('Category', 'data.primary_impact.category', default_badge={
            'indigo.500': ['COST'],
            'peacock.500': ['SUSTAINABILITY'],
            'violet.500': ['RELIABILITY'],
            'blue.500': ['PERFORMANCE'],
            'green.500': ['MANAGEABILITY'],
            'yellow.500': ['SECURITY'],
            'coral.500': ['CATEGORY_UNSPECIFIED']
        }),
        TextDyField.data_source('Location', 'region_code'),
        TextDyField.data_source('Recommender subtype', 'data.recommender_subtype'),
        TextDyField.data_source('Instance type', 'data.display.instance_type'),
        DateTimeDyField.data_source('Last refresh time', 'data.last_refresh_time'),
        TextDyField.data_source('priority', 'data.priority'),
    ],
    search=[
        SearchField.set(name='Recommendation action', key='data.content.overview.recommendedAction'),
        SearchField.set(name='State', key='data.state_info.state'),
        SearchField.set(name='Category', key='data.primary_impact.category'),
        SearchField.set(name='Location', key='region_code'),
        SearchField.set(name='Insight type', key='data.display.insight_type'),
        SearchField.set(name='Recommender subtype', key='data.recommender_subtype'),
        SearchField.set(name='priority', key='data.priority'),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf))
    ]
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({'resource': cst_recommendation}),
]
