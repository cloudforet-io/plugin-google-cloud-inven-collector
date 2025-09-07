import os

from spaceone.inventory.conf.cloud_service_conf import ASSET_URL
from spaceone.inventory.libs.schema.cloud_service_type import (
    CloudServiceTypeMeta,
    CloudServiceTypeResource,
    CloudServiceTypeResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    SearchField,
    TextDyField,
)

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, "widget/total_count.yml")
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yml")
count_by_project_conf = os.path.join(current_dir, "widget/count_by_project.yml")

cst_service = CloudServiceTypeResource()
cst_service.name = "ServiceV1"
cst_service.provider = "google_cloud"
cst_service.group = "CloudRun"
cst_service.service_code = "Cloud Run"
cst_service.labels = ["Serverless"]
cst_service.is_primary = True
cst_service.is_major = True
cst_service.tags = {
    "spaceone:icon": f"{ASSET_URL}/Cloud-Run.svg",
}

cst_service._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Service Name", "data.metadata.name"),
        TextDyField.data_source("Location", "data.location"),
        TextDyField.data_source("Project", "data.project"),
        TextDyField.data_source("URL", "data.status.url"),
        TextDyField.data_source(
            "Latest Ready Revision", "data.status.latest_ready_revision_name"
        ),
        TextDyField.data_source("Revision Count", "data.revision_count"),
    ],
    search=[
        SearchField.set(name="Name", key="data.metadata.name"),
        SearchField.set(name="Service Name", key="data.metadata.name"),
        SearchField.set(name="Service ID", key="data.metadata.uid"),
        SearchField.set(name="Location", key="data.location"),
        SearchField.set(name="Project", key="data.project"),
        SearchField.set(name="URL", key="data.status.url"),
        SearchField.set(name="Latest Ready Revision", key="data.status.latest_ready_revision_name"),
    ],
    widget=[
        # CardWidget.set(**get_data_from_yaml(total_count_conf)),
        # ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        # ChartWidget.set(**get_data_from_yaml(count_by_project_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_service}),
]
