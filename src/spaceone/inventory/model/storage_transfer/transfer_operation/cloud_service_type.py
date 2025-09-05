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

cst_transfer_operation = CloudServiceTypeResource()
cst_transfer_operation.name = "TransferOperation"
cst_transfer_operation.provider = "google_cloud"
cst_transfer_operation.group = "StorageTransfer"
cst_transfer_operation.service_code = "Storage Transfer Service"
cst_transfer_operation.is_primary = False
cst_transfer_operation.is_major = False
cst_transfer_operation.labels = ["Storage", "Transfer", "Operation"]
cst_transfer_operation.tags = {
    "spaceone:icon": f"{ASSET_URL}/Storage-Transfer.svg",
}

cst_transfer_operation._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Transfer Job", "data.transfer_job_name"),
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
        TextDyField.data_source(
            "Objects Transferred", "data.metadata.counters.objects_copied_to_sink"
        ),
        SizeField.data_source(
            "Bytes Transferred", "data.metadata.counters.bytes_copied_to_sink"
        ),
        TextDyField.data_source(
            "Objects Failed", "data.metadata.counters.objects_from_source_failed"
        ),
        TextDyField.data_source("Project ID", "data.project_id"),
    ],
    search=[
        SearchField.set(name="Operation Name", key="name"),
        SearchField.set(name="Transfer Job Name", key="data.transfer_job_name"),
        SearchField.set(name="Project ID", key="data.project_id"),
        SearchField.set(
            name="Status",
            key="data.metadata.status",
            enums={
                "IN_PROGRESS": {"label": "In Progress"},
                "PAUSED": {"label": "Paused"},
                "SUCCESS": {"label": "Success"},
                "FAILED": {"label": "Failed"},
                "ABORTED": {"label": "Aborted"},
                "QUEUED": {"label": "Queued"},
                "SUSPENDING": {"label": "Suspending"},
            },
        ),
        SearchField.set(
            name="Done",
            key="data.done",
            data_type="boolean",
        ),
        SearchField.set(
            name="Start Time", key="data.metadata.start_time", data_type="datetime"
        ),
        SearchField.set(
            name="End Time", key="data.metadata.end_time", data_type="datetime"
        ),
        SearchField.set(
            name="Objects Transferred",
            key="data.metadata.counters.objects_copied_to_sink",
            data_type="integer",
        ),
        SearchField.set(
            name="Bytes Transferred",
            key="data.metadata.counters.bytes_copied_to_sink",
            data_type="integer",
        ),
        SearchField.set(name="Account ID", key="account"),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_status_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_transfer_operation}),
]
