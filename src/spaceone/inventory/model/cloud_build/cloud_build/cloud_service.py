from schematics.types import ModelType, PolyModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    DateTimeDyField,
    ListDyField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    TableDynamicLayout,
)
from spaceone.inventory.model.cloud_build.cloud_build.data import Build

"""
Cloud Build Build
"""
# TAB - Build Overview
build_overview = ItemDynamicLayout.set_fields(
    "Build Overview",
    fields=[
        TextDyField.data_source("ID", "data.id"),
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("Status", "data.status"),
        TextDyField.data_source("Build Trigger ID", "data.build_trigger_id"),
        TextDyField.data_source("Service Account", "data.service_account"),
        TextDyField.data_source("Log URL", "data.log_url"),
        TextDyField.data_source("Logs Bucket", "data.logs_bucket"),
        TextDyField.data_source("Timeout", "data.timeout"),
        DateTimeDyField.data_source("Create Time", "data.create_time"),
        DateTimeDyField.data_source("Start Time", "data.start_time"),
        DateTimeDyField.data_source("Finish Time", "data.finish_time"),
    ],
)

# TAB - Build Configuration
build_config = ItemDynamicLayout.set_fields(
    "Build Configuration",
    fields=[
        ListDyField.data_source("Images", "data.images"),
        ListDyField.data_source("Tags", "data.tags"),
    ],
)

# TAB - Build Steps
build_steps = TableDynamicLayout.set_fields(
    "Build Steps",
    fields=[
        TextDyField.data_source("Name", "data.steps.name"),
        TextDyField.data_source("Args", "data.steps.args"),
        TextDyField.data_source("Env", "data.steps.env"),
        TextDyField.data_source("Dir", "data.steps.dir"),
        TextDyField.data_source("ID", "data.steps.id"),
        TextDyField.data_source("Wait For", "data.steps.waitFor"),
        TextDyField.data_source("Entrypoint", "data.steps.entrypoint"),
        TextDyField.data_source("Secret Env", "data.steps.secretEnv"),
        TextDyField.data_source("Volumes", "data.steps.volumes"),
        TextDyField.data_source("Timeout", "data.steps.timeout"),
        TextDyField.data_source("Status", "data.steps.status"),
    ],
    root_path="data.steps",
)

cloud_build_build_meta = CloudServiceMeta.set_layouts(
    [
        build_overview,
        build_config,
        build_steps,
    ]
)


class CloudBuildResource(CloudServiceResource):
    cloud_service_group = StringType(default="CloudBuild")


class BuildResource(CloudBuildResource):
    cloud_service_type = StringType(default="Build")
    data = ModelType(Build)
    _metadata = ModelType(
        CloudServiceMeta, default=cloud_build_build_meta, serialized_name="metadata"
    )


class BuildResponse(CloudServiceResponse):
    resource = PolyModelType(BuildResource)
