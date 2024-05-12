import os

from spaceone.inventory.libs.common_parser import *
from spaceone.inventory.libs.schema.metadata.dynamic_widget import (
    CardWidget,
    ChartWidget,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    TextDyField,
    SearchField,
    DateTimeDyField,
    ListDyField,
    EnumDyField,
    SizeField,
)
from spaceone.inventory.libs.schema.cloud_service_type import (
    CloudServiceTypeResource,
    CloudServiceTypeResponse,
    CloudServiceTypeMeta,
)
from spaceone.inventory.conf.cloud_service_conf import *

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, "widget/total_count.yml")
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yml")
count_by_project_conf = os.path.join(current_dir, "widget/count_by_project.yml")

cst_snapshot = CloudServiceTypeResource()
cst_snapshot.name = "Snapshot"
cst_snapshot.provider = "google_cloud"
cst_snapshot.group = "ComputeEngine"
cst_snapshot.service_code = "Compute Engine"
cst_snapshot.labels = ["Compute", "Storage"]
cst_snapshot.tags = {
    "spaceone:icon": f"{ASSET_URL}/Compute_Engine.svg",
}

cst_snapshot._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        EnumDyField.data_source(
            "Status",
            "data.status",
            default_state={
                "safe": ["READY"],
                "warning": ["CREATING", "UPLOADING", "DELETING"],
                "alert": ["FAILED"],
            },
        ),
        ListDyField.data_source("Location", "data.storage_locations"),
        SizeField.data_source("SnapShot Size", "data.disk.storage_bytes"),
        TextDyField.data_source("Creation Type", "data.creation_type"),
        TextDyField.data_source("Source Disk", "data.disk.source_disk_display"),
        SizeField.data_source("Disk Size", "data.disk.disk_size"),
        DateTimeDyField.data_source("Creation Time", "data.creation_timestamp"),
    ],
    search=[
        SearchField.set(name="ID", key="data.id"),
        SearchField.set(name="Name", key="data.name"),
        SearchField.set(name="Location", key="data.storage_locations"),
        SearchField.set(name="Source Disk", key="data.disk.source_disk_display"),
        SearchField.set(name="Creation Type", key="data.creation_type"),
        SearchField.set(
            name="Creation Time", key="data.creation_timestamp", data_type="datetime"
        ),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_snapshot}),
]
