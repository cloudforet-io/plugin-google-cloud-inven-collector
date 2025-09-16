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
Filestore Snapshot Cloud Service Type 정의

SpaceONE에서 Filestore 스냅샷 리소스를 표시하기 위한 메타데이터 및 레이아웃을 정의합니다.
"""

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, "widget/total_count.yml")
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yml")
count_by_state_conf = os.path.join(current_dir, "widget/count_by_state.yml")

cst_filestore_snapshot = CloudServiceTypeResource()
cst_filestore_snapshot.name = "Snapshot"
cst_filestore_snapshot.provider = "google_cloud"
cst_filestore_snapshot.group = "Filestore"
cst_filestore_snapshot.service_code = "Filestore"
cst_filestore_snapshot.is_primary = False
cst_filestore_snapshot.is_major = True
cst_filestore_snapshot.labels = ["Storage"]
cst_filestore_snapshot.tags = {
    "spaceone:icon": f"{ASSET_URL}/Filestore.svg",
    "spaceone:display_name": "Filestore Snapshot",
}

cst_filestore_snapshot._metadata = CloudServiceTypeMeta.set_meta(
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
        TextDyField.data_source("Snapshot ID", "data.snapshot_id"),
        TextDyField.data_source("Instance ID", "data.instance_id"),
        TextDyField.data_source("Location", "data.location"),
        TextDyField.data_source("Description", "data.description"),
        DateTimeDyField.data_source("Created", "data.create_time"),
    ],
    search=[
        SearchField.set("Snapshot ID", "data.snapshot_id"),
        SearchField.set("Instance ID", "data.instance_id"),
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
    CloudServiceTypeResponse({"resource": cst_filestore_snapshot}),
]
