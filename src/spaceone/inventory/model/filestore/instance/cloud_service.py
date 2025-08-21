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

"""
Filestore Instance Cloud Service 모델 정의

Google Cloud Filestore 인스턴스 리소스를 SpaceONE에서 표현하기 위한 모델을 정의합니다.
- FilestoreInstanceResource: Filestore 인스턴스 리소스 데이터 구조
- FilestoreInstanceResponse: Filestore 인스턴스 응답 형식
"""

"""
Filestore Instance UI 메타데이터 레이아웃 정의

SpaceONE 콘솔에서 Filestore 인스턴스 정보를 표시하기 위한 UI 레이아웃을 정의합니다.
"""

# TAB - Instance Details
filestore_instance_details = ItemDynamicLayout.set_fields(
    "Instance Details",
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
            ],
        ),
        TextDyField.data_source("Location", "data.location"),
        TextDyField.data_source("Description", "data.description"),
        DateTimeDyField.data_source("Created", "data.create_time"),
        DateTimeDyField.data_source("Updated", "data.update_time"),
    ],
)

# TAB - File Shares
filestore_file_shares = TableDynamicLayout.set_fields(
    "File Shares",
    root_path="data.file_shares",
    fields=[
        TextDyField.data_source("Name", "name"),
        SizeField.data_source("Capacity (GB)", "capacity_gb"),
        TextDyField.data_source("Source Backup", "source_backup"),
        ListDyField.data_source(
            "NFS Export Options",
            "nfs_export_options",
            default_badge={"type": "outline", "delimiter": "<br>"},
        ),
    ],
)

# TAB - Detailed Shares (Enterprise only)
filestore_detailed_shares = TableDynamicLayout.set_fields(
    "Detailed Shares",
    root_path="data.detailed_shares",
    fields=[
        TextDyField.data_source("Name", "name"),
        TextDyField.data_source("Mount Name", "mount_name"),
        TextDyField.data_source("Description", "description"),
        SizeField.data_source("Capacity (GB)", "capacity_gb"),
        EnumDyField.data_source(
            "State",
            "state",
            default_state={
                "safe": ["READY"],
                "warning": ["CREATING", "DELETING"],
                "alert": ["ERROR"],
            },
        ),
        ListDyField.data_source(
            "NFS Export Options",
            "nfs_export_options",
            default_badge={"type": "outline", "delimiter": "<br>"},
        ),
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

# TAB - Snapshots
filestore_snapshots = TableDynamicLayout.set_fields(
    "Snapshots",
    root_path="data.snapshots",
    fields=[
        TextDyField.data_source("Name", "name"),
        TextDyField.data_source("Description", "description"),
        EnumDyField.data_source(
            "State",
            "state",
            default_state={
                "safe": ["READY"],
                "warning": ["CREATING", "DELETING"],
                "alert": ["ERROR"],
            },
        ),
        TextDyField.data_source("File Share", "file_share"),
        DateTimeDyField.data_source("Create Time", "create_time"),
    ],
)

# TAB - Statistics
filestore_statistics = ItemDynamicLayout.set_fields(
    "Statistics",
    fields=[
        SizeField.data_source("Total Capacity (GB)", "data.stats.total_capacity_gb"),
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

# Combined metadata layout
filestore_instance_meta = CloudServiceMeta.set_layouts(
    [
        filestore_instance_details,
        filestore_file_shares,
        filestore_detailed_shares,
        filestore_networks,
        filestore_snapshots,
        filestore_statistics,
        filestore_labels,
    ]
)

"""
Filestore Instance 리소스 모델

Google Cloud Filestore 인스턴스의 모든 정보를 포함하는 리소스 모델입니다.
CloudServiceResource의 기본 구조를 상속받아 사용합니다.
"""


class FilestoreResource(CloudServiceResource):
    cloud_service_group = StringType(default="Filestore")


class FilestoreInstanceResource(FilestoreResource):
    cloud_service_type = StringType(default="Instance")
    data = ModelType(FilestoreInstanceData)
    _metadata = ModelType(
        CloudServiceMeta, default=filestore_instance_meta, serialized_name="metadata"
    )


class FilestoreInstanceResponse(CloudServiceResponse):
    """
    Filestore Instance 응답 모델

    Filestore 인스턴스 수집 결과를 반환하는 응답 모델입니다.
    """

    resource = PolyModelType(FilestoreInstanceResource)
