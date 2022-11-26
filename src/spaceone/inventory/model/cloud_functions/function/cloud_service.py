from schematics.types import ModelType, StringType, PolyModelType, DictType
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, ListDynamicLayout, \
    TableDynamicLayout, SimpleTableDynamicLayout
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, MoreField, EnumDyField, DateTimeDyField
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
source_information = ItemDynamicLayout.set_fields('Information', fields=[
    TextDyField.data_source('Runtime', 'data.display.runtime'),
    TextDyField.data_source('Entry point', 'data.build_config.entry_point'),
    TextDyField.data_source('Source location', 'data.display.source_location'),
])

source_code = SimpleTableDynamicLayout.set_source_code_field('Source code', root_path='data.display.source_code')

function_source_meta = ListDynamicLayout.set_layouts('Source', layouts=[source_information, source_code])

# variables
runtime_environment_variables = SimpleTableDynamicLayout.set_tags('Runtime environment variables',
                                                                  root_path='data.display.runtime_environment_variables')
build_environment_variables = SimpleTableDynamicLayout.set_tags('Build environment variables',
                                                                root_path='data.display.build_environment_variables')
secrets = SimpleTableDynamicLayout.set_tags('Secrets', root_path='data.service_config.secret_environment_variables',
                                            fields=[
                                                TextDyField.data_source('key', 'key'),
                                                TextDyField.data_source('project id', 'project_id'),
                                                TextDyField.data_source('secret', 'secret'),
                                                TextDyField.data_source('version', 'version')
                                            ])

function_variables_meta = ListDynamicLayout.set_layouts('Variables', layouts=[runtime_environment_variables,
                                                                              build_environment_variables, secrets])
# trigger
https = ItemDynamicLayout.set_fields('HTTPS', fields=[
    TextDyField.data_source('URL', 'data.service_config.uri')
])
eventarc_trigger = ItemDynamicLayout.set_fields('Eventarc trigger', fields=[
    TextDyField.data_source('Name', 'data.display.trigger_name'),
    TextDyField.data_source('Event provider', 'region_code'),
    TextDyField.data_source('Event type', 'data.event_trigger.event_type'),
    TextDyField.data_source('Receive events from', 'data.event_trigger.pubsub_topic'),
    TextDyField.data_source('Trigger region', 'data.event_trigger.trigger_region'),
    TextDyField.data_source('Service account', 'data.event_trigger.service_account_email'),
    TextDyField.data_source('Retry on failure', 'data.display.retry_policy')
])
function_trigger_meta = ListDynamicLayout.set_layouts('Trigger', layouts=[https, eventarc_trigger])

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
