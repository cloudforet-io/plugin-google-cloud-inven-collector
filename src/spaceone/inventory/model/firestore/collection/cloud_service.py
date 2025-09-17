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
    TableDynamicLayout,
)
from spaceone.inventory.model.firestore.collection.data import FirestoreCollection

# TAB - Collection Details
firestore_collection_details = ItemDynamicLayout.set_fields(
    "Collection Details",
    fields=[
        TextDyField.data_source("Collection ID(Name)", "data.name"),
        TextDyField.data_source("Database ID", "data.database_id"),
        TextDyField.data_source("Collection Path", "data.collection_path"),
        TextDyField.data_source("Document Count", "data.document_count"),
        TextDyField.data_source("Depth Level", "data.depth_level"),
        TextDyField.data_source("Parent Document", "data.parent_document_path"),
    ],
)

# TAB - Documents
firestore_collection_documents = TableDynamicLayout.set_fields(
    "Documents",
    root_path="data.documents",
    fields=[
        TextDyField.data_source("Document ID", "document_id"),
        TextDyField.data_source("Full Name", "document_name"),
        TextDyField.data_source("Fields Summary", "fields_summary"),
        DateTimeDyField.data_source("Created", "create_time"),
        DateTimeDyField.data_source("Updated", "update_time"),
    ],
)

# Unified metadata layout
firestore_collection_meta = CloudServiceMeta.set_layouts(
    [
        firestore_collection_details,
        firestore_collection_documents,
    ]
)


class FirestoreResource(CloudServiceResource):
    cloud_service_group = StringType(default="Firestore")


class CollectionResource(FirestoreResource):
    cloud_service_type = StringType(default="Collection")
    data = ModelType(FirestoreCollection)
    _metadata = ModelType(
        CloudServiceMeta, default=firestore_collection_meta, serialized_name="metadata"
    )


class CollectionResponse(CloudServiceResponse):
    resource = PolyModelType(CollectionResource)
