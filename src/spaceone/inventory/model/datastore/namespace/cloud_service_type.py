from spaceone.inventory.libs.schema.cloud_service_type import (
    CloudServiceTypeMeta,
    CloudServiceTypeResource,
    CloudServiceTypeResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    DateTimeDyField,
    SearchField,
    TextDyField,
)

"""
Datastore Namespace Cloud Service Type 정의

Google Cloud Datastore Namespace 서비스 타입을 SpaceONE에서 표현하기 위한 모델을 정의합니다.
"""

# Cloud Service Type 리소스 정의
cst_namespace = CloudServiceTypeResource()
cst_namespace.name = "Namespace"
cst_namespace.provider = "google_cloud"
cst_namespace.group = "Datastore"
cst_namespace.labels = ["Database", "NoSQL"]
cst_namespace.service_code = "Cloud Datastore"
cst_namespace.is_primary = True
cst_namespace.is_major = True
cst_namespace.resource_type = "inventory.CloudService"
cst_namespace.tags = {
    "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/Cloud_Datastore.svg",
    "spaceone:display_name": "Datastore Namespace",
}

# 메타데이터 설정
cst_namespace_meta = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Namespace ID", "data.namespace_id"),
        TextDyField.data_source("Display Name", "data.display_name"),
        TextDyField.data_source("Kind Count", "data.kind_count"),
        TextDyField.data_source("Project", "data.project_id"),
        DateTimeDyField.data_source("Created Time", "data.created_time"),
    ],
    search=[
        SearchField.set(name="Namespace ID", key="data.namespace_id"),
        SearchField.set(name="Display Name", key="data.display_name"),
        SearchField.set(name="Project ID", key="data.project_id"),
    ],
)

cst_namespace.metadata = cst_namespace_meta

# Cloud Service Type 목록
CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_namespace}),
]
