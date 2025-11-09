import os

from spaceone.inventory.conf.cloud_service_conf import *
from spaceone.inventory.conf.cloud_service_conf import ASSET_URL
from spaceone.inventory.libs.common_parser import *
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
count_by_account_conf = os.path.join(current_dir, "widget/count_by_account.yml")
count_by_serving_status_conf = os.path.join(
    current_dir, "widget/count_by_serving_status.yml"
)

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
    "spaceone:icon": f"{ASSET_URL}/App-Engine.svg",
}

cst_app_engine_service._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Service", "data.name"),
        TextDyField.data_source("Service ID", "data.service_id"),
        EnumDyField.data_source(
            "Serving Status",
            "data.serving_status",
            default_state={
                "safe": ["SERVING"],
                "warning": ["USER_DISABLED", "STOPPED"],
                "alert": ["SYSTEM_DISABLED"],
            },
        ),
        TextDyField.data_source("Versions", "data.version_count"),
        TextDyField.data_source("Instance Count", "data.instance_count"),
        TextDyField.data_source("Labels", "data.labels"),
        TextDyField.data_source("VPC Access Name", "data.vpc_access_connector.name"),
        TextDyField.data_source(
            "VPC Egress Setting", "data.vpc_access_connector.egress_setting"
        ),
        TextDyField.data_source(
            "Last Version Deployed", "data.latest_version_deployed"
        ),
    ],
    search=[
        SearchField.set(name="Service", key="data.name"),
        SearchField.set(name="Service ID", key="data.service_id"),
        SearchField.set(name="Project", key="data.project_id"),
        SearchField.set(name="Serving Status", key="data.serving_status"),
        SearchField.set(name="Versions", key="data.version_count"),
        SearchField.set(name="Instance Count", key="data.instance_count"),
        SearchField.set(name="Labels", key="data.labels"),
        SearchField.set(name="VPC Access Name", key="data.vpc_access_connector.name"),
        SearchField.set(
            name="Last Version Deployed", key="data.latest_version_deployed"
        ),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_account_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_serving_status_conf)),
    ],
)

# Export
CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_app_engine_service}),
]

# Export
CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_app_engine_service}),
]
