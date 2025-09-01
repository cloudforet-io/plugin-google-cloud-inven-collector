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
from spaceone.inventory.model.cloud_build.connection.data import Connection

"""
Cloud Build Connection
"""
# TAB - Connection Overview
connection_overview = ItemDynamicLayout.set_fields(
    "Connection Overview",
    fields=[
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("UID", "data.uid"),
        TextDyField.data_source("Disabled", "data.disabled"),
        TextDyField.data_source("Reconciling", "data.reconciling"),
        TextDyField.data_source("ETag", "data.etag"),
        DateTimeDyField.data_source("Create Time", "data.create_time"),
        DateTimeDyField.data_source("Update Time", "data.update_time"),
    ],
)

cloud_build_connection_meta = CloudServiceMeta.set_layouts(
    [
        connection_overview,
    ]
)


class CloudBuildResource(CloudServiceResource):
    cloud_service_group = StringType(default="CloudBuild")


class ConnectionResource(CloudBuildResource):
    cloud_service_type = StringType(default="Connection")
    data = ModelType(Connection)
    _metadata = ModelType(
        CloudServiceMeta,
        default=cloud_build_connection_meta,
        serialized_name="metadata",
    )


class ConnectionResponse(CloudServiceResponse):
    resource = PolyModelType(ConnectionResource)
