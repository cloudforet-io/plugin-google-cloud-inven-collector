import os

from spaceone.inventory.libs.common_parser import get_data_from_yaml
from spaceone.inventory.libs.schema.cloud_service_type import *
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, SearchField, EnumDyField
from spaceone.inventory.libs.schema.metadata.dynamic_widget import CardWidget, ChartWidget

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, 'widget/total_count.yml')
count_by_region_conf = os.path.join(current_dir, 'widget/count_by_region.yml')
count_by_project_conf = os.path.join(current_dir, 'widget/count_by_project.yml')

cst_schema = CloudServiceTypeResource()
cst_schema.name = 'Schema'
cst_schema.provider = 'google_cloud'
cst_schema.group = 'Pub/Sub'
cst_schema.service_code = 'Cloud Pub/Sub'
cst_schema.labels = ['Application Integration']
cst_schema.is_primary = True
cst_schema.is_major = True
cst_schema.tags = {
    'spaceone:icon': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/cloud_pubsub.svg'
}

cst_schema._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source('Schema ID', 'data.id'),
        EnumDyField.data_source('Schema type', 'data.schema_type',
                                default_outline_badge=['AVRO', 'PROTOCOL_BUFFER', 'TYPE_UNSPECIFIED']),
        TextDyField.data_source('Project', 'data.project'),
    ],
    search=[
        SearchField.set(name='Schema ID', key='data.id'),
        SearchField.set(name='Schema type', key='data.schema_type'),
        SearchField.set(name='Project', key='data.project')
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf))
    ]
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({'resource': cst_schema}),
]
