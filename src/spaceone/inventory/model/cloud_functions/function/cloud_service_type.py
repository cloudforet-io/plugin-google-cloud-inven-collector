import os

from spaceone.inventory.libs.common_parser import *
from spaceone.inventory.libs.schema.metadata.dynamic_widget import CardWidget, ChartWidget
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, SearchField, DateTimeDyField, \
    EnumDyField, SizeField
from spaceone.inventory.libs.schema.cloud_service_type import CloudServiceTypeResource, CloudServiceTypeResponse, \
    CloudServiceTypeMeta

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, 'widget/total_count.yml')
count_by_region_conf = os.path.join(current_dir, 'widget/count_by_region.yml')
count_by_project_conf = os.path.join(current_dir, 'widget/count_by_project.yml')

cst_function = CloudServiceTypeResource()
cst_function.name = 'Function'
cst_function.provider = 'google_cloud'
cst_function.group = 'CloudFunctions'
cst_function.service_code = 'Cloud Functions'
cst_function.is_primary = True
cst_function.is_major = True
cst_function.labels = ['Compute']
cst_function.tags = {
    'spaceone:icon': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/cloud_functions.svg',
    'spaceone:display_name': 'CloudFunctions'
}

cst_function._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        EnumDyField.data_source('Status', 'data.state', default_state={
            'safe': ['ACTIVE'],
            'warning': ['DEPLOYING', 'DELETING'],
            'alert': ['STATE_UNSPECIFIED', 'FAILED', 'UNKNOWN']
        }),
        TextDyField.data_source('Environment', 'data.display.environment'),
        TextDyField.data_source('ID', 'data.display.function_id'),
        TextDyField.data_source('Last deployed', 'data.display.last_deployed'),
        TextDyField.data_source('Region', 'region_code'),
        # TextDyField.data_source('Trigger'),
        # TextDyField.data_source('Runtime'),
        # TextDyField.data_source('Memory allocated'),
        # TextDyField.data_source('Timeout'),
        # TextDyField.data_source('Executed function'),
        # TextDyField.data_source('Authentication')
    ],
    search=[
        # SearchField.set(name='Status', key=''),
        # SearchField.set(name='Environment', key=''),
        # SearchField.set(name='ID', key=''),
        # SearchField.set(name='Last deployed', key=''),
        # SearchField.set(name='Trigger', key=''),
        # SearchField.set(name='Runtime', key=''),
        # SearchField.set(name='Memory allocated', key=''),
        # SearchField.set(name='Timeout', key=''),
        # SearchField.set(name='Authentication', key=''),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf))
    ]
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({'resource': cst_function}),
]
