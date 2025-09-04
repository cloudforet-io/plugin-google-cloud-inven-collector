from schematics.types import ModelType, PolyModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    DateTimeDyField,
    DictDyField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
)
from spaceone.inventory.model.cloud_run.worker_pool_v1.data import WorkerPoolV1

"""
WORKER POOL V1
"""
worker_pool_v1_meta = CloudServiceMeta.set_layouts(
    [
        ItemDynamicLayout.set_fields(
            "WorkerPool V1 Details",
            fields=[
                TextDyField.data_source("Name", "data.name"),
                TextDyField.data_source("Kind", "data.kind"),
                TextDyField.data_source("API Version", "data.api_version"),
                TextDyField.data_source("Namespace", "data.metadata.namespace"),
                TextDyField.data_source("UID", "data.metadata.uid"),
                DateTimeDyField.data_source("Created", "data.metadata.creation_timestamp"),
            ],
        ),
        ItemDynamicLayout.set_fields(
            "Labels & Annotations",
            fields=[
                DictDyField.data_source("Labels", "data.metadata.labels"),
                DictDyField.data_source("Annotations", "data.metadata.annotations"),
            ],
        ),
    ]
)


class WorkerPoolV1Resource(CloudServiceResource):
    cloud_service_type = StringType(default="WorkerPoolV1")
    cloud_service_group = StringType(default="CloudRun")
    provider = StringType(default="google_cloud")
    data = ModelType(WorkerPoolV1)
    _metadata = ModelType(CloudServiceMeta, default=worker_pool_v1_meta, serialized_name="metadata")


class WorkerPoolV1Response(CloudServiceResponse):
    resource = PolyModelType(WorkerPoolV1Resource)
