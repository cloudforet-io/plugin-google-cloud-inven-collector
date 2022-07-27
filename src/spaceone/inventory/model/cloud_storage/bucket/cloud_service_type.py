import os

from spaceone.inventory.libs.common_parser import *
from spaceone.inventory.libs.schema.metadata.dynamic_widget import CardWidget, ChartWidget
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, SearchField, DateTimeDyField, EnumDyField, SizeField
from spaceone.inventory.libs.schema.cloud_service_type import CloudServiceTypeResource, CloudServiceTypeResponse, \
    CloudServiceTypeMeta

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, 'widget/total_count.yml')
count_by_region_conf = os.path.join(current_dir, 'widget/count_by_region.yml')
count_by_project_conf = os.path.join(current_dir, 'widget/count_by_project.yml')

cst_bucket = CloudServiceTypeResource()
cst_bucket.name = 'Bucket'
cst_bucket.provider = 'google_cloud'
cst_bucket.group = 'CloudStorage'
cst_bucket.service_code = 'Cloud Storage'
cst_bucket.is_primary = True
cst_bucket.is_major = True
cst_bucket.labels = ['Storage', 'Volume']
cst_bucket.tags = {
    'spaceone:icon': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/Cloud_Storage.svg',
    'spaceone:display_name': 'CloudStorage'
}

cst_bucket._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source('Name', 'data.name'),
        TextDyField.data_source('Location Type', 'data.location.location_type'),
        TextDyField.data_source('Location', 'data.location.location_display'),
        EnumDyField.data_source('Default Storage Class', 'data.default_storage_class',
                                default_outline_badge=['Standard', 'Nearline', 'Coldline', 'Archive']),
        EnumDyField.data_source('Public Access', 'data.public_access', default_state={
            'safe': ['Subject to object ACLs', 'Not public'],
            'warning': ['Not authorized'],
            'alert': ['Public to internet'],
        }),
        TextDyField.data_source('Object Total Counts', 'data.object_count'),
        SizeField.data_source('Object Size', 'data.object_total_size'),
        TextDyField.data_source('Access Control', 'data.access_control'),
        TextDyField.data_source('Lifecycle rules', 'data.lifecycle_rule.lifecycle_rule_display'),
        EnumDyField.data_source('Requester Pays', 'data.requester_pays', default_badge={
            'indigo.500': ['OFF'], 'coral.600': ['ON']
        }),
        TextDyField.data_source('Retention Policy', 'data.retention_policy_display'),
        TextDyField.data_source('Encryption', 'data.encryption'),
        DateTimeDyField.data_source('Creation Time', 'data.creation_timestamp'),

        # is_optional - Default
        TextDyField.data_source('Link URL', 'data.links.link_url', options={
            'is_optional': True
        }),
        TextDyField.data_source('Link for gsutil', 'data.links.gsutil_link', options={
            'is_optional': True
        }),
        TextDyField.data_source('Retention Period', 'data.retention_policy_display', options={
            'is_optional': True
        }),

    ],

    search=[
        SearchField.set(name='ID', key='data.id'),
        SearchField.set(name='Name', key='data.name'),
        SearchField.set(name='Location', key='data.location.location'),
        SearchField.set(name='Object Counts', key='data.object_count', data_type='integer'),
        SearchField.set(name='Object Total Size (Bytes)', key='data.object_total_size', data_type='integer'),
        SearchField.set(name='Creation Time', key='data.creation_timestamp', data_type='datetime'),
        SearchField.set(name='Update Time', key='data.update_timestamp', data_type='datetime'),
    ],

    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf))
    ]
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({'resource': cst_bucket}),
]
