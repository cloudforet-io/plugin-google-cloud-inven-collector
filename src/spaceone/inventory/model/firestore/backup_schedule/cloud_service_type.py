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
BACKUP SCHEDULE
"""
total_count_conf = os.path.join(current_dir, "widget/total_count.yaml")
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yaml")
count_by_project_conf = os.path.join(current_dir, "widget/count_by_project.yaml")

cst_backup_schedule = CloudServiceTypeResource()
cst_backup_schedule.name = "BackupSchedule"
cst_backup_schedule.provider = "google_cloud"
cst_backup_schedule.group = "Firestore"
cst_backup_schedule.service_code = "Cloud Firestore"
cst_backup_schedule.is_primary = False
cst_backup_schedule.is_major = False
cst_backup_schedule.labels = ["NoSQL", "Database", "Backup"]
cst_backup_schedule.tags = {
    "spaceone:icon": f"{ASSET_URL}/Firestore.svg",
}

cst_backup_schedule._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Database ID", "data.database_id"),
        EnumDyField.data_source(
            "Recurrence Type",
            "data.recurrence_type",
            default_badge={"indigo.500": ["DAILY"], "coral.600": ["WEEKLY"]},
        ),
        TextDyField.data_source("Retention", "data.retention"),
        DateTimeDyField.data_source("Created", "data.create_time"),
        DateTimeDyField.data_source("Updated", "data.update_time"),
    ],
    search=[
        SearchField.set(name="Database ID", key="data.database_id"),
        SearchField.set(name="Recurrence Type", key="data.recurrence_type"),
        SearchField.set(name="Retention", key="data.retention"),
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
    CloudServiceTypeResponse({"resource": cst_backup_schedule}),
]
