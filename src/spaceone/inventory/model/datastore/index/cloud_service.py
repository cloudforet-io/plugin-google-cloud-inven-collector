from schematics.types import ModelType, PolyModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    EnumDyField,
    ListDyField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    TableDynamicLayout,
)
from spaceone.inventory.model.datastore.index.data import DatastoreIndexData

"""
CLOUD SERVICE RESOURCE
"""

# TAB - Index Details
datastore_index_details = ItemDynamicLayout.set_fields(
    "Index Details",
    fields=[
        TextDyField.data_source("Index ID", "data.index_id"),
        TextDyField.data_source("Kind", "data.kind"),
        TextDyField.data_source("Ancestor", "data.ancestor"),
        EnumDyField.data_source(
            "State",
            "data.state",
            default_badge={
                "safe": ["READY", "SERVING"],
                "warning": ["CREATING", "DELETING"],
                "alert": ["ERROR"],
                "disable": ["UNKNOWN"],
            },
        ),
        TextDyField.data_source("Project ID", "data.project_id"),
        TextDyField.data_source("Property Count", "data.property_count"),
    ],
)

# TAB - Properties
datastore_index_properties = TableDynamicLayout.set_fields(
    "Properties",
    root_path="data.properties",
    fields=[
        TextDyField.data_source("Name", "name"),
        EnumDyField.data_source(
            "Direction",
            "direction",
            default_badge={
                "indigo.500": ["ASCENDING"],
                "coral.600": ["DESCENDING"],
            },
        ),
    ],
)

# TAB - Sorted Properties
datastore_index_sorted_properties = ItemDynamicLayout.set_fields(
    "Sorted Properties",
    fields=[
        ListDyField.data_source("Sorted Properties", "data.sorted_properties"),
        ListDyField.data_source("Unsorted Properties", "data.unsorted_properties"),
    ],
)

index_meta = CloudServiceMeta.set_layouts(
    [
        datastore_index_details,
        datastore_index_properties,
        datastore_index_sorted_properties,
    ]
)


class DatastoreIndexResource(CloudServiceResource):
    cloud_service_type = StringType(default="Index")
    cloud_service_group = StringType(default="Datastore")
    data = ModelType(DatastoreIndexData)
    _metadata = ModelType(
        CloudServiceMeta, default=index_meta, serialized_name="metadata"
    )


class DatastoreIndexResponse(CloudServiceResponse):
    resource = PolyModelType(DatastoreIndexResource)
