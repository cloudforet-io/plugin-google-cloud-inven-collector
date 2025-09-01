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
from spaceone.inventory.model.cloud_build.repository.data import Repository

"""
Cloud Build Repository
"""
# TAB - Repository Overview
repository_overview = ItemDynamicLayout.set_fields(
    "Repository Overview",
    fields=[
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("Remote URI", "data.remote_uri"),
        TextDyField.data_source("UID", "data.uid"),
        TextDyField.data_source("Webhook ID", "data.webhook_id"),
        TextDyField.data_source("ETag", "data.etag"),
        DateTimeDyField.data_source("Create Time", "data.create_time"),
        DateTimeDyField.data_source("Update Time", "data.update_time"),
    ],
)

cloud_build_repository_meta = CloudServiceMeta.set_layouts(
    [
        repository_overview,
    ]
)


class CloudBuildResource(CloudServiceResource):
    cloud_service_group = StringType(default="CloudBuild")


class RepositoryResource(CloudBuildResource):
    cloud_service_type = StringType(default="Repository")
    data = ModelType(Repository)
    _metadata = ModelType(
        CloudServiceMeta,
        default=cloud_build_repository_meta,
        serialized_name="metadata",
    )


class RepositoryResponse(CloudServiceResponse):
    resource = PolyModelType(RepositoryResource)
