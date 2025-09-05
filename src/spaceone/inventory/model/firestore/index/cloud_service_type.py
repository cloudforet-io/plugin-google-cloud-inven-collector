from spaceone.inventory.libs.schema.cloud_service_type import (
    CloudServiceTypeMeta,
    CloudServiceTypeResource,
    CloudServiceTypeResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    EnumDyField,
    SearchField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_widget import (
    CardWidget,
    ChartWidget,
)

ASSET_URL = "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/gcp"

cst_index = CloudServiceTypeResource()
cst_index.name = "Index"
cst_index.provider = "gcp"
cst_index.group = "Firestore"
cst_index.service_code = "Cloud Firestore"
cst_index.is_primary = False
cst_index.is_major = True
cst_index.labels = ["Database", "Index"]
cst_index.tags = {
    "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/Firestore.svg",
}

cst_index._metadata = CloudServiceTypeMeta.set_meta(
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
            "State",
            "data.state",
            default_badge={
                "indigo.500": ["READY"],
                "yellow.500": ["CREATING"],
                "red.500": ["ERROR"],
            },
        ),
    ],
    search=[
        SearchField.set(name="Index Name", key="data.name"),
        SearchField.set(name="Database ID", key="data.database_id"),
        SearchField.set(name="Project", key="data.project_id"),
        SearchField.set(name="Collection Group", key="data.collection_group"),
        SearchField.set(name="Query Scope", key="data.query_scope"),
        SearchField.set(name="State", key="data.state"),
    ],
    widget=[
        CardWidget.set(
            **{
                "cloud_service_group": "Firestore",
                "cloud_service_type": "Index",
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
                "cloud_service_type": "Index",
                "name": "Indexes by State",
                "query": {
                    "aggregate": [
                        {
                            "group": {
                                "keys": [{"key": "data.state", "name": "state"}],
                                "fields": [
                                    {"name": "index_count", "operator": "count"}
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
    CloudServiceTypeResponse({"resource": cst_index}),
]
