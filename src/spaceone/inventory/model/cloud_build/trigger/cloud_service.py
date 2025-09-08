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
from spaceone.inventory.model.cloud_build.trigger.data import Trigger

"""
Cloud Build Trigger
"""
# TAB - Trigger Overview
trigger_overview = ItemDynamicLayout.set_fields(
    "Trigger Overview",
    fields=[
        TextDyField.data_source("ID", "data.id"),
        TextDyField.data_source("Disabled", "data.disabled"),
        TextDyField.data_source("Service Account", "data.service_account"),
        TextDyField.data_source("Autodetect", "data.autodetect"),
        DateTimeDyField.data_source("Create Time", "data.create_time"),
    ],
)

cloud_build_trigger_meta = CloudServiceMeta.set_layouts(
    [
        trigger_overview,
    ]
)


class CloudBuildResource(CloudServiceResource):
    cloud_service_group = StringType(default="CloudBuild")


class TriggerResource(CloudBuildResource):
    cloud_service_type = StringType(default="Trigger")
    data = ModelType(Trigger)
    _metadata = ModelType(
        CloudServiceMeta, default=cloud_build_trigger_meta, serialized_name="metadata"
    )


class TriggerResponse(CloudServiceResponse):
    resource = PolyModelType(TriggerResource)
