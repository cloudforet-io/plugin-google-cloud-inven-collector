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
    TableDynamicLayout,
)
from spaceone.inventory.model.cloud_run.job_v1.data import JobV1

"""
JOB V1
"""
job_v1_meta = CloudServiceMeta.set_layouts(
    [
        ItemDynamicLayout.set_fields(
            "Job V1 Details",
            fields=[
                TextDyField.data_source("Name", "data.name"),
                TextDyField.data_source("Kind", "data.kind"),
                TextDyField.data_source("API Version", "data.api_version"),
                TextDyField.data_source("Namespace", "data.metadata.namespace"),
                TextDyField.data_source("UID", "data.metadata.uid"),
                TextDyField.data_source("Execution Count", "data.execution_count"),
                DateTimeDyField.data_source("Created", "data.metadata.creation_timestamp"),
            ],
        ),
        TableDynamicLayout.set_fields(
            "Executions",
            "data.executions",
            fields=[
                TextDyField.data_source("Name", "metadata.name"),
                TextDyField.data_source("Status", "status.conditions[0].status"),
                DateTimeDyField.data_source("Created", "metadata.creationTimestamp"),
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


class JobV1Resource(CloudServiceResource):
    cloud_service_type = StringType(default="JobV1")
    cloud_service_group = StringType(default="CloudRun")
    provider = StringType(default="google_cloud")
    data = ModelType(JobV1)
    _metadata = ModelType(CloudServiceMeta, default=job_v1_meta, serialized_name="metadata")


class JobV1Response(CloudServiceResponse):
    resource = PolyModelType(JobV1Resource)
