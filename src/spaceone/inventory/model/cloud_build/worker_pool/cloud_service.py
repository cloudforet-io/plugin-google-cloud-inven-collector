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
from spaceone.inventory.model.cloud_build.worker_pool.data import WorkerPool

"""
Cloud Build Worker Pool
"""
# TAB - Worker Pool Overview
worker_pool_overview = ItemDynamicLayout.set_fields(
    "Worker Pool Overview",
    fields=[
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("Display Name", "data.display_name"),
        TextDyField.data_source("UID", "data.uid"),
        TextDyField.data_source("State", "data.state"),
        TextDyField.data_source("ETag", "data.etag"),
        DateTimeDyField.data_source("Create Time", "data.create_time"),
        DateTimeDyField.data_source("Update Time", "data.update_time"),
        DateTimeDyField.data_source("Delete Time", "data.delete_time"),
    ],
)

cloud_build_worker_pool_meta = CloudServiceMeta.set_layouts(
    [
        worker_pool_overview,
    ]
)


class CloudBuildResource(CloudServiceResource):
    cloud_service_group = StringType(default="CloudBuild")


class WorkerPoolResource(CloudBuildResource):
    cloud_service_type = StringType(default="WorkerPool")
    data = ModelType(WorkerPool)
    _metadata = ModelType(
        CloudServiceMeta,
        default=cloud_build_worker_pool_meta,
        serialized_name="metadata",
    )


class WorkerPoolResponse(CloudServiceResponse):
    resource = PolyModelType(WorkerPoolResource)
