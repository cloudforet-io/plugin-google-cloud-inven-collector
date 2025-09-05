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

total_count_conf = os.path.join(current_dir, "widget/total_count.yml")
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yml")
count_by_tier_conf = os.path.join(current_dir, "widget/count_by_tier.yml")

cst_filestore_instance = CloudServiceTypeResource()
cst_filestore_instance.name = "Instance"
cst_filestore_instance.provider = "google_cloud"
cst_filestore_instance.group = "Filestore"
cst_filestore_instance.service_code = "Filestore"
cst_filestore_instance.is_primary = True
cst_filestore_instance.is_major = True
cst_filestore_instance.labels = ["Storage", "FileSystem"]
cst_filestore_instance.tags = {
    "spaceone:icon": f"{ASSET_URL}/Filestore.svg",
    "spaceone:display_name": "Filestore",
}

cst_filestore_instance._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Instance ID", "data.instance_id"),
        TextDyField.data_source("Name", "data.name"),
        EnumDyField.data_source(
            "State",
            "data.state",
            default_state={
                "safe": ["READY"],
                "warning": ["CREATING", "REPAIRING", "DELETING"],
                "alert": ["ERROR"],
                "disable": ["UNKNOWN"],
            },
        ),
        EnumDyField.data_source(
            "Tier",
            "data.tier",
            default_outline_badge=[
                "BASIC_HDD",
                "BASIC_SSD",
                "HIGH_SCALE_SSD",
                "REGIONAL",
                "ENTERPRISE",
                "ENTERPRISE_TIER_1",
                "ENTERPRISE_TIER_2",
            ],
        ),
        TextDyField.data_source("Location", "data.location"),
        TextDyField.data_source("Description", "data.description"),
        SizeField.data_source("Total Capacity (GB)", "data.stats.total_capacity_gb"),
        TextDyField.data_source("File Share Count", "data.stats.file_share_count"),
        TextDyField.data_source("Snapshot Count", "data.stats.snapshot_count"),
        TextDyField.data_source("Network Count", "data.stats.network_count"),
        DateTimeDyField.data_source("Created", "data.create_time"),
        DateTimeDyField.data_source("Updated", "data.update_time"),
        # Optional fields
        TextDyField.data_source(
            "Primary File Share Name",
            "data.file_shares.0.name",
            options={"is_optional": True},
        ),
        SizeField.data_source(
            "Primary File Share Capacity (GB)",
            "data.file_shares.0.capacity_gb",
            options={"is_optional": True},
        ),
        TextDyField.data_source(
            "Primary Network", "data.networks.0.network", options={"is_optional": True}
        ),
        TextDyField.data_source(
            "Reserved IP Range",
            "data.networks.0.reserved_ip_range",
            options={"is_optional": True},
        ),
        TextDyField.data_source(
            "Latest Snapshot", "data.snapshots.0.name", options={"is_optional": True}
        ),
        DateTimeDyField.data_source(
            "Latest Snapshot Created",
            "data.snapshots.0.create_time",
            options={"is_optional": True},
        ),
    ],
    search=[
        SearchField.set(name="Instance ID", key="data.instance_id"),
        SearchField.set(name="Name", key="data.name"),
        SearchField.set(
            name="State",
            key="data.state",
            enums={
                "READY": {"label": "Ready"},
                "CREATING": {"label": "Creating"},
                "REPAIRING": {"label": "Repairing"},
                "DELETING": {"label": "Deleting"},
                "ERROR": {"label": "Error"},
                "UNKNOWN": {"label": "Unknown"},
            },
        ),
        SearchField.set(
            name="Tier",
            key="data.tier",
            enums={
                "BASIC_HDD": {"label": "Basic HDD"},
                "BASIC_SSD": {"label": "Basic SSD"},
                "HIGH_SCALE_SSD": {"label": "High Scale SSD"},
                "REGIONAL": {"label": "Regional"},
                "ENTERPRISE": {"label": "Enterprise"},
                "ENTERPRISE_TIER_1": {"label": "Enterprise Tier 1"},
                "ENTERPRISE_TIER_2": {"label": "Enterprise Tier 2"},
            },
        ),
        SearchField.set(name="Location", key="data.location"),
        SearchField.set(name="Description", key="data.description"),
        SearchField.set(
            name="Total Capacity (GB)",
            key="data.stats.total_capacity_gb",
            data_type="integer",
        ),
        SearchField.set(
            name="File Share Count",
            key="data.stats.file_share_count",
            data_type="integer",
        ),
        SearchField.set(
            name="Snapshot Count", key="data.stats.snapshot_count", data_type="integer"
        ),
        SearchField.set(
            name="Network Count", key="data.stats.network_count", data_type="integer"
        ),
        SearchField.set(name="Created", key="data.create_time", data_type="datetime"),
        SearchField.set(name="Updated", key="data.update_time", data_type="datetime"),
        SearchField.set(name="File Share Name", key="data.file_shares.name"),
        SearchField.set(name="Network", key="data.networks.network"),
        SearchField.set(name="Snapshot Name", key="data.snapshots.name"),
        SearchField.set(name="Account ID", key="account"),
        SearchField.set(name="Region", key="region_code"),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_tier_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_filestore_instance}),
]
