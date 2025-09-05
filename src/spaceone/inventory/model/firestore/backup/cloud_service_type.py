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
    SizeField,
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
cst_backup.is_major = True
cst_backup.labels = ["NoSQL", "Database", "Backup"]
cst_backup.tags = {
    "spaceone:icon": f"{ASSET_URL}/Firestore.svg",
}

cst_backup._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Location", "data.location_id"),
        TextDyField.data_source("Database", "data.database"),
        EnumDyField.data_source(
            "State",
            "data.state",
            default_badge={
                "green.500": ["READY"],
                "yellow.500": ["CREATING"],
                "red.500": ["NOT_AVAILABLE"],
            },
        ),
        SizeField.data_source("Size", "data.size_bytes"),
        DateTimeDyField.data_source("Created", "data.create_time"),
        DateTimeDyField.data_source("Expires", "data.expire_time"),
        DateTimeDyField.data_source("Version Time", "data.version_time"),
    ],
    search=[
        SearchField.set(name="Location", key="data.location_id"),
        SearchField.set(name="Database", key="data.database"),
        SearchField.set(name="State", key="data.state"),
        SearchField.set(
            name="Size (Bytes)", key="data.size_bytes", data_type="integer"
        ),
        SearchField.set(
            name="Created Time", key="data.create_time", data_type="datetime"
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
