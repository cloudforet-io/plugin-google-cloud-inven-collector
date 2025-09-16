import os

from spaceone.inventory.conf.cloud_service_conf import ASSET_URL
from spaceone.inventory.libs.schema.cloud_service_type import (
    CloudServiceTypeMeta,
    CloudServiceTypeResource,
    CloudServiceTypeResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    DateTimeDyField,
    EnumDyField,
    SearchField,
    TextDyField,
)

"""
Filestore Backup Cloud Service Type 정의

SpaceONE에서 Filestore 백업 리소스를 표시하기 위한 메타데이터 및 레이아웃을 정의합니다.
"""

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, "widget/total_count.yml")
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yml")
count_by_state_conf = os.path.join(current_dir, "widget/count_by_state.yml")

cst_filestore_backup = CloudServiceTypeResource()
cst_filestore_backup.name = "Backup"
cst_filestore_backup.provider = "google_cloud"
cst_filestore_backup.group = "Filestore"
cst_filestore_backup.service_code = "Filestore"
cst_filestore_backup.is_primary = False
cst_filestore_backup.is_major = True
cst_filestore_backup.labels = ["Storage"]
cst_filestore_backup.tags = {
    "spaceone:icon": f"{ASSET_URL}/Filestore.svg",
    "spaceone:display_name": "Filestore Backup",
}

cst_filestore_backup._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        EnumDyField.data_source(
            "State",
            "data.state",
            default_state={
                "safe": ["READY"],
                "warning": ["CREATING", "DELETING"],
                "alert": ["ERROR"],
            },
        ),
        TextDyField.data_source("Backup ID", "data.backup_id"),
        TextDyField.data_source("Source Instance", "data.source_instance"),
        TextDyField.data_source("Source File Share", "data.source_file_share"),
        TextDyField.data_source("Location", "data.location"),
        TextDyField.data_source("Capacity (GB)", "data.capacity_gb"),
        TextDyField.data_source("Storage (Bytes)", "data.storage_bytes"),
        TextDyField.data_source("Description", "data.description"),
        DateTimeDyField.data_source("Created", "data.create_time"),
    ],
    search=[
        SearchField.set("Backup ID", "data.backup_id"),
        SearchField.set("Source Instance", "data.source_instance"),
        SearchField.set("State", "data.state"),
        SearchField.set("Location", "data.location"),
        SearchField.set("Created", "data.create_time"),
    ],
    # widget=[
    #     CardWidget.set(**get_data_from_yaml(total_count_conf)),
    #     ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
    #     ChartWidget.set(**get_data_from_yaml(count_by_state_conf)),
    # ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_filestore_backup}),
]
