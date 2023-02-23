import os

from spaceone.inventory.libs.common_parser import get_data_from_yaml
from spaceone.inventory.libs.schema.cloud_service_type import *
from spaceone.inventory.libs.schema.metadata.dynamic_widget import CardWidget, ChartWidget
from spaceone.inventory.libs.schema.metadata.dynamic_field import EnumDyField, TextDyField, SizeField, SearchField
from spaceone.inventory.conf.cloud_service_conf import *

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, 'widget/total_count.yml')
count_by_region_conf = os.path.join(current_dir, 'widget/count_by_region.yml')
count_by_project_conf = os.path.join(current_dir, 'widget/count_by_project.yml')

cst_insight = CloudServiceTypeResource()
cst_insight.name = 'Insight'
cst_insight.provider = 'google_cloud'
cst_insight.group = 'Recommender'
cst_insight.service_code = 'Recommender'
cst_insight.labels = ['Application Integration']
cst_insight.is_primary = True
cst_insight.is_major = True
cst_insight.tags = {
    'spaceone:icon': f'{ASSET_URL}/recommender.svg'
}

cst_insight._metadata = CloudServiceTypeMeta.set_meta(
    fields=[],
    search=[],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf))
    ]
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({'resource': cst_insight}),
]
