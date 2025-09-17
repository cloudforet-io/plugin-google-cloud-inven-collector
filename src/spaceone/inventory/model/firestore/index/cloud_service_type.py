import os

from spaceone.inventory.conf.cloud_service_conf import ASSET_URL
from spaceone.inventory.libs.common_parser import get_data_from_yaml
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

"""
Google Cloud Firestore Index
"""

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, "widget/total_count.yaml")
count_by_state_conf = os.path.join(current_dir, "widget/count_by_state.yaml")
count_by_query_scope_conf = os.path.join(
    current_dir, "widget/count_by_query_scope.yaml"
)

# Cloud Service Type resource definition
cst_index = CloudServiceTypeResource()
cst_index.name = "Index"
cst_index.provider = "google_cloud"
cst_index.group = "Firestore"
cst_index.service_code = "Cloud Firestore"
cst_index.is_primary = False
cst_index.is_major = False
cst_index.labels = ["Database", "Index"]
cst_index.tags = {
    "spaceone:icon": f"{ASSET_URL}/Firestore.svg",
}

cst_index._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Database ID", "data.database_id"),
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
        SearchField.set(name="Database ID", key="data.database_id"),
        SearchField.set(name="Collection Group", key="data.collection_group"),
        SearchField.set(name="Query Scope", key="data.query_scope"),
        SearchField.set(name="State", key="data.state"),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_state_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_query_scope_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_index}),
]
