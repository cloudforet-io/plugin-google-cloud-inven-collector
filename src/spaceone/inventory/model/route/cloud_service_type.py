import os

from spaceone.inventory.libs.common_parser import *
from spaceone.inventory.libs.schema.metadata.dynamic_widget import CardWidget, ChartWidget
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, SearchField, DateTimeDyField, EnumDyField, ListDyField
from spaceone.inventory.libs.schema.cloud_service_type import CloudServiceTypeResource, CloudServiceTypeResponse, \
    CloudServiceTypeMeta

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, 'widget/total_count.yml')
count_by_region_conf = os.path.join(current_dir, 'widget/count_by_region.yml')
count_by_project_conf = os.path.join(current_dir, 'widget/count_by_project.yml')

cst_route = CloudServiceTypeResource()
cst_route.name = 'Route'
cst_route.provider = 'google_cloud'
cst_route.group = 'Networking'
cst_route.service_code = 'Networking'
cst_route.labels = ['Networking']
cst_route.tags = {
    'spaceone:icon': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/Route.svg',
}


cst_route._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source('Name', 'data.name'),
        TextDyField.data_source('Description', 'data.description'),
        TextDyField.data_source('Destination IP Range', 'data.dest_range'),
        TextDyField.data_source('Priority', 'data.priority'),
        ListDyField.data_source('Instance tags', 'data.display.instance_tags_on_list'),
        TextDyField.data_source('Network', 'data.display.network_display'),
        TextDyField.data_source('Next Hop', 'data.display.next_hop'),
        DateTimeDyField.data_source('Creation Time', 'data.creation_timestamp')
    ],

    search=[
        SearchField.set(name='ID', key='data.id'),
        SearchField.set(name='Name', key='data.name'),
        SearchField.set(name='Priority', key='data.priority'),
        SearchField.set(name='Instance Tags', key='data.tags'),
        SearchField.set(name='Network', key='data.display.network_display'),
        SearchField.set(name='Creation Time', key='data.creation_timestamp', data_type='datetime'),
    ],

    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf))
    ]
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({'resource': cst_route}),
]
