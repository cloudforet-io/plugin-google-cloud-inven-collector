from spaceone.inventory.libs.schema.cloud_service_type import CloudServiceTypeResource
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    ListDynamicLayout,
    TableDynamicLayout,
)

"""
Filestore Snapshot Cloud Service Type 정의

SpaceONE에서 Filestore 스냅샷 리소스를 표시하기 위한 메타데이터 및 레이아웃을 정의합니다.
"""

# Snapshot 상세 정보 레이아웃
snapshot_detail = ItemDynamicLayout.set_fields(
    "스냅샷 상세 정보",
    fields=[
        "snapshot_id",
        "state",
        "description",
        "location",
        "instance_id",
        "create_time",
    ],
)

# 라벨 정보 테이블 레이아웃
snapshot_labels = TableDynamicLayout.set_fields(
    "라벨",
    root_path="labels",
    fields=[
        "key",
        "value",
    ],
)

# 메타데이터 레이아웃 정의
snapshot_meta = ListDynamicLayout.set_layouts(
    "스냅샷",
    layouts=[snapshot_detail, snapshot_labels],
)

# Cloud Service Type 정의
cst_filestore_snapshot = CloudServiceTypeResource()
cst_filestore_snapshot.name = "Snapshot"
cst_filestore_snapshot.provider = "google_cloud"
cst_filestore_snapshot.group = "Filestore"
cst_filestore_snapshot.service_code = "Filestore"
cst_filestore_snapshot.is_primary = False
cst_filestore_snapshot.is_major = True
cst_filestore_snapshot.labels = ["Storage"]
cst_filestore_snapshot.tags = {
    "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/filestore.svg"
}

# 메타데이터 설정
cst_filestore_snapshot.metadata = snapshot_meta

# Export할 Cloud Service Types
CLOUD_SERVICE_TYPES = [cst_filestore_snapshot]
