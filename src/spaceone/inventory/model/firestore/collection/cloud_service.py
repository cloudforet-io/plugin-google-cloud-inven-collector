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
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout
from spaceone.inventory.model.firestore.collection.data import FirestoreCollection

"""
COLLECTION
"""
collection_meta = CloudServiceMeta.set_layouts(
    [
        ItemDynamicLayout.set_fields(
            "Collection",
            fields=[
                TextDyField.data_source("Collection ID", "data.collection_id"),
                TextDyField.data_source("Database ID", "data.database_id"),
                TextDyField.data_source("Project", "data.project_id"),
                TextDyField.data_source("Collection Path", "data.collection_path"),
                TextDyField.data_source("Document Count", "data.document_count"),
                TextDyField.data_source("Depth Level", "data.depth_level"),
                TextDyField.data_source("Parent Document", "data.parent_document_path"),
            ],
        ),
        ItemDynamicLayout.set_fields(
            "Documents",
            fields=[
                ListDyField.data_source(
                    "Documents",
                    "data.documents",
                    default_layout={
                        "type": "table",
                        "options": {
                            "fields": [
                                {"key": "id", "name": "Document ID"},
                                {"key": "create_time", "name": "Created"},
                                {"key": "update_time", "name": "Updated"},
                                {"key": "fields_summary", "name": "Fields Summary"},
                            ]
                        },
                    },
                ),
            ],
        ),
    ]
)


class CollectionResource(CloudServiceResource):
    cloud_service_group = StringType(default="Firestore")
    cloud_service_type = StringType(default="Collection")
    data = ModelType(FirestoreCollection)
    _metadata = ModelType(
        CloudServiceMeta, default=collection_meta, serialized_name="metadata"
    )


class CollectionResponse(CloudServiceResponse):
    resource = PolyModelType(CollectionResource)
