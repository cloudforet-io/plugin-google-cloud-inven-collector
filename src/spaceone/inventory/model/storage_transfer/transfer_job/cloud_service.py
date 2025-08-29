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
    TableDynamicLayout,
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
        TextDyField.data_source("Job Name", "name"),
        TextDyField.data_source("Project ID", "data.project_id"),
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
        DateTimeDyField.data_source("Created", "data.creation_time"),
        DateTimeDyField.data_source("Last Modified", "data.last_modification_time"),
        DateTimeDyField.data_source("Deleted", "data.deletion_time"),
    ],
)

# TAB - Transfer Specification
transfer_spec_meta = ItemDynamicLayout.set_fields(
    "Transfer Specification",
    fields=[
        TextDyField.data_source(
            "Source Agent Pool", "data.transfer_spec.source_agent_pool_name"
        ),
        TextDyField.data_source(
            "Sink Agent Pool", "data.transfer_spec.sink_agent_pool_name"
        ),
        TextDyField.data_source(
            "GCS Data Source", "data.transfer_spec.gcs_data_source"
        ),
        TextDyField.data_source("GCS Data Sink", "data.transfer_spec.gcs_data_sink"),
        TextDyField.data_source(
            "AWS S3 Data Source", "data.transfer_spec.aws_s3_data_source"
        ),
        TextDyField.data_source(
            "Azure Blob Storage Data Source",
            "data.transfer_spec.azure_blob_storage_data_source",
        ),
        TextDyField.data_source(
            "HTTP Data Source", "data.transfer_spec.http_data_source"
        ),
        TextDyField.data_source(
            "POSIX Data Source", "data.transfer_spec.posix_data_source"
        ),
        TextDyField.data_source(
            "POSIX Data Sink", "data.transfer_spec.posix_data_sink"
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

# TAB - Labels
transfer_job_labels_meta = TableDynamicLayout.set_fields(
    "Labels",
    root_path="data.labels",
    fields=[
        TextDyField.data_source("Key", "key"),
        TextDyField.data_source("Value", "value"),
    ],
)

transfer_job_meta = CloudServiceMeta.set_layouts(
    [
        transfer_job_configuration_meta,
        transfer_spec_meta,
        notification_config_meta,
        logging_config_meta,
        transfer_job_labels_meta,
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
