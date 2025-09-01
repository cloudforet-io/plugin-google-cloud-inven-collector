from schematics.types import ModelType, StringType, PolyModelType

from spaceone.inventory.model.app_engine.instance.data import AppEngineInstance
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
AppEngine Instance
"""
app_engine_instance = ItemDynamicLayout.set_fields(
    "AppEngine Instance",
    fields=[
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("Project ID", "data.project_id"),
        TextDyField.data_source("Service ID", "data.service_id"),
        TextDyField.data_source("Version ID", "data.version_id"),
        TextDyField.data_source("Instance ID", "data.instance_id"),
        EnumDyField.data_source(
            "VM Status",
            "data.vm_status",
            default_state={
                "safe": ["RUNNING"],
                "warning": ["PENDING", "STAGING"],
                "alert": ["STOPPED", "TERMINATED"],
            },
        ),
        TextDyField.data_source("VM Debug Enabled", "data.vm_debug_enabled"),
        TextDyField.data_source("VM Liveness", "data.vm_liveness"),
        TextDyField.data_source("Request Count", "data.request_count"),
        TextDyField.data_source("Memory Usage", "data.memory_usage"),
        TextDyField.data_source("CPU Usage", "data.cpu_usage"),
        DateTimeDyField.data_source("Created", "data.create_time"),
        DateTimeDyField.data_source("Updated", "data.update_time"),
    ],
)

vm_details = ItemDynamicLayout.set_fields(
    "VM Details",
    fields=[
        TextDyField.data_source("VM Zone Name", "data.vm_details.vmZoneName"),
        TextDyField.data_source("VM ID", "data.vm_details.vmId"),
        TextDyField.data_source("VM IP", "data.vm_details.vmIp"),
        TextDyField.data_source("VM Name", "data.vm_details.vmName"),
    ],
)

availability = ItemDynamicLayout.set_fields(
    "Availability",
    fields=[
        TextDyField.data_source("Liveness", "data.availability.liveness"),
        TextDyField.data_source("Readiness", "data.availability.readiness"),
    ],
)

network = ItemDynamicLayout.set_fields(
    "Network",
    fields=[
        TextDyField.data_source("Forwarded Ports", "data.network.forwardedPorts"),
        TextDyField.data_source("Instance Tag", "data.network.instanceTag"),
        TextDyField.data_source("Network Name", "data.network.name"),
        TextDyField.data_source("Subnetwork Name", "data.network.subnetworkName"),
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

app_engine_instance_meta = CloudServiceMeta.set_layouts(
    [app_engine_instance, vm_details, availability, network, resources]
)


class AppEngineResource(CloudServiceResource):
    cloud_service_group = StringType(default="AppEngine")


class AppEngineInstanceResource(AppEngineResource):
    cloud_service_type = StringType(default="Instance")
    data = ModelType(AppEngineInstance)
    _metadata = ModelType(
        CloudServiceMeta, default=app_engine_instance_meta, serialized_name="metadata"
    )


class AppEngineInstanceResponse(CloudServiceResponse):
    resource = PolyModelType(AppEngineInstanceResource)
