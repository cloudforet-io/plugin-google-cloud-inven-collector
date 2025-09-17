from schematics.types import ModelType, PolyModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    ListDyField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
)
from spaceone.inventory.model.datastore.namespace.data import DatastoreNamespaceData

# TAB - Namespace Details
datastore_namespace_details = ItemDynamicLayout.set_fields(
    "Namespace Details",
    fields=[
        TextDyField.data_source("Namespace ID", "data.namespace_id"),
        TextDyField.data_source("Database ID", "data.database_id"),
        TextDyField.data_source("Kind Count", "data.kind_count"),
    ],
)

# TAB - Kinds
datastore_namespace_kinds = ItemDynamicLayout.set_fields(
    "Kinds",
    fields=[
        ListDyField.data_source(
            "Kind List", "data.kinds", options={"delimiter": "<br>"}
        ),
    ],
)

namespace_meta = CloudServiceMeta.set_layouts(
    [
        datastore_namespace_details,
        datastore_namespace_kinds,
    ]
)


class DatastoreNamespaceResource(CloudServiceResource):
    cloud_service_type = StringType(default="Namespace")
    cloud_service_group = StringType(default="Datastore")
    data = ModelType(DatastoreNamespaceData)
    _metadata = ModelType(
        CloudServiceMeta, default=namespace_meta, serialized_name="metadata"
    )


class DatastoreNamespaceResponse(CloudServiceResponse):
    resource = PolyModelType(DatastoreNamespaceResource)
