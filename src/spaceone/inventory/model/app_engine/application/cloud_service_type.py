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
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yml")
count_by_account_conf = os.path.join(current_dir, "widget/count_by_account.yml")
count_by_serving_status_conf = os.path.join(current_dir, "widget/count_by_serving_status.yml")

# AppEngine Application
cst_app_engine_application = CloudServiceTypeResource()
cst_app_engine_application.name = "Application"
cst_app_engine_application.provider = "google_cloud"
cst_app_engine_application.group = "AppEngine"
cst_app_engine_application.service_code = "AppEngine"
cst_app_engine_application.is_primary = True
cst_app_engine_application.is_major = True
cst_app_engine_application.labels = ["Compute", "AppEngine"]
cst_app_engine_application.tags = {
    "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/App_Engine.svg",
}

cst_app_engine_application._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("Project", "data.project_id"),
        TextDyField.data_source("Location", "data.location_id"),
        EnumDyField.data_source("Serving Status", "data.serving_status", default_state={
            "safe": ["SERVING"],
            "warning": ["USER_DISABLED"],
            "alert": ["STOPPED"],
        }),
        TextDyField.data_source("Default Hostname", "data.default_hostname"),
        TextDyField.data_source("Default Cookie Expiration", "data.default_cookie_expiration"),
        TextDyField.data_source("Code Bucket", "data.code_bucket"),
        TextDyField.data_source("GCR Domain", "data.gcr_domain"),
        TextDyField.data_source("Database Type", "data.database_type"),
        TextDyField.data_source("Feature Settings", "data.feature_settings"),
        DateTimeDyField.data_source("Created", "data.create_time"),
        DateTimeDyField.data_source("Updated", "data.update_time"),
    ],
    search=[
        SearchField.set(name="Name", key="data.name"),
        SearchField.set(name="Project", key="data.project_id"),
        SearchField.set(name="Location", key="data.location_id"),
        SearchField.set(name="Serving Status", key="data.serving_status"),
        SearchField.set(name="Default Hostname", key="data.default_hostname"),
        SearchField.set(name="Code Bucket", key="data.code_bucket"),
        SearchField.set(name="GCR Domain", key="data.gcr_domain"),
        SearchField.set(name="Database Type", key="data.database_type"),
        SearchField.set(name="Created", key="data.create_time", data_type="datetime"),
        SearchField.set(name="Updated", key="data.update_time", data_type="datetime"),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_account_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_serving_status_conf)),
    ]
)

# Export
CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_app_engine_application}),
]
