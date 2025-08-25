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

"""
Datastore Index Cloud Service Type 정의

Google Cloud Datastore Index 서비스 타입을 SpaceONE에서 표현하기 위한 모델을 정의합니다.
"""

# Cloud Service Type 리소스 정의
cst_index = CloudServiceTypeResource()
cst_index.name = "Index"
cst_index.provider = "google_cloud"
cst_index.group = "Datastore"
cst_index.labels = ["Database", "NoSQL", "Index"]
cst_index.service_code = "Cloud Datastore"
cst_index.is_primary = False
cst_index.is_major = True
cst_index.resource_type = "inventory.CloudService"
cst_index.tags = {
    "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/Cloud_Datastore.svg",
    "spaceone:display_name": "Datastore Index",
}

# 메타데이터 설정
cst_index_meta = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Index ID", "data.indexId"),
        TextDyField.data_source("Kind", "data.kind"),
        TextDyField.data_source("Ancestor", "data.ancestor"),
        EnumDyField.data_source(
            "State",
            "data.state",
            default_state={
                "safe": ["READY", "SERVING"],
                "warning": ["CREATING", "DELETING"],
                "alert": ["ERROR"],
                "disable": ["UNKNOWN"],
            },
        ),
        TextDyField.data_source("Property Count", "data.property_count"),
        TextDyField.data_source("Project", "data.project_id"),
    ],
    search=[
        SearchField.set(name="Index ID", key="data.indexId"),
        SearchField.set(name="Kind", key="data.kind"),
        SearchField.set(
            name="State",
            key="data.state",
            enums={
                "READY": {"label": "Ready"},
                "SERVING": {"label": "Serving"},
                "CREATING": {"label": "Creating"},
                "DELETING": {"label": "Deleting"},
                "ERROR": {"label": "Error"},
                "UNKNOWN": {"label": "Unknown"},
            },
        ),
        SearchField.set(name="Project ID", key="data.project_id"),
    ],
)

cst_index.metadata = cst_index_meta

# Cloud Service Type 목록
CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_index}),
]
