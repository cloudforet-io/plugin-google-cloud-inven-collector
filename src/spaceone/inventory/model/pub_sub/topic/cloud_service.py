from schematics.types import ModelType, StringType, PolyModelType, DictType
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta
from spaceone.inventory.model.pub_sub.topic.data import Topic

topic = ItemDynamicLayout.set_fields('Topic', fields=[])
topic_meta = CloudServiceMeta.set_layouts([])


class PubSubResource(CloudServiceResource):
    tags = DictType(StringType, serialize_when_none=False)
    cloud_service_group = StringType(default='Pub/Sub')


class TopicResource(PubSubResource):
    cloud_service_type = StringType(default='Topic')
    data = ModelType(Topic)
    _metadata = ModelType(CloudServiceMeta, default=topic_meta, serialized_name='metadata')


class TopicResponse(CloudServiceResponse):
    resource = PolyModelType(TopicResource)
