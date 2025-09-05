import os

from spaceone.inventory.libs.common_parser import *
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    TextDyField,
    SearchField,
    DateTimeDyField,
    EnumDyField,
)
from spaceone.inventory.libs.schema.cloud_service_type import CloudServiceTypeResource, CloudServiceTypeResponse, CloudServiceTypeMeta
from spaceone.inventory.libs.schema.metadata.dynamic_widget import (
    CardWidget,
    ChartWidget,
)
from spaceone.inventory.conf.cloud_service_conf import *

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, "widget/total_count.yml")
count_by_account_conf = os.path.join(current_dir, "widget/count_by_account.yml")
count_by_serving_status_conf = os.path.join(current_dir, "widget/count_by_serving_status.yml")

# AppEngine Service
cst_app_engine_service = CloudServiceTypeResource()
cst_app_engine_service.name = "Service"
cst_app_engine_service.provider = "google_cloud"
cst_app_engine_service.group = "AppEngine"
cst_app_engine_service.service_code = "AppEngine"
cst_app_engine_service.is_primary = False
cst_app_engine_service.is_major = False
cst_app_engine_service.labels = ["Compute", "AppEngine"]
cst_app_engine_service.tags = {
    "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/App_Engine.svg",
}

cst_app_engine_service._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("Project", "data.project_id"),
        TextDyField.data_source("Service ID", "data.service_id"),
        EnumDyField.data_source("Serving Status", "data.serving_status", default_state={
            "safe": ["SERVING"],
            "warning": ["USER_DISABLED"],
            "alert": ["STOPPED"],
        }),
        TextDyField.data_source("Split", "data.split"),
        TextDyField.data_source("Version Count", "data.version_count"),
        TextDyField.data_source("Instance Count", "data.instance_count"),
        DateTimeDyField.data_source("Created", "data.create_time"),
        DateTimeDyField.data_source("Updated", "data.update_time"),
    ],
    search=[
        SearchField.set(name="Name", key="data.name"),
        SearchField.set(name="Service ID", key="data.service_id"),
        SearchField.set(name="Project", key="data.project_id"),
        SearchField.set(name="Serving Status", key="data.serving_status"),
        SearchField.set(name="Split", key="data.split"),
        SearchField.set(name="Version Count", key="data.version_count"),
        SearchField.set(name="Instance Count", key="data.instance_count"),
        SearchField.set(name="Created", key="data.create_time", data_type="datetime"),
        SearchField.set(name="Updated", key="data.update_time", data_type="datetime"),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_account_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_serving_status_conf)),
    ]
)

# Export
CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_app_engine_service}),
]
