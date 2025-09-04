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
from spaceone.inventory.model.cloud_run.configuration_v1.data import ConfigurationV1

"""
CONFIGURATION V1
"""
configuration_v1_meta = CloudServiceMeta.set_layouts(
    [
        ItemDynamicLayout.set_fields(
            "Configuration V1 Details",
            fields=[
                TextDyField.data_source("Name", "data.name"),
                TextDyField.data_source("Kind", "data.kind"),
                TextDyField.data_source("API Version", "data.api_version"),
                TextDyField.data_source("Namespace", "data.metadata.namespace"),
                TextDyField.data_source("UID", "data.metadata.uid"),
                DateTimeDyField.data_source("Created", "data.metadata.creation_timestamp"),
                TextDyField.data_source("Latest Ready Revision", "data.status.latest_ready_revision_name"),
                TextDyField.data_source("Latest Created Revision", "data.status.latest_created_revision_name"),
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


class ConfigurationV1Resource(CloudServiceResource):
    cloud_service_type = StringType(default="ConfigurationV1")
    cloud_service_group = StringType(default="CloudRun")
    provider = StringType(default="google_cloud")
    data = ModelType(ConfigurationV1)
    _metadata = ModelType(CloudServiceMeta, default=configuration_v1_meta, serialized_name="metadata")


class ConfigurationV1Response(CloudServiceResponse):
    resource = PolyModelType(ConfigurationV1Resource)
