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

cst_connection = CloudServiceTypeResource()
cst_connection.name = "Connection"
cst_connection.provider = "google_cloud"
cst_connection.group = "CloudBuild"
cst_connection.service_code = "Cloud Build"
cst_connection.is_primary = True
cst_connection.is_major = True
cst_connection.labels = ["Compute", "Developer Tools"]
cst_connection.tags = {
    "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/Cloud-Build.svg",
}

cst_connection._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("UID", "data.uid"),
        EnumDyField.data_source(
            "Disabled",
            "data.disabled",
            default_state={
                "safe": [False],
                "alert": [True],
            },
        ),
        EnumDyField.data_source(
            "Reconciling",
            "data.reconciling",
            default_state={
                "safe": [False],
                "warning": [True],
            },
        ),
        DateTimeDyField.data_source("Create Time", "data.create_time"),
        DateTimeDyField.data_source("Update Time", "data.update_time"),
    ],
    search=[
        SearchField.set(name="Name", key="data.name"),
        SearchField.set(name="UID", key="data.uid"),
        SearchField.set(name="Disabled", key="data.disabled", data_type="boolean"),
        SearchField.set(
            name="Reconciling", key="data.reconciling", data_type="boolean"
        ),
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
    CloudServiceTypeResponse({"resource": cst_connection}),
]
