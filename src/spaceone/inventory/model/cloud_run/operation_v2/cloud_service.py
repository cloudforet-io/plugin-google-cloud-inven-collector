from schematics.types import PolyModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    DateTimeDyField,
    EnumDyField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    TableDynamicLayout,
)

"""
Cloud Run Operation V2
"""
# TAB - Operation Overview
operation_overview = ItemDynamicLayout.set_fields(
    "Operation Overview",
    fields=[
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("Status", "data.status"),
        EnumDyField.data_source(
            "Done",
            "data.done",
            default_badge={
                "indigo.500": ["true"],
                "coral.600": ["false"],
            },
        ),
        TextDyField.data_source("Operation Type", "data.operation_type"),
        TextDyField.data_source("Target Resource", "data.target_resource"),
        TextDyField.data_source("Progress (%)", "data.progress"),
        DateTimeDyField.data_source("Create Time", "data.create_time"),
        DateTimeDyField.data_source("End Time", "data.end_time"),
        TextDyField.data_source("Project", "data.project"),
        TextDyField.data_source("Location", "data.location"),
        TextDyField.data_source("Region", "data.region"),
    ],
)

# TAB - Metadata
metadata_table = TableDynamicLayout.set_fields(
    "Metadata",
    root_path="data.metadata",
    fields=[
        TextDyField.data_source("Key", "key"),
        TextDyField.data_source("Value", "value"),
    ],
)

# TAB - Labels
labels_table = TableDynamicLayout.set_fields(
    "Labels", 
    root_path="data.labels",
    fields=[
        TextDyField.data_source("Key", "key"),
        TextDyField.data_source("Value", "value"),
    ],
)

operation_meta = CloudServiceMeta.set_layouts(
    [operation_overview, metadata_table, labels_table]
)


class OperationResource(CloudServiceResource):
    cloud_service_type = StringType(default="Operation")


class OperationResponse(CloudServiceResponse):
    resource = PolyModelType(OperationResource)
