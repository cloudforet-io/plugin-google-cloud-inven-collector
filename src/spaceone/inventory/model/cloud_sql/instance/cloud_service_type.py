import os

from spaceone.inventory.libs.common_parser import *
from spaceone.inventory.libs.schema.metadata.dynamic_widget import CardWidget, ChartWidget
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, ListDyField, SearchField, \
    EnumDyField
from spaceone.inventory.libs.schema.cloud_service_type import CloudServiceTypeResource, CloudServiceTypeResponse, \
    CloudServiceTypeMeta
from spaceone.inventory.conf.cloud_service_conf import *

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, 'widget/total_count.yml')
count_by_region_conf = os.path.join(current_dir, 'widget/count_by_region.yml')
count_by_project_conf = os.path.join(current_dir, 'widget/count_by_project.yml')

cst_instance = CloudServiceTypeResource()
cst_instance.name = 'Instance'
cst_instance.provider = 'google_cloud'
cst_instance.group = 'CloudSQL'
cst_instance.service_code = 'Cloud SQL'
cst_instance.labels = ['Database']
cst_instance.is_primary = True
cst_instance.is_major = True
cst_instance.tags = {
    'spaceone:icon': f'{ASSET_URL}/Cloud_SQL.svg',
}

cst_instance._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        EnumDyField.data_source('State', 'data.display_state', default_state={
            'safe': ['RUNNING'],
            'disable': ['UNKNOWN', 'ON-DEMAND'],
            'alert': ['STOPPED'],
        }),
        TextDyField.data_source('Type', 'data.database_version'),
        TextDyField.data_source('Project', 'data.project'),
        ListDyField.data_source('Public IP Address', 'data.ip_addresses', default_badge={'type': 'outline',
                                                                                         'sub_key': 'ip_address',
                                                                                         'delimiter': '<br>'}),
        TextDyField.data_source('Location', 'data.gce_zone'),
        TextDyField.data_source('Data Disk Size (GB)', 'data.settings.data_disk_size_gb'),

        TextDyField.data_source('Connection name', 'data.connection_name', options={'is_optional': True}),
        TextDyField.data_source('Location', 'data.gce_zone', options={'is_optional': True}),
        TextDyField.data_source('Service Account', 'data.service_account_email_address', options={'is_optional': True}),


        TextDyField.data_source('Auto Storage Increased Limit Size (GB)', 'data.settings.storage_auto_resize_limit',
                                options={'is_optional': True}),

    ],
    search=[
        SearchField.set(name='Name', key='data.name'),
        SearchField.set(name='State', key='data.state'),
        SearchField.set(name='Type', key='data.database_version'),
        SearchField.set(name='Project', key='data.project'),
        SearchField.set(name='Region', key='data.region'),
        SearchField.set(name='Zone', key='data.gce_zone'),
        SearchField.set(name='Public IP Address', key='data.ip_addresses.ip_address'),
    ],

    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf))
    ]
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({'resource': cst_instance}),
]
