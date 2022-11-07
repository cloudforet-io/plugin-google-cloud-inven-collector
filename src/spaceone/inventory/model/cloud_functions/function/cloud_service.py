from schematics.types import ModelType, StringType, PolyModelType, DictType
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, ListDynamicLayout, \
    TableDynamicLayout
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, EnumDyField, DateTimeDyField
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta
from spaceone.inventory.model.cloud_functions.function.data import Function

__all__ = ['FunctionResource', 'FunctionResponse']

function_detail = ItemDynamicLayout.set_fields('', fields=[])

# TODO: write proper words
topic_subscription_meta = TableDynamicLayout.set_fields('', root_path='', fields=[])
topic_snapshot_meta = TableDynamicLayout.set_fields('', root_path='', fields=[])
topic_detail_meta = ListDynamicLayout.set_layouts('', layouts=[function_detail])

function_meta = CloudServiceMeta.set_layouts([topic_detail_meta, topic_subscription_meta, topic_snapshot_meta])


class CloudFunctionsResource(CloudServiceResource):
    tags = DictType(StringType, serialize_when_none=False)
    cloud_service_group = StringType(default='CloudFunctions')


class FunctionResource(CloudFunctionsResource):
    cloud_service_type = StringType(default='Function')
    data = ModelType(Function)
    _metadata = ModelType(CloudServiceMeta, default=function_meta, serialized_name='metadata')


class FunctionResponse(CloudServiceResponse):
    resource = PolyModelType(FunctionResource)
