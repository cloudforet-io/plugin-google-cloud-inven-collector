import os

from spaceone.inventory.libs.common_parser import *
from spaceone.inventory.libs.schema.metadata.dynamic_widget import CardWidget, ChartWidget
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, SearchField, DateTimeDyField, \
    EnumDyField, ListDyField
from spaceone.inventory.libs.schema.cloud_service_type import CloudServiceTypeResource, CloudServiceTypeResponse, \
    CloudServiceTypeMeta

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, 'widget/total_count.yml')
count_by_region_conf = os.path.join(current_dir, 'widget/count_by_region.yml')
count_by_project_conf = os.path.join(current_dir, 'widget/count_by_project.yml')

cst_load_balancing = CloudServiceTypeResource()
cst_load_balancing.name = 'LoadBalancing'
cst_load_balancing.provider = 'google_cloud'
cst_load_balancing.group = 'Networking'
cst_load_balancing.service_code = 'Networking'
cst_load_balancing.is_primary = True
cst_load_balancing.is_major = True
cst_load_balancing.labels = ['Networking']
cst_load_balancing.tags = {
    'spaceone:icon': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/Load_Balancing.svg',
}

cst_load_balancing._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source('Name', 'data.name'),
        EnumDyField.data_source('Protocol', 'data.lead_protocol', default_badge={
            'primary': ['HTTP', 'HTTPS', 'HTTP(S)'], 'indigo.500': ['TCP', 'TCP (Proxy)'],
            'coral.600': ['UDP', 'UDP (Proxy)']
        }),
        TextDyField.data_source('Region', 'data.region'),
        TextDyField.data_source('Frontends', 'data.frontend_display'),
        TextDyField.data_source('Backends', 'data.backends_display'),
        DateTimeDyField.data_source('Creation Time', 'data.creation_timestamp'),
    ],

    search=[
        SearchField.set(name='ID', key='data.id'),
        SearchField.set(name='Name', key='data.name'),
        SearchField.set(name='Protocol', key='data.lead_protocol'),
        SearchField.set(name='Region', key='data.region'),
        SearchField.set(name='description', key='data.description'),
        SearchField.set(name='Creation Time', key='data.creation_timestamp', data_type='datetime'),
    ],

    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf))
    ]
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({'resource': cst_load_balancing}),
]
