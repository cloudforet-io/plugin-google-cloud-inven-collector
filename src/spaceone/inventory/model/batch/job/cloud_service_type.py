import os

from spaceone.inventory.conf.cloud_service_conf import ASSET_URL
from spaceone.inventory.libs.common_parser import get_data_from_yaml
from spaceone.inventory.libs.schema.cloud_service_type import (
    CloudServiceTypeResource,
    CloudServiceTypeResponse,
)

"""
Batch Job Cloud Service Type - Job 개별 리소스 타입 정의
"""

current_dir = os.path.abspath(os.path.dirname(__file__))

# Job 관련 위젯 설정 파일들
total_count_conf = os.path.join(current_dir, "widget", "total_count.yml")
count_by_account_conf = os.path.join(current_dir, "widget", "count_by_account.yml")
count_by_region_conf = os.path.join(current_dir, "widget", "count_by_region.yml")
count_by_status_conf = os.path.join(current_dir, "widget", "count_by_status.yml")

cst_batch_job = CloudServiceTypeResource()
cst_batch_job.name = "Job"
cst_batch_job.provider = "google_cloud"
cst_batch_job.group = "Batch"
cst_batch_job.service_code = "google.batch"
cst_batch_job.is_primary = True
cst_batch_job.is_major = True
cst_batch_job.labels = ["Compute", "Container"]
cst_batch_job.tags = {
    "spaceone:icon": f"{ASSET_URL}/google_cloud_batch.svg",
    "spaceone:display_name": "Google Cloud Batch Jobs",
    "spaceone:is_beta": "true",
}

# 위젯 설정 (파일이 존재하는 경우에만 추가)
cst_batch_job.widgets = []

if os.path.exists(total_count_conf):
    cst_batch_job.widgets.append(get_data_from_yaml(total_count_conf))

if os.path.exists(count_by_account_conf):
    cst_batch_job.widgets.append(get_data_from_yaml(count_by_account_conf))

if os.path.exists(count_by_region_conf):
    cst_batch_job.widgets.append(get_data_from_yaml(count_by_region_conf))

if os.path.exists(count_by_status_conf):
    cst_batch_job.widgets.append(get_data_from_yaml(count_by_status_conf))

# 클라우드 서비스 타입 목록
CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_batch_job}),
]
