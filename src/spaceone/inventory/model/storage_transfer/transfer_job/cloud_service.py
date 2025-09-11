from schematics.types import ModelType, PolyModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    DateTimeDyField,
    EnumDyField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
)
from spaceone.inventory.model.storage_transfer.transfer_job.data import (
    TransferJob,
)

"""
Transfer Job (Simplified)
"""

# TAB - Transfer Job Configuration
transfer_job_configuration_meta = ItemDynamicLayout.set_fields(
    "Configuration",
    fields=[
        TextDyField.data_source("Job Name", "data.name"),
        TextDyField.data_source("Description", "data.description"),
        EnumDyField.data_source(
            "Status",
            "data.status",
            default_state={
                "safe": ["ENABLED"],
                "warning": ["DISABLED"],
                "alert": ["DELETED"],
            },
        ),
        TextDyField.data_source("Source Type", "data.source_type"),
        TextDyField.data_source("Sink Type", "data.sink_type"),
        TextDyField.data_source("Schedule", "data.schedule_display"),
        TextDyField.data_source("Transfer Options", "data.transfer_options_display"),
        TextDyField.data_source("Latest Operation", "data.latest_operation_name"),
        DateTimeDyField.data_source("Created", "data.creation_time"),
        DateTimeDyField.data_source("Last Modified", "data.last_modification_time"),
        DateTimeDyField.data_source("Deleted", "data.deletion_time"),
    ],
)

# TAB - Active Transfer Configuration (Union Field 기반)
active_transfer_config_meta = ItemDynamicLayout.set_fields(
    "Active Transfer Configuration",
    fields=[
        # Active source/sink information
        TextDyField.data_source("Active Source Type", "data.source_type"),
        TextDyField.data_source("Active Source Details", "data.active_source_details"),
        TextDyField.data_source("Active Sink Type", "data.sink_type"),
        TextDyField.data_source("Active Sink Details", "data.active_sink_details"),
        # Agent Pool information (POSIX transfers only)
        TextDyField.data_source(
            "Source Agent Pool",
            "data.transfer_spec.source_agent_pool_name",
            options={"is_optional": True},
        ),
        TextDyField.data_source(
            "Sink Agent Pool",
            "data.transfer_spec.sink_agent_pool_name",
            options={"is_optional": True},
        ),
    ],
)

# TAB - Complete Transfer Specification (모든 필드 표시)
transfer_spec_meta = ItemDynamicLayout.set_fields(
    "Complete Transfer Specification",
    fields=[
        # Union Field 그룹 1: Data Source (하나만 활성화)
        TextDyField.data_source(
            "GCS Data Source",
            "data.transfer_spec.gcs_data_source",
            options={"is_optional": True, "translation_id": "COMMON.GCS_SOURCE"},
        ),
        TextDyField.data_source(
            "AWS S3 Data Source",
            "data.transfer_spec.aws_s3_data_source",
            options={"is_optional": True},
        ),
        TextDyField.data_source(
            "Azure Blob Storage Data Source",
            "data.transfer_spec.azure_blob_storage_data_source",
            options={"is_optional": True},
        ),
        TextDyField.data_source(
            "HTTP Data Source",
            "data.transfer_spec.http_data_source",
            options={"is_optional": True},
        ),
        TextDyField.data_source(
            "POSIX Data Source",
            "data.transfer_spec.posix_data_source",
            options={"is_optional": True},
        ),
        # Union Field 그룹 2: Data Sink (하나만 활성화)
        TextDyField.data_source(
            "GCS Data Sink",
            "data.transfer_spec.gcs_data_sink",
            options={"is_optional": True, "translation_id": "COMMON.GCS_SINK"},
        ),
        TextDyField.data_source(
            "POSIX Data Sink",
            "data.transfer_spec.posix_data_sink",
            options={"is_optional": True},
        ),
        # 기타 비-Union 필드들
        TextDyField.data_source(
            "Object Conditions", "data.transfer_spec.object_conditions"
        ),
        TextDyField.data_source(
            "Transfer Manifest", "data.transfer_spec.transfer_manifest"
        ),
    ],
)

# TAB - Notification Configuration
notification_config_meta = ItemDynamicLayout.set_fields(
    "Notification Configuration",
    fields=[
        TextDyField.data_source(
            "Pub/Sub Topic", "data.notification_config.pubsub_topic"
        ),
        TextDyField.data_source("Event Types", "data.notification_config.event_types"),
        TextDyField.data_source(
            "Payload Format", "data.notification_config.payload_format"
        ),
    ],
)

# TAB - Logging Configuration
logging_config_meta = ItemDynamicLayout.set_fields(
    "Logging Configuration",
    fields=[
        TextDyField.data_source("Log Actions", "data.logging_config.log_actions"),
        TextDyField.data_source(
            "Log Action States", "data.logging_config.log_action_states"
        ),
        EnumDyField.data_source(
            "Enable On-prem GCS Transfer Logs",
            "data.logging_config.enable_onprem_gcs_transfer_logs",
            default_badge={"indigo.500": ["true"], "coral.600": ["false"]},
        ),
    ],
)

transfer_job_meta = CloudServiceMeta.set_layouts(
    [
        transfer_job_configuration_meta,
        active_transfer_config_meta,
        transfer_spec_meta,
        notification_config_meta,
        logging_config_meta,
    ]
)


class StorageTransferResource(CloudServiceResource):
    cloud_service_group = StringType(default="StorageTransfer")


class TransferJobResource(StorageTransferResource):
    cloud_service_type = StringType(default="TransferJob")
    data = ModelType(TransferJob)
    _metadata = ModelType(
        CloudServiceMeta, default=transfer_job_meta, serialized_name="metadata"
    )


class TransferJobResponse(CloudServiceResponse):
    resource = PolyModelType(TransferJobResource)
