from schematics.types import ModelType, StringType, PolyModelType, DictType
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    ListDynamicLayout,
    SimpleTableDynamicLayout,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, MoreField
from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceResource,
    CloudServiceResponse,
    CloudServiceMeta,
)
from spaceone.inventory.model.cloud_functions.function_gen1.data import FunctionGen1

__all__ = ["FunctionResource", "FunctionResponse"]

# detail
general_information = ItemDynamicLayout.set_fields(
    "General Information",
    fields=[
        TextDyField.data_source("Last deployed", "data.display.last_deployed"),
        TextDyField.data_source("Region", "region_code"),
        TextDyField.data_source("Memory allocated", "data.display.memory_allocated"),
        TextDyField.data_source("Timeout", "data.display.timeout"),
        TextDyField.data_source("Minimum instances", "data.min_instances"),
        TextDyField.data_source("Maximum instances", "data.max_instances"),
        TextDyField.data_source("Service account", "data.service_account_email"),
        TextDyField.data_source("Build Worker Pools", "data.build_worker_pool"),
        TextDyField.data_source("Container build log", "data.build_id"),
    ],
)
networking_settings = ItemDynamicLayout.set_fields(
    "Networking Settings",
    fields=[
        TextDyField.data_source("Ingress settings", "data.display.ingress_settings"),
        TextDyField.data_source("VPC connector", "data.vpc_connector"),
        TextDyField.data_source(
            "VPC connector egress", "data.display.vpc_connector_egress_settings"
        ),
    ],
)
function_detail_meta = ListDynamicLayout.set_layouts(
    "Details", layouts=[general_information, networking_settings]
)

# source
source_information = ItemDynamicLayout.set_fields(
    "Information",
    fields=[
        TextDyField.data_source("Runtime", "data.display.runtime"),
        TextDyField.data_source("Entry point", "data.entry_point"),
    ],
)

function_source_meta = ListDynamicLayout.set_layouts(
    "Source", layouts=[source_information]
)

# variables
runtime_environment_variables = SimpleTableDynamicLayout.set_tags(
    "Runtime environment variables",
    root_path="data.display.runtime_environment_variables",
)
build_environment_variables = SimpleTableDynamicLayout.set_tags(
    "Build environment variables", root_path="data.display.build_environment_variables"
)
secrets = SimpleTableDynamicLayout.set_tags(
    "Secrets",
    root_path="data.service_config.secret_environment_variables",
    fields=[
        TextDyField.data_source("key", "key"),
        TextDyField.data_source("project id", "project_id"),
        TextDyField.data_source("secret", "secret"),
        TextDyField.data_source("version", "version"),
    ],
)

function_variables_meta = ListDynamicLayout.set_layouts(
    "Variables",
    layouts=[runtime_environment_variables, build_environment_variables, secrets],
)
# trigger
https = ItemDynamicLayout.set_fields(
    "HTTPS", fields=[TextDyField.data_source("Trigger URL", "data.https_trigger.url")]
)

event = ItemDynamicLayout.set_fields(
    "Event Trigger",
    fields=[
        TextDyField.data_source("Event provider", "data.display.event_provider"),
        TextDyField.data_source("Event type", "data.event_trigger.event_type"),
        TextDyField.data_source("Resource", "data.event_trigger.resource"),
        TextDyField.data_source("Service", "data.event_trigger.service"),
    ],
)

function_trigger_meta = ListDynamicLayout.set_layouts("Trigger", layouts=[https, event])

function_meta = CloudServiceMeta.set_layouts(
    [
        function_detail_meta,
        function_source_meta,
        function_variables_meta,
        function_trigger_meta,
    ]
)


class CloudFunctionsResource(CloudServiceResource):
    tags = DictType(StringType, serialize_when_none=False)
    cloud_service_group = StringType(default="CloudFunctions")


class FunctionResource(CloudFunctionsResource):
    cloud_service_type = StringType(default="Function")
    data = ModelType(FunctionGen1)
    _metadata = ModelType(
        CloudServiceMeta, default=function_meta, serialized_name="metadata"
    )


class FunctionResponse(CloudServiceResponse):
    resource = PolyModelType(FunctionResource)
