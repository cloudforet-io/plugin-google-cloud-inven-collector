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

cst_topic = CloudServiceTypeResource()
cst_topic.name = 'Topic'
cst_topic.provider = 'google_cloud'
cst_topic.group = 'Pub/Sub'
cst_topic.service_code = 'Cloud Pub/Sub'
cst_topic.labels = ['Application Integration']
cst_topic.is_primary = True
cst_topic.is_major = True
cst_topic.tags = {
    'spaceone:icon': f'{ASSET_URL}/cloud_pubsub.svg'
}

cst_topic._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        EnumDyField.data_source('Encryption key', 'data.display.encryption_key',
                                default_badge={'primary': ['Google managed'], 'indigo.500': ['Customer managed']}),
        TextDyField.data_source('Topic ID', 'data.topic_id'),
        TextDyField.data_source('Retention', 'data.display.retention'),
        TextDyField.data_source('Subscription count', 'data.display.subscription_count'),
        TextDyField.data_source('Project', 'data.project'),
        TextDyField.data_source('Schema name', 'data.schema_settings.schema', options={'is_optional': True}),
        TextDyField.data_source('Message encoding', 'data.schema_settings.encoding', options={'is_optional': True})
    ],
    search=[
        SearchField.set(name='Topic ID', key='data.topic_id'),
        SearchField.set(name='Encryption key', key='data.display.encryption_key'),
        SearchField.set(name='Topic name', key='data.name'),
        SearchField.set(name='Retention', key='data.display.retention'),
        SearchField.set(name='Project', key='data.project'),
        SearchField.set(name='Schema name', key='data.schema_settings.schema'),
        SearchField.set(name='Message encoding', key='data.schema_settings.encoding'),
        SearchField.set(name='Subscription count', key='data.display.subscription_count', data_type='integer')
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf))
    ]
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({'resource': cst_topic}),
]
