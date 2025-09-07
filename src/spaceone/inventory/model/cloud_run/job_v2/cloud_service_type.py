import os

from spaceone.inventory.libs.common_parser import get_data_from_yaml
from spaceone.inventory.libs.schema.cloud_service_type import (
    CloudServiceTypeMeta,
    CloudServiceTypeResource,
    CloudServiceTypeResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
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
count_by_project_conf = os.path.join(current_dir, "widget/count_by_project.yml")

cst_job = CloudServiceTypeResource()
cst_job.name = "Job"
cst_job.provider = "google_cloud"
cst_job.group = "CloudRun"
cst_job.service_code = "Cloud Run"
cst_job.labels = ["Serverless"]
cst_job.is_primary = True
cst_job.is_major = True
cst_job.tags = {
    "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/Cloud-Run.svg",
}

cst_job._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        EnumDyField.data_source(
            "Status",
            "data.terminal_condition.state",
            default_state={
                "safe": ["CONDITION_SUCCEEDED"],
                "warning": ["CONDITION_PENDING"],
                "alert": ["CONDITION_FAILED"],
            },
        ),
        TextDyField.data_source("Location", "data.location"),
        TextDyField.data_source("Project", "data.project"),
        TextDyField.data_source("Execution Count", "data.execution_count"),
        TextDyField.data_source(
            "Latest Created Execution", "data.latest_created_execution.name"
        ),
    ],
    search=[
        SearchField.set(name="Name", key="data.name"),
        SearchField.set(name="Job ID", key="data.uid"),
        SearchField.set(name="Location", key="data.location"),
        SearchField.set(name="Project", key="data.project"),
        SearchField.set(name="Status", key="data.terminal_condition.state"),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_job}),
]
