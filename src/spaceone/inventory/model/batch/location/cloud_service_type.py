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

# 위젯 설정 파일 경로
current_dir = os.path.abspath(os.path.dirname(__file__))
total_count_conf = os.path.join(current_dir, "widget/total_count.yml")
count_by_account_conf = os.path.join(current_dir, "widget/count_by_account.yml")
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yml")

# 최적화된 Batch 클라우드 서비스 타입
cst_batch = CloudServiceTypeResource()
cst_batch.name = "Location"
cst_batch.provider = "google_cloud"
cst_batch.group = "Batch"
cst_batch.service_code = "Batch"
cst_batch.labels = ["Compute", "Batch", "Container"]
cst_batch.is_primary = True
cst_batch.is_major = True
cst_batch.tags = {
    "spaceone:icon": f"{ASSET_URL}/Batch.svg",
}

# 최적화된 메타데이터 - 핵심 필드만 포함
cst_batch._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        # 핵심 필드들만 포함
        TextDyField.data_source("Project ID", "data.project_id"),
        TextDyField.data_source("Total Jobs", "data.job_count"),
        TextDyField.data_source("Account ID", "account", options={"is_optional": True}),
    ],
    search=[
        # 검색 필드 최적화
        SearchField.set(name="Project ID", key="data.project_id"),
        SearchField.set(name="Job Count", key="data.job_count"),
        SearchField.set(name="Account ID", key="account"),
        SearchField.set(
            name="Project Group",
            key="project_group_id",
            reference="identity.ProjectGroup",
        ),
    ],
    widget=[
        # 위젯 설정 (파일이 존재하는 경우만)
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_account_conf)),
    ],
)

# 클라우드 서비스 타입 목록
CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_batch}),
]
