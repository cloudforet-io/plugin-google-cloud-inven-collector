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
Google Cloud Datastore Index 서비스 타입을 SpaceONE에서 표현하기 위한 모델을 정의합니다.
"""

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, "widget/total_count.yml")
count_by_state_conf = os.path.join(current_dir, "widget/count_by_state.yml")
count_by_kind_conf = os.path.join(current_dir, "widget/count_by_kind.yml")

# Cloud Service Type 리소스 정의
cst_index = CloudServiceTypeResource()
cst_index.name = "Index"
cst_index.provider = "google_cloud"
cst_index.group = "Datastore"
cst_index.labels = ["Database", "NoSQL", "Index"]
cst_index.service_code = "Datastore"
cst_index.is_primary = False
cst_index.is_major = True
cst_index.resource_type = "inventory.CloudService"
cst_index.tags = {
    "spaceone:icon": f"{ASSET_URL}/Datastore.svg",
    "spaceone:display_name": "Datastore Index",
}

# 메타데이터 설정
cst_index._metadata = CloudServiceTypeMeta.set_meta(
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
    search=[
        SearchField.set(name="Index ID", key="data.index_id"),
        SearchField.set(name="Kind", key="data.kind"),
        SearchField.set(name="State", key="data.state"),
        SearchField.set(name="Ancestor", key="data.ancestor"),
        SearchField.set(name="Project ID", key="data.project_id"),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_state_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_kind_conf)),
    ],
)

# Cloud Service Type 목록
CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_index}),
]
