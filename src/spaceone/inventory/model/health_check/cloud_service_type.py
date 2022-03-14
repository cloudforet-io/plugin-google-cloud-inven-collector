import os

from spaceone.inventory.libs.common_parser import *
from spaceone.inventory.libs.schema.metadata.dynamic_widget import CardWidget, ChartWidget
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, SearchField, DateTimeDyField, EnumDyField, \
    SizeField
from spaceone.inventory.libs.schema.cloud_service_type import CloudServiceTypeResource, CloudServiceTypeResponse, \
    CloudServiceTypeMeta

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, 'widget/total_count.yml')
count_by_region_conf = os.path.join(current_dir, 'widget/count_by_region.yml')
count_by_project_conf = os.path.join(current_dir, 'widget/count_by_project.yml')

cst_health_check = CloudServiceTypeResource()
cst_health_check.name = 'HealthCheck'
cst_health_check.provider = 'google_cloud'
cst_health_check.group = 'ComputeEngine'
cst_health_check.service_code = 'ComputeEngine'
cst_health_check.labels = ['Networking', 'Compute']
cst_health_check.tags = {
    'spaceone:icon': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/Compute_Engine.svg',
}

cst_health_check._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source('Name', 'data.name'),
        TextDyField.data_source('Location', 'data.location'),
        EnumDyField.data_source('Type', 'data.type', default_badge={
            'primary': ['TCP'],
            'indigo.500': ['SSL'],
            'coral.600': ['HTTP', 'HTTPS'],
            'green.500': ['HTTP2'],
            'gray.900': ['GRPC']
        }),
        DateTimeDyField.data_source('Creation Time', 'data.creation_time')
    ],

    search=[
        SearchField.set(name='Name', key='data.name'),
        SearchField.set(name='Creation Time', key='data.creation_time', data_type='datetime')
    ],

    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf))
    ]
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({'resource': cst_health_check}),
]
