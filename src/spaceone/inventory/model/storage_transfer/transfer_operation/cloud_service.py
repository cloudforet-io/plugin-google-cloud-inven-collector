from schematics.types import ModelType, PolyModelType, StringType

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
from spaceone.inventory.model.storage_transfer.transfer_operation.data import (
    TransferOperation,
)

"""
Transfer Operation
"""

# TAB - Operation Configuration
operation_configuration_meta = ItemDynamicLayout.set_fields(
    "Configuration",
    fields=[
        TextDyField.data_source("Operation Name", "name"),
        TextDyField.data_source("Transfer Job", "data.transfer_job_name"),
        TextDyField.data_source("Project ID", "data.project_id"),
        EnumDyField.data_source(
            "Status",
            "data.metadata.status",
            default_state={
                "safe": ["SUCCESS"],
                "warning": ["IN_PROGRESS", "PAUSED", "QUEUED", "SUSPENDING"],
                "alert": ["FAILED", "ABORTED"],
            },
        ),
        EnumDyField.data_source(
            "Done",
            "data.done",
            default_badge={"indigo.500": ["true"], "coral.600": ["false"]},
        ),
        DateTimeDyField.data_source("Start Time", "data.metadata.start_time"),
        DateTimeDyField.data_source("End Time", "data.metadata.end_time"),
        TextDyField.data_source("Duration", "data.duration"),
    ],
)

# TAB - Transfer Counters
transfer_counters_meta = ItemDynamicLayout.set_fields(
    "Transfer Statistics",
    fields=[
        TextDyField.data_source(
            "Objects Found", "data.metadata.counters.objects_found_from_source"
        ),
        SizeField.data_source(
            "Bytes Found", "data.metadata.counters.bytes_found_from_source"
        ),
        TextDyField.data_source(
            "Objects Transferred", "data.metadata.counters.objects_copied_to_sink"
        ),
        SizeField.data_source(
            "Bytes Transferred", "data.metadata.counters.bytes_copied_to_sink"
        ),
        TextDyField.data_source(
            "Objects Failed", "data.metadata.counters.objects_from_source_failed"
        ),
        SizeField.data_source(
            "Bytes Failed", "data.metadata.counters.bytes_from_source_failed"
        ),
    ],
)

# TAB - Error Breakdowns
error_breakdowns_meta = TableDynamicLayout.set_fields(
    "Error Breakdowns",
    root_path="data.metadata.error_breakdowns",
    fields=[
        TextDyField.data_source("Error Code", "error_code"),
        TextDyField.data_source("Error Count", "error_count"),
    ],
)

# TAB - Labels
operation_labels_meta = TableDynamicLayout.set_fields(
    "Labels",
    root_path="data.labels",
    fields=[
        TextDyField.data_source("Key", "key"),
        TextDyField.data_source("Value", "value"),
    ],
)

transfer_operation_meta = CloudServiceMeta.set_layouts(
    [
        operation_configuration_meta,
        transfer_counters_meta,
        error_breakdowns_meta,
        operation_labels_meta,
    ]
)


class StorageTransferResource(CloudServiceResource):
    cloud_service_group = StringType(default="StorageTransfer")


class TransferOperationResource(StorageTransferResource):
    cloud_service_type = StringType(default="TransferOperation")
    data = ModelType(TransferOperation)
    _metadata = ModelType(
        CloudServiceMeta, default=transfer_operation_meta, serialized_name="metadata"
    )


class TransferOperationResponse(CloudServiceResponse):
    resource = PolyModelType(TransferOperationResource)
