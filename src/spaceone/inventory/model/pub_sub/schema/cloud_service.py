from schematics.types import ModelType, StringType, PolyModelType
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta
from spaceone.inventory.model.pub_sub.schema.data import PubSubSchema

pub_sub_schema = ItemDynamicLayout.set_fields('Schema', fields=[])
pub_sub_schema_meta = CloudServiceMeta.set_layouts([])


class PubSubResource(CloudServiceResource):
    cloud_service_group = StringType(default='PubSub')


class PubSubSchemaResource(PubSubResource):
    cloud_service_type = StringType(default='Schema')
    data = ModelType(PubSubSchema)
    _metadata = ModelType(CloudServiceMeta, default=pub_sub_schema_meta, serialized_name='metadata')


class PubSubSchemaResponse(CloudServiceResponse):
    resource = PolyModelType(PubSubSchemaResource)
