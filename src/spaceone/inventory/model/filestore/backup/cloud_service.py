from schematics.types import ModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    DateTimeDyField,
    EnumDyField,
    SizeField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    TableDynamicLayout,
)
from spaceone.inventory.model.filestore.backup.data import FilestoreBackupData

"""
Filestore Backup Cloud Service 모델 정의

SpaceONE의 Cloud Service 형태로 Filestore 백업 리소스를 표현하기 위한 모델입니다.
"""

"""
Filestore Backup UI 메타데이터 레이아웃 정의

SpaceONE 콘솔에서 Filestore 백업 정보를 표시하기 위한 UI 레이아웃을 정의합니다.
"""

# TAB - Backup Details
filestore_backup_details = ItemDynamicLayout.set_fields(
    "Backup Details",
    fields=[
        TextDyField.data_source("Backup ID", "data.backup_id"),
        TextDyField.data_source("Full Name", "data.full_name"),
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
    ],
)

# TAB - Source Information
filestore_backup_source = ItemDynamicLayout.set_fields(
    "Source Information",
    fields=[
        TextDyField.data_source("Source Instance ID", "data.source_instance_id"),
        TextDyField.data_source("Source File Share", "data.source_file_share"),
        TextDyField.data_source("Source Instance Tier", "data.source_instance_tier"),
        TextDyField.data_source("File System Protocol", "data.file_system_protocol"),
    ],
)

# TAB - Capacity Information
filestore_backup_capacity = ItemDynamicLayout.set_fields(
    "Capacity Information",
    fields=[
        SizeField.data_source("Capacity (GB)", "data.capacity_gb"),
        SizeField.data_source("Storage (Bytes)", "data.storage_bytes"),
        SizeField.data_source("Download (Bytes)", "data.download_bytes"),
    ],
)

# TAB - Labels
filestore_backup_labels = TableDynamicLayout.set_fields(
    "Labels",
    root_path="data.labels",
    fields=[
        TextDyField.data_source("Key", "key"),
        TextDyField.data_source("Value", "value"),
    ],
)

filestore_backup_meta = CloudServiceMeta.set_layouts(
    [
        filestore_backup_details,
        filestore_backup_source,
        filestore_backup_capacity,
        filestore_backup_labels,
    ]
)


class FilestoreBackupResource(CloudServiceResource):
    """Filestore 백업 리소스 모델"""

    cloud_service_type = StringType(default="Backup")
    cloud_service_group = StringType(default="Filestore")
    data = ModelType(FilestoreBackupData)
    _metadata = ModelType(
        CloudServiceMeta, default=filestore_backup_meta, serialized_name="metadata"
    )


class FilestoreBackupResponse(CloudServiceResponse):
    """Filestore 백업 응답 모델"""

    resource = ModelType(FilestoreBackupResource)
