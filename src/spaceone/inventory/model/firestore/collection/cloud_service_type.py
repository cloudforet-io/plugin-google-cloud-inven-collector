from spaceone.inventory.libs.schema.cloud_service_type import (
    CloudServiceTypeMeta,
    CloudServiceTypeResource,
    CloudServiceTypeResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    SearchField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_widget import (
    CardWidget,
    ChartWidget,
)

ASSET_URL = "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/gcp"

cst_collection = CloudServiceTypeResource()
cst_collection.name = "Collection"
cst_collection.provider = "gcp"
cst_collection.group = "Firestore"
cst_collection.service_code = "Cloud Firestore"
cst_collection.is_primary = False
cst_collection.is_major = True
cst_collection.labels = ["Database", "NoSQL"]
cst_collection.tags = {
    "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/Firestore.svg",
}

cst_collection._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Collection ID", "data.collection_id"),
        TextDyField.data_source("Database ID", "data.database_id"),
        TextDyField.data_source("Project", "data.project_id"),
        TextDyField.data_source("Collection Path", "data.collection_path"),
        TextDyField.data_source("Document Count", "data.document_count"),
        TextDyField.data_source("Depth Level", "data.depth_level"),
        TextDyField.data_source("Parent Document", "data.parent_document_path"),
    ],
    search=[
        SearchField.set(name="Collection ID", key="data.collection_id"),
        SearchField.set(name="Database ID", key="data.database_id"),
        SearchField.set(name="Project", key="data.project_id"),
        SearchField.set(name="Collection Path", key="data.collection_path"),
        SearchField.set(
            name="Document Count", key="data.document_count", data_type="integer"
        ),
        SearchField.set(
            name="Depth Level", key="data.depth_level", data_type="integer"
        ),
    ],
    widget=[
        CardWidget.set(
            **{
                "cloud_service_group": "Firestore",
                "cloud_service_type": "Collection",
                "name": "Total Count",
                "query": {
                    "aggregate": [
                        {"group": {"fields": [{"name": "value", "operator": "count"}]}}
                    ]
                },
                "options": {
                    "value_options": {"key": "value", "options": {"default": 0}}
                },
            }
        ),
        ChartWidget.set(
            **{
                "cloud_service_group": "Firestore",
                "cloud_service_type": "Collection",
                "name": "Collections by Database",
                "query": {
                    "aggregate": [
                        {
                            "group": {
                                "keys": [
                                    {"key": "data.database_id", "name": "database_id"}
                                ],
                                "fields": [
                                    {"name": "collection_count", "operator": "count"}
                                ],
                            }
                        }
                    ]
                },
                "options": {"chart_type": "DONUT"},
            }
        ),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_collection}),
]
