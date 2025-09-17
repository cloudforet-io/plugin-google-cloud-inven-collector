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

total_count_conf = os.path.join(current_dir, "widget/total_count.yml")
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yml")
count_by_state_conf = os.path.join(current_dir, "widget/count_by_state.yml")

cst_filestore_backup = CloudServiceTypeResource()
cst_filestore_backup.name = "Backup"
cst_filestore_backup.provider = "google_cloud"
cst_filestore_backup.group = "Filestore"
cst_filestore_backup.service_code = "Filestore"
cst_filestore_backup.is_primary = False
cst_filestore_backup.is_major = False
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
                "warning": ["CREATING", "FINALIZING", "DELETING"],
                "alert": ["STATE_UNSPECIFIED", "INVALID"],
            },
        ),
        TextDyField.data_source("Description", "data.description"),
        DateTimeDyField.data_source("Created", "data.create_time"),
        TextDyField.data_source("Source Instance", "data.source_instance_id"),
        TextDyField.data_source("Source File Share", "data.source_file_share"),
        TextDyField.data_source("Capacity (GB)", "data.capacity_gb"),
        TextDyField.data_source("Storage (Bytes)", "data.storage_bytes"),
    ],
    search=[
        SearchField.set("State", "data.state"),
        SearchField.set("Description", "data.description"),
        SearchField.set("Created", "data.create_time"),
        SearchField.set("Source Instance", "data.source_instance_id"),
        SearchField.set("Source File Share", "data.source_file_share"),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_state_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_filestore_backup}),
]
