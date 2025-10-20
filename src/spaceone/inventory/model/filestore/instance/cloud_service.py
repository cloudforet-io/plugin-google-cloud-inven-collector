from schematics.types import ModelType, PolyModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    DateTimeDyField,
    EnumDyField,
    ListDyField,
    SizeField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    TableDynamicLayout,
)
from spaceone.inventory.model.filestore.instance.data import FilestoreInstanceData

# TAB - Instance Details
filestore_instance_details = ItemDynamicLayout.set_fields(
    "Instance Details",
    fields=[
        TextDyField.data_source("Instance ID", "data.instance_id"),
        TextDyField.data_source("Full Name", "data.full_name"),
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
            ],
        ),
        TextDyField.data_source("Location", "data.location"),
        TextDyField.data_source("Description", "data.description"),
        DateTimeDyField.data_source("Created", "data.create_time"),
    ],
)

# TAB - Performance
filestore_performance = ItemDynamicLayout.set_fields(
    "Performance",
    fields=[
        TextDyField.data_source("Protocol", "data.protocol"),
        TextDyField.data_source("Custom Performance Supported", "data.custom_performance_supported"),
        TextDyField.data_source("Max Read IOPS", "data.performance_limits.max_read_iops"),
        TextDyField.data_source("Max Write IOPS", "data.performance_limits.max_write_iops"),
        TextDyField.data_source("Max Read Throughput (Bps)", "data.performance_limits.max_read_throughput_bps"),
        TextDyField.data_source("Max Write Throughput (Bps)", "data.performance_limits.max_write_throughput_bps"),
        TextDyField.data_source("Max IOPS", "data.performance_limits.max_iops"),
    ],
)

# TAB - Networks
filestore_networks = TableDynamicLayout.set_fields(
    "Networks",
    root_path="data.networks",
    fields=[
        TextDyField.data_source("Network", "network"),
        ListDyField.data_source(
            "Modes",
            "modes",
            default_badge={"type": "outline", "delimiter": "<br>"},
        ),
        TextDyField.data_source("Reserved IP Range", "reserved_ip_range"),
        TextDyField.data_source("Connect Mode", "connect_mode"),
    ],
)

# TAB - File Shares
filestore_file_shares = TableDynamicLayout.set_fields(
    "File Shares",
    root_path="data.unified_file_shares",
    fields=[
        TextDyField.data_source("Name", "name"),
        # TextDyField.data_source("Mount Name", "mount_name"),
        # TextDyField.data_source("Description", "description"),
        SizeField.data_source("Capacity (TiB)", "capacity_tib"),
        # EnumDyField.data_source(
        #     "State",
        #     "state",
        #     default_state={
        #         "safe": ["READY"],
        #         "warning": ["CREATING", "DELETING"],
        #         "alert": ["ERROR"],
        #         "disable": ["UNKNOWN", ""],
        #     },
        # ),
        TextDyField.data_source("Source Backup", "source_backup"),
        ListDyField.data_source(
            "NFS Export Options",
            "nfs_export_options",
            default_badge={"type": "outline", "delimiter": "<br>"},
        ),
        # TextDyField.data_source("Data Source", "data_source"),
    ],
)

# TAB - Statistics
filestore_statistics = ItemDynamicLayout.set_fields(
    "Statistics",
    fields=[
        SizeField.data_source("Total Capacity (TiB)", "data.stats.total_capacity_tib"),
        TextDyField.data_source("File Share Count", "data.stats.file_share_count"),
        TextDyField.data_source("Snapshot Count", "data.stats.snapshot_count"),
        TextDyField.data_source("Network Count", "data.stats.network_count"),
    ],
)

# TAB - Labels (if any)
filestore_labels = TableDynamicLayout.set_fields(
    "Labels",
    root_path="data.labels",
    fields=[
        TextDyField.data_source("Key", "key"),
        TextDyField.data_source("Value", "value"),
    ],
)

# Unified metadata layout
filestore_instance_meta = CloudServiceMeta.set_layouts(
    [
        filestore_instance_details,
        filestore_performance,
        filestore_networks,
        filestore_file_shares,
        filestore_statistics,
        filestore_labels,
    ]
)


class FilestoreResource(CloudServiceResource):
    cloud_service_group = StringType(default="Filestore")


class FilestoreInstanceResource(FilestoreResource):
    cloud_service_type = StringType(default="Instance")
    data = ModelType(FilestoreInstanceData)
    _metadata = ModelType(
        CloudServiceMeta, default=filestore_instance_meta, serialized_name="metadata"
    )


class FilestoreInstanceResponse(CloudServiceResponse):
    resource = PolyModelType(FilestoreInstanceResource)
