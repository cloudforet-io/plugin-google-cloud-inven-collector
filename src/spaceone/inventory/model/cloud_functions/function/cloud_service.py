from schematics.types import ModelType, StringType, PolyModelType, DictType
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, ListDynamicLayout, \
    TableDynamicLayout
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, EnumDyField, DateTimeDyField
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta
from spaceone.inventory.model.cloud_functions.function.data import Function

__all__ = ['FunctionResource', 'FunctionResponse']

# detail
general_information = ItemDynamicLayout.set_fields('General Information', fields=[
    TextDyField.data_source('Last deployed', 'data.display.last_deployed'),
    TextDyField.data_source('Region', 'region_code'),
    TextDyField.data_source('Memory allocated', 'data.display.memory_allocated'),
    TextDyField.data_source('Timeout', 'data.display.timeout'),
    TextDyField.data_source('Minimum instances', 'data.service_config.min_instance_count'),
    TextDyField.data_source('Maximum instances', 'data.service_config.max_instance_count'),
    TextDyField.data_source('Service account', 'data.service_config.service_account_email'),
    TextDyField.data_source('Build Worker Pools', 'data.build_config.worker_pool'),
    TextDyField.data_source('Container build log', 'data.build_config.build'),
])
networking_settings = ItemDynamicLayout.set_fields('Networking Settings', fields=[
    TextDyField.data_source('Ingress settings', 'data.service_config.ingress_settings'),
    TextDyField.data_source('VPC connector', 'data.service_config.vpc_connector'),
    TextDyField.data_source('VPC connector egress', 'data.display.vpc_connector_egress'),
])
function_detail_meta = ListDynamicLayout.set_layouts('Details', layouts=[general_information, networking_settings])

# source
source_information = ItemDynamicLayout.set_fields('', fields=[
    TextDyField.data_source('Runtime', 'data.display.runtime'),
    TextDyField.data_source('Entry point', ''),
    TextDyField.data_source('Source location', ''),
])

# TODO: Need some research on how to get the code
# code = ItemDynamicLayout.set_fields('', fields=[
# ])

function_source_meta = ListDynamicLayout.set_layouts('', layouts=[source_information])

# variables
# it_meta_labels = TableDynamicLayout.set_fields('Labels', root_path='data.labels', fields=[
#     TextDyField.data_source('Key', 'key'),
#     TextDyField.data_source('Value', 'value'),
# ])
runtime_environment_variables = ItemDynamicLayout.set_fields('', fields=[])
build_environment_variables = ItemDynamicLayout.set_fields('', fields=[])
secrets = ItemDynamicLayout.set_fields('', fields=[])
function_variables_meta = ListDynamicLayout.set_layouts('', layouts=[runtime_environment_variables,
                                                                     build_environment_variables, secrets])

# trigger
https = ItemDynamicLayout.set_fields('', fields=[])
eventarc_trigger = ItemDynamicLayout.set_fields('', fields=[])
function_trigger_meta = ListDynamicLayout.set_layouts('', layouts=[https, eventarc_trigger])

function_meta = CloudServiceMeta.set_layouts(
    [function_detail_meta, function_source_meta, function_variables_meta, function_trigger_meta])


class CloudFunctionsResource(CloudServiceResource):
    tags = DictType(StringType, serialize_when_none=False)
    cloud_service_group = StringType(default='CloudFunctions')


class FunctionResource(CloudFunctionsResource):
    cloud_service_type = StringType(default='Function')
    data = ModelType(Function)
    _metadata = ModelType(CloudServiceMeta, default=function_meta, serialized_name='metadata')


class FunctionResponse(CloudServiceResponse):
    resource = PolyModelType(FunctionResource)
