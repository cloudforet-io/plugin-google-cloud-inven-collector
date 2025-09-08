import os

from spaceone.inventory.conf.cloud_service_conf import ASSET_URL
from spaceone.inventory.libs.common_parser import get_data_from_yaml
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

"""
Google Cloud Firestore Collection 서비스 타입을 SpaceONE에서 표현하기 위한 모델을 정의합니다.
"""

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, "widget/total_count.yaml")
count_by_database_conf = os.path.join(current_dir, "widget/count_by_database.yaml")
count_by_project_conf = os.path.join(current_dir, "widget/count_by_project.yaml")

# Cloud Service Type 리소스 정의
cst_collection = CloudServiceTypeResource()
cst_collection.name = "Collection"
cst_collection.provider = "google_cloud"
cst_collection.group = "Firestore"
cst_collection.service_code = "Cloud Firestore"
cst_collection.is_primary = False
cst_collection.is_major = True
cst_collection.labels = ["Database", "NoSQL"]
cst_collection.tags = {
    "spaceone:icon": f"{ASSET_URL}/Firestore.svg",
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
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_database_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_collection}),
]
