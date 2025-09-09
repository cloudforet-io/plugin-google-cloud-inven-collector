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

cst_service = CloudServiceTypeResource()
cst_service.name = "Route"
cst_service.provider = "google_cloud"
cst_service.group = "CloudRun"
cst_service.service_code = "Cloud Run"
cst_service.labels = ["Serverless"]
cst_service.is_primary = True
cst_service.is_major = True
cst_service.tags = {
    "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/Cloud-Run.svg",
}

cst_service._metadata = CloudServiceTypeMeta.set_meta(
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
        TextDyField.data_source("URL", "data.status.address.url"),
        TextDyField.data_source("Namespace", "data.metadata.namespace"),
        TextDyField.data_source(
            "Latest Ready Revision", "data.latest_ready_revision_name"
        ),
        TextDyField.data_source("Revision Count", "data.revision_count"),
    ],
    search=[
        SearchField.set(name="Name", key="data.metadata.name"),
        SearchField.set(name="Status", key="data.status.conditions.0.status"),
        SearchField.set(name="URL", key="data.status.address.url"),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_service}),
]
