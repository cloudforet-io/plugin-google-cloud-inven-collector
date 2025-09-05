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
count_by_status_conf = os.path.join(current_dir, "widget/count_by_status.yml")
count_by_source_type_conf = os.path.join(current_dir, "widget/count_by_source_type.yml")

cst_transfer_job = CloudServiceTypeResource()
cst_transfer_job.name = "TransferJob"
cst_transfer_job.provider = "google_cloud"
cst_transfer_job.group = "StorageTransfer"
cst_transfer_job.service_code = "Storage Transfer Service"
cst_transfer_job.is_primary = True
cst_transfer_job.is_major = True
cst_transfer_job.labels = ["Storage", "Transfer", "Migration"]
cst_transfer_job.tags = {
    "spaceone:icon": f"{ASSET_URL}/Storage-Transfer.svg",
}

cst_transfer_job._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
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
        EnumDyField.data_source(
            "Last Execution Status",
            "data.last_execution_status",
            default_state={
                "safe": ["SUCCESS"],
                "warning": ["IN_PROGRESS", "PAUSED", "QUEUED"],
                "alert": ["FAILED", "ABORTED"],
            },
        ),
        TextDyField.data_source(
            "Total Objects Transferred", "data.total_objects_transferred"
        ),
        SizeField.data_source(
            "Total Bytes Transferred", "data.total_bytes_transferred"
        ),
        TextDyField.data_source("Total Objects Failed", "data.total_objects_failed"),
        TextDyField.data_source("Latest Operation", "data.latest_operation_name"),
        DateTimeDyField.data_source("Created", "data.creation_time"),
        DateTimeDyField.data_source("Last Modified", "data.last_modification_time"),
        # Optional fields
        TextDyField.data_source(
            "Pub/Sub Topic",
            "data.notification_config.pubsub_topic",
            options={"is_optional": True},
        ),
        DateTimeDyField.data_source(
            "Deleted", "data.deletion_time", options={"is_optional": True}
        ),
    ],
    search=[
        SearchField.set(name="Transfer Job Name", key="name"),
        SearchField.set(name="Project ID", key="data.project_id"),
        SearchField.set(
            name="Status",
            key="data.status",
            enums={
                "ENABLED": {"label": "Enabled"},
                "DISABLED": {"label": "Disabled"},
                "DELETED": {"label": "Deleted"},
            },
        ),
        SearchField.set(name="Source Type", key="data.source_type"),
        SearchField.set(name="Sink Type", key="data.sink_type"),
        SearchField.set(
            name="Last Execution Status",
            key="data.last_execution_status",
            enums={
                "SUCCESS": {"label": "Success"},
                "FAILED": {"label": "Failed"},
                "IN_PROGRESS": {"label": "In Progress"},
                "PAUSED": {"label": "Paused"},
                "ABORTED": {"label": "Aborted"},
                "QUEUED": {"label": "Queued"},
                "SUSPENDING": {"label": "Suspending"},
            },
        ),
        SearchField.set(
            name="Total Objects Transferred",
            key="data.total_objects_transferred",
            data_type="integer",
        ),
        SearchField.set(
            name="Total Bytes Transferred",
            key="data.total_bytes_transferred",
            data_type="integer",
        ),
        SearchField.set(
            name="Total Objects Failed",
            key="data.total_objects_failed",
            data_type="integer",
        ),
        SearchField.set(
            name="Creation Time", key="data.creation_time", data_type="datetime"
        ),
        SearchField.set(
            name="Last Modification Time",
            key="data.last_modification_time",
            data_type="datetime",
        ),
        SearchField.set(
            name="Pub/Sub Topic", key="data.notification_config.pubsub_topic"
        ),
        SearchField.set(name="Account ID", key="account"),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_status_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_source_type_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_transfer_job}),
]
