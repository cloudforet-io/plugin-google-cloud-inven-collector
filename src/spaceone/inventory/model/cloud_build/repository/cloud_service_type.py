import os

from spaceone.inventory.libs.common_parser import get_data_from_yaml
from spaceone.inventory.libs.schema.cloud_service_type import (
    CloudServiceTypeMeta,
    CloudServiceTypeResource,
    CloudServiceTypeResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    DateTimeDyField,
    SearchField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_widget import (
    CardWidget,
    ChartWidget,
)

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, "widget/total_count.yaml")
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yaml")
count_by_project_conf = os.path.join(current_dir, "widget/count_by_project.yaml")

cst_repository = CloudServiceTypeResource()
cst_repository.name = "Repository"
cst_repository.provider = "google_cloud"
cst_repository.group = "CloudBuild"
cst_repository.service_code = "Cloud Build"
cst_repository.is_primary = True
cst_repository.is_major = True
cst_repository.labels = ["Compute", "Developer Tools"]
cst_repository.tags = {
    "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/Cloud-Build.svg",
}

cst_repository._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("Remote URI", "data.remote_uri"),
        TextDyField.data_source("UID", "data.uid"),
        TextDyField.data_source("Webhook ID", "data.webhook_id"),
        DateTimeDyField.data_source("Create Time", "data.create_time"),
        DateTimeDyField.data_source("Update Time", "data.update_time"),
    ],
    search=[
        SearchField.set(name="Name", key="data.name"),
        SearchField.set(name="Remote URI", key="data.remote_uri"),
        SearchField.set(name="UID", key="data.uid"),
        SearchField.set(name="Webhook ID", key="data.webhook_id"),
        SearchField.set(
            name="Create Time", key="data.create_time", data_type="datetime"
        ),
        SearchField.set(
            name="Update Time", key="data.update_time", data_type="datetime"
        ),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_repository}),
]
