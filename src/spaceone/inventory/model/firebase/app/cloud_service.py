from schematics.types import ModelType, PolyModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.model.firebase.app.data import App, firebase_app_meta

"""
Firebase App Cloud Service Resource
"""


class AppResource(CloudServiceResource):
    cloud_service_group = StringType(default="Firebase")
    cloud_service_type = StringType(default="App")
    data = ModelType(App)
    _metadata = ModelType(
        CloudServiceMeta, default=firebase_app_meta, serialized_name="metadata"
    )


class AppResponse(CloudServiceResponse):
    resource = PolyModelType(AppResource)
