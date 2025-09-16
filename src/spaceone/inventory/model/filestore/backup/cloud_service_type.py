from spaceone.inventory.libs.schema.cloud_service_type import CloudServiceTypeResource
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    ListDynamicLayout,
    TableDynamicLayout,
)

"""
Filestore Backup Cloud Service Type 정의

SpaceONE에서 Filestore 백업 리소스를 표시하기 위한 메타데이터 및 레이아웃을 정의합니다.
"""

# Backup 상세 정보 레이아웃
backup_detail = ItemDynamicLayout.set_fields(
    "백업 상세 정보",
    fields=[
        "backup_id",
        "state",
        "description",
        "location",
        "source_instance",
        "source_file_share",
        "capacity_gb",
        "storage_bytes",
        "create_time",
    ],
)

# 라벨 정보 테이블 레이아웃
backup_labels = TableDynamicLayout.set_fields(
    "라벨",
    root_path="labels",
    fields=[
        "key",
        "value",
    ],
)

# 메타데이터 레이아웃 정의
backup_meta = ListDynamicLayout.set_layouts(
    "백업",
    layouts=[backup_detail, backup_labels],
)

# Cloud Service Type 정의
cst_filestore_backup = CloudServiceTypeResource()
cst_filestore_backup.name = "Backup"
cst_filestore_backup.provider = "google_cloud"
cst_filestore_backup.group = "Filestore"
cst_filestore_backup.service_code = "Filestore"
cst_filestore_backup.is_primary = False
cst_filestore_backup.is_major = True
cst_filestore_backup.labels = ["Storage"]
cst_filestore_backup.tags = {
    "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/filestore.svg"
}

# 메타데이터 설정
cst_filestore_backup.metadata = backup_meta

# Export할 Cloud Service Types
CLOUD_SERVICE_TYPES = [cst_filestore_backup]
