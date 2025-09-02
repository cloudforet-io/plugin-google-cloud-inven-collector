from schematics.types import ModelType, PolyModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    EnumDyField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout
from spaceone.inventory.model.firestore.index.data import FirestoreIndex

"""
INDEX
"""
index_meta = CloudServiceMeta.set_layouts(
    [
        ItemDynamicLayout.set_fields(
            "Index",
            fields=[
                TextDyField.data_source("Index Name", "data.name"),
                TextDyField.data_source("Database ID", "data.database_id"),
                TextDyField.data_source("Project", "data.project_id"),
                TextDyField.data_source("Collection Group", "data.collection_group"),
                EnumDyField.data_source(
                    "Query Scope",
                    "data.query_scope",
                    default_badge={
                        "indigo.500": ["COLLECTION"],
                        "coral.600": ["COLLECTION_GROUP"],
                    },
                ),
                EnumDyField.data_source(
                    "API Scope",
                    "data.api_scope",
                    default_badge={
                        "indigo.500": ["ANY_API"],
                        "coral.600": ["DATASTORE_MODE_API"],
                    },
                ),
                EnumDyField.data_source(
                    "State",
                    "data.state",
                    default_badge={
                        "indigo.500": ["READY"],
                        "yellow.500": ["CREATING"],
                        "red.500": ["ERROR"],
                    },
                ),
                TextDyField.data_source("Fields Summary", "data.fields_summary"),
            ],
        ),
    ]
)


class IndexResource(CloudServiceResource):
    cloud_service_group = StringType(default="Firestore")
    cloud_service_type = StringType(default="Index")
    data = ModelType(FirestoreIndex)
    _metadata = ModelType(
        CloudServiceMeta, default=index_meta, serialized_name="metadata"
    )


class IndexResponse(CloudServiceResponse):
    resource = PolyModelType(IndexResource)
