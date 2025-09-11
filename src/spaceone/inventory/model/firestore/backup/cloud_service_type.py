import os

from spaceone.inventory.conf.cloud_service_conf import ASSET_URL
from spaceone.inventory.libs.common_parser import get_data_from_yaml
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
from spaceone.inventory.libs.schema.metadata.dynamic_widget import (
    CardWidget,
    ChartWidget,
)

current_dir = os.path.abspath(os.path.dirname(__file__))

"""
BACKUP
"""
total_count_conf = os.path.join(current_dir, "widget/total_count.yaml")
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yaml")
count_by_project_conf = os.path.join(current_dir, "widget/count_by_project.yaml")

cst_backup = CloudServiceTypeResource()
cst_backup.name = "Backup"
cst_backup.provider = "google_cloud"
cst_backup.group = "Firestore"
cst_backup.service_code = "Cloud Firestore"
cst_backup.is_primary = False
cst_backup.is_major = False
cst_backup.labels = ["NoSQL", "Database", "Backup"]
cst_backup.tags = {
    "spaceone:icon": f"{ASSET_URL}/Firestore.svg",
}

cst_backup._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Database ID", "data.database_id"),
        EnumDyField.data_source(
            "State",
            "data.state",
            default_badge={
                "green.500": ["READY"],
                "yellow.500": ["CREATING"],
                "red.500": ["NOT_AVAILABLE"],
            },
        ),
        DateTimeDyField.data_source("Expires", "data.expire_time"),
        DateTimeDyField.data_source("Snapshot Time", "data.snapshot_time"),
    ],
    search=[
        SearchField.set(name="Database ID", key="data.database_id"),
        SearchField.set(name="State", key="data.state"),
        SearchField.set(
            name="Created Time", key="data.expire_time", data_type="datetime"
        ),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_backup}),
]
