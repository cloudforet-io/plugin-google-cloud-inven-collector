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
from spaceone.inventory.model.cloud_run.service_v2.data import Service

"""
Cloud Run Service
"""
# TAB - Service Overview
service_overview = ItemDynamicLayout.set_fields(
    "Service Overview",
    fields=[
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("UID", "data.uid"),
        TextDyField.data_source("Generation", "data.generation"),
        TextDyField.data_source("URI", "data.uri"),
        ListDyField.data_source("URLs", "data.urls"),
        DateTimeDyField.data_source("Create Time", "data.create_time"),
        DateTimeDyField.data_source("Update Time", "data.update_time"),
        DateTimeDyField.data_source("Delete Time", "data.delete_time"),
        DateTimeDyField.data_source("Expire Time", "data.expire_time"),
    ],
)

# TAB - Status & Conditions
service_status = ItemDynamicLayout.set_fields(
    "Status & Conditions",
    fields=[
        TextDyField.data_source(
            "Latest Ready Revision", "data.latest_ready_revision_name"
        ),
        TextDyField.data_source(
            "Latest Created Revision", "data.latest_created_revision_name"
        ),
        TextDyField.data_source("Revision Count", "data.revision_count"),
        TextDyField.data_source("Observed Generation", "data.observed_generation"),
        ListDyField.data_source(
            "Conditions",
            "data.conditions",
            default_badge={
                "type": "outline",
                "sub_key": "type",
                "delimiter": "<br>",
            },
        ),
    ],
)

# TAB - Configuration
service_config = ItemDynamicLayout.set_fields(
    "Configuration",
    fields=[
        TextDyField.data_source("Ingress", "data.ingress"),
        TextDyField.data_source("Launch Stage", "data.launch_stage"),
        ListDyField.data_source(
            "Traffic",
            "data.traffic",
            default_badge={
                "type": "outline",
                "sub_key": "revision",
                "delimiter": "<br>",
            },
        ),
    ],
)

# TAB - Revisions
service_revisions = TableDynamicLayout.set_fields(
    "Revisions",
    fields=[
        TextDyField.data_source("Name", "data.revisions.name"),
        TextDyField.data_source("UID", "data.revisions.uid"),
        TextDyField.data_source("Service", "data.revisions.service"),
        TextDyField.data_source("Generation", "data.revisions.generation"),
        DateTimeDyField.data_source("Create Time", "data.revisions.create_time"),
        DateTimeDyField.data_source("Update Time", "data.revisions.update_time"),
        ListDyField.data_source(
            "Conditions",
            "data.revisions.conditions",
            default_badge={
                "type": "outline",
                "sub_key": "type",
                "delimiter": "<br>",
            },
        ),
    ],
    root_path="data.revisions",
)

cloud_run_service_meta = CloudServiceMeta.set_layouts(
    [
        service_overview,
        service_status,
        service_config,
        service_revisions,
    ]
)


class CloudRunResource(CloudServiceResource):
    cloud_service_group = StringType(default="CloudRun")


class ServiceResource(CloudRunResource):
    cloud_service_type = StringType(default="Service")
    data = ModelType(Service)
    _metadata = ModelType(
        CloudServiceMeta, default=cloud_run_service_meta, serialized_name="metadata"
    )


class ServiceResponse(CloudServiceResponse):
    resource = PolyModelType(ServiceResource)
