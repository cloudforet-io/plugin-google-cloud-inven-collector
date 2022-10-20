from schematics.types import ModelType, StringType, PolyModelType, DictType
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, EnumDyField, ListDyField, DateTimeDyField
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta
from spaceone.inventory.model.pub_sub.topic.data import Topic

topic = ItemDynamicLayout.set_fields('Topic', fields=[])

topic_subscription_meta = ItemDynamicLayout.set_fields('Subscriptions', fields=[
    TextDyField.data_source('Subscription ID', 'data.subscription.id'), # TODO: make id field
    TextDyField.data_source('Subscription name', 'data.subscription.name', )
])
topic_snapshot_meta = ItemDynamicLayout.set_fields('Snapshots', root_path='data.snapshots', fields=[

])
topic_detail_meta = ItemDynamicLayout.set_fields('Topic Details', fields=[

])

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
