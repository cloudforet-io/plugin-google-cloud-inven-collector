from schematics.types import ModelType, StringType, PolyModelType

from spaceone.inventory.model.app_engine.version.data import AppEngineVersion
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    TextDyField,
    EnumDyField,
    DateTimeDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
)
from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)

"""
AppEngine Version
"""
app_engine_version = ItemDynamicLayout.set_fields(
    "AppEngine Version",
    fields=[
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("Project ID", "data.project_id"),
        TextDyField.data_source("Service ID", "data.service_id"),
        TextDyField.data_source("Version ID", "data.version_id"),
        EnumDyField.data_source(
            "Serving Status",
            "data.serving_status",
            default_state={
                "safe": ["SERVING"],
                "warning": ["USER_DISABLED"],
                "alert": ["STOPPED"],
            },
        ),
        TextDyField.data_source("Runtime", "data.runtime"),
        TextDyField.data_source("Environment", "data.environment"),
        TextDyField.data_source("Instance Count", "data.instance_count"),
        TextDyField.data_source("Memory Usage", "data.memory_usage"),
        TextDyField.data_source("CPU Usage", "data.cpu_usage"),
        DateTimeDyField.data_source("Created", "data.create_time"),
        DateTimeDyField.data_source("Updated", "data.update_time"),
    ],
)

automatic_scaling = ItemDynamicLayout.set_fields(
    "Automatic Scaling",
    fields=[
        TextDyField.data_source("Cool Down Period", "data.automatic_scaling.coolDownPeriod"),
        TextDyField.data_source("CPU Utilization", "data.automatic_scaling.cpuUtilization"),
        TextDyField.data_source("Max Concurrent Requests", "data.automatic_scaling.maxConcurrentRequests"),
        TextDyField.data_source("Max Idle Instances", "data.automatic_scaling.maxIdleInstances"),
        TextDyField.data_source("Max Total Instances", "data.automatic_scaling.maxTotalInstances"),
        TextDyField.data_source("Min Idle Instances", "data.automatic_scaling.minIdleInstances"),
        TextDyField.data_source("Min Total Instances", "data.automatic_scaling.minTotalInstances"),
    ],
)

manual_scaling = ItemDynamicLayout.set_fields(
    "Manual Scaling",
    fields=[
        TextDyField.data_source("Instances", "data.manual_scaling.instances"),
    ],
)

basic_scaling = ItemDynamicLayout.set_fields(
    "Basic Scaling",
    fields=[
        TextDyField.data_source("Idle Timeout", "data.basic_scaling.idleTimeout"),
        TextDyField.data_source("Max Instances", "data.basic_scaling.maxInstances"),
    ],
)

resources = ItemDynamicLayout.set_fields(
    "Resources",
    fields=[
        TextDyField.data_source("CPU", "data.resources.cpu"),
        TextDyField.data_source("Disk GB", "data.resources.diskGb"),
        TextDyField.data_source("Memory GB", "data.resources.memoryGb"),
        TextDyField.data_source("Volumes", "data.resources.volumes"),
    ],
)

app_engine_version_meta = CloudServiceMeta.set_layouts(
    [app_engine_version, automatic_scaling, manual_scaling, basic_scaling, resources]
)


class AppEngineResource(CloudServiceResource):
    cloud_service_group = StringType(default="AppEngine")


class AppEngineVersionResource(AppEngineResource):
    cloud_service_type = StringType(default="Version")
    data = ModelType(AppEngineVersion)
    _metadata = ModelType(
        CloudServiceMeta, default=app_engine_version_meta, serialized_name="metadata"
    )


class AppEngineVersionResponse(CloudServiceResponse):
    resource = PolyModelType(AppEngineVersionResource)
