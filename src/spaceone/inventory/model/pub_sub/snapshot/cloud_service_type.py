import os

from spaceone.inventory.libs.common_parser import get_data_from_yaml
from spaceone.inventory.libs.schema.cloud_service_type import *
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, SearchField, DateTimeDyField
from spaceone.inventory.libs.schema.metadata.dynamic_widget import CardWidget, ChartWidget

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, 'widget/total_count.yml')
count_by_region_conf = os.path.join(current_dir, 'widget/count_by_region.yml')
count_by_project_conf = os.path.join(current_dir, 'widget/count_by_project.yml')

cst_pub_sub_snapshot = CloudServiceTypeResource()
cst_pub_sub_snapshot.name = 'Snapshot'
cst_pub_sub_snapshot.provider = 'google_cloud'
cst_pub_sub_snapshot.group = 'Pub/Sub'
cst_pub_sub_snapshot.service_code = 'Cloud Pub/Sub'
cst_pub_sub_snapshot.labels = ['Application Integration']
cst_pub_sub_snapshot.is_primary = True
cst_pub_sub_snapshot.is_major = True
cst_pub_sub_snapshot.tags = {
    'spaceone:icon': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/cloud_pubsub.svg'
}

cst_pub_sub_snapshot._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source('Snapshot ID', 'data.id'),
        TextDyField.data_source('Topic name', 'data.topic'),
        DateTimeDyField.data_source('Expiration', 'data.expire_time'),
        TextDyField.data_source('Project', 'data.project', options={'is_optional': True})
    ],
    search=[
        SearchField.set(name='Snapshot ID', key='data.id'),
        SearchField.set(name='Topic name', key='data.topic'),
        SearchField.set(name='Expiration', key='data.expire_time', data_type='datetime'),
        SearchField.set(name='Project', key='data.project')
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf))
    ]
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({'resource': cst_pub_sub_snapshot}),
]
