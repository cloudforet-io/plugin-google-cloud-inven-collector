from schematics.types import ModelType, StringType, PolyModelType

from spaceone.inventory.model.app_engine.service.data import AppEngineService
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
AppEngine Service
"""
app_engine_service = ItemDynamicLayout.set_fields(
    "AppEngine Service",
    fields=[
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("Project ID", "data.project_id"),
        TextDyField.data_source("Service ID", "data.service_id"),
        EnumDyField.data_source(
            "Serving Status",
            "data.serving_status",
            default_state={
                "safe": ["SERVING"],
                "warning": ["USER_DISABLED"],
                "alert": ["STOPPED"],
            },
        ),
        TextDyField.data_source("Split", "data.split"),
        TextDyField.data_source("Version Count", "data.version_count"),
        TextDyField.data_source("Instance Count", "data.instance_count"),
        DateTimeDyField.data_source("Created", "data.create_time"),
        DateTimeDyField.data_source("Updated", "data.update_time"),
    ],
)

traffic_split = ItemDynamicLayout.set_fields(
    "Traffic Split",
    fields=[
        TextDyField.data_source("Allocations", "data.split.allocations"),
        TextDyField.data_source("Shard By", "data.split.shardBy"),
    ],
)

network_settings = ItemDynamicLayout.set_fields(
    "Network Settings",
    fields=[
        TextDyField.data_source("Forwarded Ports", "data.network.forwardedPorts"),
        TextDyField.data_source("Instance Tag", "data.network.instanceTag"),
        TextDyField.data_source("Network Name", "data.network.name"),
        TextDyField.data_source("Subnetwork Name", "data.network.subnetworkName"),
    ],
)

app_engine_service_meta = CloudServiceMeta.set_layouts(
    [app_engine_service, traffic_split, network_settings]
)


class AppEngineResource(CloudServiceResource):
    cloud_service_group = StringType(default="AppEngine")


class AppEngineServiceResource(AppEngineResource):
    cloud_service_type = StringType(default="Service")
    data = ModelType(AppEngineService)
    _metadata = ModelType(
        CloudServiceMeta, default=app_engine_service_meta, serialized_name="metadata"
    )


class AppEngineServiceResponse(CloudServiceResponse):
    resource = PolyModelType(AppEngineServiceResource)
