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
from spaceone.inventory.model.cloud_run.route_v1.data import RouteV1

"""
ROUTE V1
"""
route_v1_meta = CloudServiceMeta.set_layouts(
    [
        ItemDynamicLayout.set_fields(
            "Route V1 Details",
            fields=[
                TextDyField.data_source("Name", "data.name"),
                TextDyField.data_source("Kind", "data.kind"),
                TextDyField.data_source("API Version", "data.api_version"),
                TextDyField.data_source("Namespace", "data.metadata.namespace"),
                TextDyField.data_source("UID", "data.metadata.uid"),
                TextDyField.data_source("URL", "data.status.url"),
                DateTimeDyField.data_source("Created", "data.metadata.creation_timestamp"),
            ],
        ),
        TableDynamicLayout.set_fields(
            "Traffic Configuration",
            "data.spec.traffic",
            fields=[
                TextDyField.data_source("Revision", "revision_name"),
                TextDyField.data_source("Configuration", "configuration_name"),
                TextDyField.data_source("Percent", "percent"),
                TextDyField.data_source("Tag", "tag"),
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


class RouteV1Resource(CloudServiceResource):
    cloud_service_type = StringType(default="RouteV1")
    cloud_service_group = StringType(default="CloudRun")
    provider = StringType(default="google_cloud")
    data = ModelType(RouteV1)
    _metadata = ModelType(CloudServiceMeta, default=route_v1_meta, serialized_name="metadata")


class RouteV1Response(CloudServiceResponse):
    resource = PolyModelType(RouteV1Resource)
