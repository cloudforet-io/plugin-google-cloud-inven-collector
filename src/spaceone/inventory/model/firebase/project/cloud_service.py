from schematics.types import ModelType, PolyModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.model.firebase.project.data import (
    Project,
    firebase_project_meta,
)

"""
Firebase Project Cloud Service Resource
"""


class ProjectResource(CloudServiceResource):
    cloud_service_group = StringType(default="Firebase")
    cloud_service_type = StringType(default="Project")
    data = ModelType(Project)
    _metadata = ModelType(
        CloudServiceMeta, default=firebase_project_meta, serialized_name="metadata"
    )


class ProjectResponse(CloudServiceResponse):
    resource = PolyModelType(ProjectResource)
