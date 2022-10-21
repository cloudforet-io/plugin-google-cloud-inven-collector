from schematics.types import ModelType, StringType, PolyModelType, DictType
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, ListDynamicLayout, \
    TableDynamicLayout
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, EnumDyField, DateTimeDyField
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta
from spaceone.inventory.model.pub_sub.topic.data import Topic

topic = ItemDynamicLayout.set_fields('Topic', fields=[])

topic_subscription_meta = TableDynamicLayout.set_fields('Subscriptions', root_path='data.subscription', fields=[
    TextDyField.data_source('Subscription ID', 'id'),
    EnumDyField.data_source('State', 'state', default_state={
        'safe': ['ACTIVE'],
        'alert': ['RESOURCE_ERROR']
    }),
    EnumDyField.data_source('Delivery type', 'delivery_type', default_badge={
        'primary': ['Push'], 'indigo.500': ['Pull'], 'coral.600': ['BigQuery']}),
    TextDyField.data_source('Subscription name', 'name'),
])
topic_snapshot_meta = TableDynamicLayout.set_fields('Snapshots', root_path='data.snapshots', fields=[
    TextDyField.data_source('Snapshot ID', 'id'),
    TextDyField.data_source('Snapshot name', 'name'),
    DateTimeDyField.data_source('Expire time', 'expire_time'),
    TextDyField.data_source('Topic', 'topic')
])
topic_detail = ItemDynamicLayout.set_fields('Topic Details', fields=[
    TextDyField.data_source('Name', 'name'),
    TextDyField.data_source('Project', 'data.project'),
    TextDyField.data_source('Encryption key', 'data.encryption_key'),
    TextDyField.data_source('Schema name', 'data.schema_settings.schema'),
    TextDyField.data_source('Message encoding', 'data.schema_settings.encoding'),
    TextDyField.data_source('Subscription count', 'data.display.subscription_count'),
    TextDyField.data_source('Reduction duration', 'data.display.retention')

])

topic_detail_meta = ListDynamicLayout.set_layouts('Details', layouts=[topic_detail])
topic_meta = CloudServiceMeta.set_layouts([topic_subscription_meta, topic_snapshot_meta, topic_detail_meta])


class PubSubResource(CloudServiceResource):
    tags = DictType(StringType, serialize_when_none=False)
    cloud_service_group = StringType(default='Pub/Sub')


class TopicResource(PubSubResource):
    cloud_service_type = StringType(default='Topic')
    data = ModelType(Topic)
    _metadata = ModelType(CloudServiceMeta, default=topic_meta, serialized_name='metadata')


class TopicResponse(CloudServiceResponse):
    resource = PolyModelType(TopicResource)
