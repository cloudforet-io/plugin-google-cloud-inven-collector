from schematics.types import PolyModelType

from spaceone.inventory.model.bigquery.sql_workspace.data import *
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    TextDyField,
    DateTimeDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    TableDynamicLayout,
    ListDynamicLayout,
    SimpleTableDynamicLayout,
)
from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceResource,
    CloudServiceResponse,
    CloudServiceMeta,
)

"""
SQL Workspace
"""

# TAB - Bucket
dataset_details_meta = ItemDynamicLayout.set_fields(
    "Information",
    fields=[
        TextDyField.data_source("ID", "data.id"),
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("Location", "data.location"),
        TextDyField.data_source(
            "Default Partition Expires", "data.default_partition_expiration_ms_display"
        ),
        TextDyField.data_source(
            "Default Table Expires", "data.default_table_expiration_ms_display"
        ),
        DateTimeDyField.data_source("Creation Time", "data.creation_time"),
        DateTimeDyField.data_source("Last Modified Time", "data.last_modified_time"),
    ],
)

access_table_meta = SimpleTableDynamicLayout.set_fields(
    "Access",
    root_path="data.access",
    fields=[
        TextDyField.data_source("Role", "role"),
        TextDyField.data_source("Special Group", "special_group"),
        TextDyField.data_source("User by E-mail", "user_by_email"),
    ],
)

workspace_dataset_meta = ListDynamicLayout.set_layouts(
    "Dataset Details", layouts=[dataset_details_meta, access_table_meta]
)


workspace_labels_meta = TableDynamicLayout.set_fields(
    "Labels",
    root_path="data.labels",
    fields=[
        TextDyField.data_source("Key", "key"),
        TextDyField.data_source("Value", "value"),
    ],
)

big_query_workspace_meta = CloudServiceMeta.set_layouts(
    [
        workspace_dataset_meta,
        workspace_labels_meta,
    ]
)


class BigQueryGroupResource(CloudServiceResource):
    cloud_service_group = StringType(default="BigQuery")


class SQLWorkSpaceResource(BigQueryGroupResource):
    cloud_service_type = StringType(default="SQLWorkspace")
    data = ModelType(BigQueryWorkSpace)
    _metadata = ModelType(
        CloudServiceMeta, default=big_query_workspace_meta, serialized_name="metadata"
    )


class SQLWorkSpaceResponse(CloudServiceResponse):
    resource = PolyModelType(SQLWorkSpaceResource)
