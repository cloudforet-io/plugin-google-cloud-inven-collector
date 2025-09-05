import os

from spaceone.inventory.libs.common_parser import get_data_from_yaml
from spaceone.inventory.libs.schema.cloud_service_type import (
    CloudServiceTypeMeta,
    CloudServiceTypeResource,
    CloudServiceTypeResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    DateTimeDyField,
    EnumDyField,
    ListDyField,
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

cst_build = CloudServiceTypeResource()
cst_build.name = "Build"
cst_build.provider = "google_cloud"
cst_build.group = "CloudBuild"
cst_build.service_code = "Cloud Build"
cst_build.is_primary = True
cst_build.is_major = True
cst_build.labels = ["Compute", "Developer Tools"]
cst_build.tags = {
    "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/Cloud-Build.svg",
}

cst_build._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("ID", "data.id"),
        TextDyField.data_source("Name", "data.name"),
        EnumDyField.data_source(
            "Status",
            "data.status",
            default_state={
                "safe": ["SUCCESS"],
                "warning": ["QUEUED", "WORKING"],
                "alert": ["FAILURE", "INTERNAL_ERROR", "TIMEOUT", "CANCELLED", "EXPIRED"],
            },
        ),
        TextDyField.data_source("Build Trigger ID", "data.build_trigger_id"),
        TextDyField.data_source("Service Account", "data.service_account"),
        DateTimeDyField.data_source("Create Time", "data.create_time"),
        DateTimeDyField.data_source("Start Time", "data.start_time"),
        DateTimeDyField.data_source("Finish Time", "data.finish_time"),
        ListDyField.data_source("Images", "data.images"),
        ListDyField.data_source("Tags", "data.tags"),
    ],
    search=[
        SearchField.set(name="ID", key="data.id"),
        SearchField.set(name="Name", key="data.name"),
        SearchField.set(name="Status", key="data.status"),
        SearchField.set(name="Build Trigger ID", key="data.build_trigger_id"),
        SearchField.set(name="Service Account", key="data.service_account"),
        SearchField.set(name="Create Time", key="data.create_time", data_type="datetime"),
        SearchField.set(name="Start Time", key="data.start_time", data_type="datetime"),
        SearchField.set(name="Finish Time", key="data.finish_time", data_type="datetime"),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_build}),
]
