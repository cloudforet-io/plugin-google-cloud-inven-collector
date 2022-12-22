import os

from spaceone.inventory.libs.common_parser import *
from spaceone.inventory.libs.schema.metadata.dynamic_widget import CardWidget, ChartWidget
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, SearchField, DateTimeDyField, EnumDyField, ListDyField
from spaceone.inventory.libs.schema.cloud_service_type import CloudServiceTypeResource, CloudServiceTypeResponse, \
    CloudServiceTypeMeta
from spaceone.inventory.conf.cloud_service_conf import *

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, 'widget/total_count.yml')
count_by_region_conf = os.path.join(current_dir, 'widget/count_by_region.yml')
count_by_project_conf = os.path.join(current_dir, 'widget/count_by_project.yml')

cst_external_ip = CloudServiceTypeResource()
cst_external_ip.name = 'ExternalIPAddress'
cst_external_ip.provider = 'google_cloud'
cst_external_ip.group = 'Networking'
cst_external_ip.service_code = 'Networking'
cst_external_ip.labels = ['Networking']
cst_external_ip.tags = {
    'spaceone:icon': f'{ASSET_URL}/External_IP_Address.svg',
}


cst_external_ip._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source('External Address', 'data.address'),
        TextDyField.data_source('Region', 'data.region'),
        EnumDyField.data_source('Type', 'data.is_ephemeral', default_badge={
            'indigo.500': ['Static'], 'coral.600': ['Ephemeral']
        }),
        EnumDyField.data_source('Version', 'data.ip_version_display', default_badge={
            'indigo.500': ['IPv4'], 'coral.600': ['IPv6']
        }),
        ListDyField.data_source('In Used By', 'data.used_by'),

        TextDyField.data_source('Network Tier', 'data.network_tier_display'),

        DateTimeDyField.data_source('Creation Time', 'data.creation_timestamp'),
    ],

    search=[
        SearchField.set(name='ID', key='data.id'),
        SearchField.set(name='Name', key='data.name'),
        SearchField.set(name='IP Address', key='data.address'),
        SearchField.set(name='Version', key='data.ip_version_display'),
        SearchField.set(name='Network Tier', key='data.network_tier_display'),
        SearchField.set(name='Creation Time', key='data.creation_timestamp', data_type='datetime'),
    ],

    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf))
    ]
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({'resource': cst_external_ip}),
]
