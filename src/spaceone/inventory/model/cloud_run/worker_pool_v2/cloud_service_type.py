import os

from spaceone.inventory.conf.cloud_service_conf import ASSET_URL
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

cst_worker_pool = CloudServiceTypeResource()
cst_worker_pool.name = "WorkerPool"
cst_worker_pool.provider = "google_cloud"
cst_worker_pool.group = "CloudRun"
cst_worker_pool.service_code = "Cloud Run"
cst_worker_pool.labels = ["Serverless"]
cst_worker_pool.is_primary = True
cst_worker_pool.is_major = True
cst_worker_pool.tags = {
    "spaceone:icon": f"{ASSET_URL}/Cloud-Run.svg",
}

cst_worker_pool._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        EnumDyField.data_source(
            "Status",
            "data.status.conditions.0.status",
            default_state={
                "safe": ["True"],
                "warning": ["False"],
                "alert": ["Unknown"],
            },
        ),
        TextDyField.data_source("Worker Pool Name", "data.metadata.name"),
        TextDyField.data_source("Location", "data.metadata.location"),
        TextDyField.data_source("Project", "data.metadata.project"),
        TextDyField.data_source("Revision Count", "data.revision_count"),
    ],
    search=[
        SearchField.set(name="Worker Pool Name", key="data.metadata.name"),
        SearchField.set(name="Worker Pool ID", key="data.metadata.uid"),
        SearchField.set(name="Location", key="data.metadata.location"),
        SearchField.set(name="Project", key="data.metadata.project"),
        SearchField.set(name="Status", key="data.status.conditions.0.status"),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_worker_pool}),
]
