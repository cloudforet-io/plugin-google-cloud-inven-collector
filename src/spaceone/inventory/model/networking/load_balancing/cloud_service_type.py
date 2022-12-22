import os

from spaceone.inventory.libs.common_parser import *
from spaceone.inventory.libs.schema.metadata.dynamic_widget import CardWidget, ChartWidget
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, SearchField, DateTimeDyField, \
    EnumDyField, ListDyField
from spaceone.inventory.libs.schema.cloud_service_type import CloudServiceTypeResource, CloudServiceTypeResponse, \
    CloudServiceTypeMeta
from spaceone.inventory.conf.cloud_service_conf import *

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
    'spaceone:icon': f'{ASSET_URL}/Load_Balancing.svg',
    'spaceone:display_name': 'LoadBalancing'
}

cst_load_balancing._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source('Type', 'data.type'),
        EnumDyField.data_source('Source', 'data.internal_or_external', default_badge={

        }),
        EnumDyField.data_source('Protocol', 'data.protocol', default_badge={
            'primary': ['HTTP', 'HTTPS'], 'indigo.500': ['TCP', 'UDP'],
            'coral.600': ['ESP', 'AH', 'SCTP', 'ICMP', 'L3_DEFAULT', 'UnKnown']
        }),
        TextDyField.data_source('Region', 'data.region'),
        DateTimeDyField.data_source('Creation Time', 'data.creation_timestamp'),
    ],

    search=[
        SearchField.set(name='ID', key='data.id'),
        SearchField.set(name='Name', key='data.name'),
        SearchField.set(name='Type', key='data.type'),
        SearchField.set(name='Source', key='data.internal_or_external'),
        SearchField.set(name='Protocol', key='data.protocol'),
        SearchField.set(name='Region', key='data.region'),
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
