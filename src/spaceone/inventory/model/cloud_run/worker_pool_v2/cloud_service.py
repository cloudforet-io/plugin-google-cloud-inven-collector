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
from spaceone.inventory.model.cloud_run.worker_pool_v2.data import WorkerPool

"""
Cloud Run Worker Pool
"""
# TAB - Worker Pool Overview
worker_pool_meta = ItemDynamicLayout.set_fields(
    "Worker Pool Overview",
    fields=[
        TextDyField.data_source("UID", "data.uid"),
        TextDyField.data_source("Generation", "data.generation"),
        DateTimeDyField.data_source("Create Time", "data.create_time"),
        DateTimeDyField.data_source("Update Time", "data.update_time"),
        TextDyField.data_source("Creator", "data.creator"),
        TextDyField.data_source("Last Modifier", "data.last_modifier"),
    ],
)

# TAB - Status
worker_pool_status_meta = ItemDynamicLayout.set_fields(
    "Status",
    fields=[
        TextDyField.data_source("Revision Count", "data.revision_count"),
    ],
)

# TAB - Revisions
worker_pool_revisions = TableDynamicLayout.set_fields(
    "Revisions",
    "data.revisions",
    fields=[
        TextDyField.data_source("Name", "name"),
        TextDyField.data_source("UID", "uid"),
        TextDyField.data_source("Service", "service"),
        TextDyField.data_source("Generation", "generation"),
        DateTimeDyField.data_source("Create Time", "create_time"),
        DateTimeDyField.data_source("Update Time", "update_time"),
        ListDyField.data_source("Conditions", "conditions", default_badge={
            "type": "outline",
            "sub_key": "type",
            "delimiter": " ",
        }),
    ],
)

cloud_run_worker_pool_meta = CloudServiceMeta.set_layouts(
    [
        worker_pool_meta,
        worker_pool_status_meta,
        worker_pool_revisions,
    ]
)


class CloudRunResource(CloudServiceResource):
    cloud_service_group = StringType(default="CloudRun")


class WorkerPoolResource(CloudRunResource):
    cloud_service_type = StringType(default="WorkerPool")
    data = ModelType(WorkerPool)
    _metadata = ModelType(
        CloudServiceMeta, default=cloud_run_worker_pool_meta, serialized_name="metadata"
    )


class WorkerPoolResponse(CloudServiceResponse):
    resource = PolyModelType(WorkerPoolResource)
