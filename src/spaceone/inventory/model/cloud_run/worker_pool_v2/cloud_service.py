from schematics.types import ModelType, PolyModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    DateTimeDyField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
)
from spaceone.inventory.model.cloud_run.worker_pool_v2.data import WorkerPool

"""
Cloud Run Worker Pool
"""
# TAB - Worker Pool
worker_pool_meta = ItemDynamicLayout.set_fields(
    "Worker Pool",
    fields=[
        TextDyField.data_source("Name", "data.metadata.name"),
        TextDyField.data_source("UID", "data.metadata.uid"),
        TextDyField.data_source("Generation", "data.metadata.generation"),
        DateTimeDyField.data_source("Create Time", "data.metadata.create_time"),
        DateTimeDyField.data_source("Update Time", "data.metadata.update_time"),
    ],
)

# TAB - Status
worker_pool_status_meta = ItemDynamicLayout.set_fields(
    "Status",
    fields=[
        TextDyField.data_source("Revision Count", "data.revision_count"),
    ],
)

cloud_run_worker_pool_meta = CloudServiceMeta.set_layouts(
    [
        worker_pool_meta,
        worker_pool_status_meta,
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
