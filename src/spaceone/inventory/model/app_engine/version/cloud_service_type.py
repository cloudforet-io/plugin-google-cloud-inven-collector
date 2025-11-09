import os
from spaceone.inventory.conf.cloud_service_conf import ASSET_URL
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
count_by_runtime_conf = os.path.join(current_dir, "widget/count_by_runtime.yml")
count_by_environment_conf = os.path.join(current_dir, "widget/count_by_environment.yml")

# AppEngine Version
cst_app_engine_version = CloudServiceTypeResource()
cst_app_engine_version.name = "Version"
cst_app_engine_version.provider = "google_cloud"
cst_app_engine_version.group = "AppEngine"
cst_app_engine_version.service_code = "AppEngine"
cst_app_engine_version.is_primary = False
cst_app_engine_version.is_major = False
cst_app_engine_version.labels = ["Compute", "AppEngine"]
cst_app_engine_version.tags = {
    "spaceone:icon": f"{ASSET_URL}/App-Engine.svg",
}

cst_app_engine_version._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Service ID", "data.service_id"),
        TextDyField.data_source("Version ID", "data.version_id"),
        EnumDyField.data_source("Serving Status", "data.serving_status", default_state={
            "safe": ["SERVING"],
            "warning": ["USER_DISABLED"],
            "alert": ["STOPPED"],
        }),
        TextDyField.data_source("Runtime", "data.runtime"),
        TextDyField.data_source("Environment", "data.environment"),
        EnumDyField.data_source("Scaling Type", "data.scaling_type", default_state={
            "safe": ["Automatic"],
            "warning": ["Manual"],
            "alert": ["Basic"],
            "disable": ["Unknown"],
        }),
        TextDyField.data_source("Instance Count", "data.instance_count"),
        TextDyField.data_source("Memory Usage", "data.memory_usage"),
        TextDyField.data_source("CPU Usage", "data.cpu_usage"),
        DateTimeDyField.data_source("Created", "data.create_time"),
    ],
    search=[
        SearchField.set(name="Name", key="data.name"),
        SearchField.set(name="Version ID", key="data.version_id"),
        SearchField.set(name="Service ID", key="data.service_id"),
        SearchField.set(name="Project", key="data.project_id"),
        SearchField.set(name="Serving Status", key="data.serving_status"),
        SearchField.set(name="Runtime", key="data.runtime"),
        SearchField.set(name="Environment", key="data.environment"),
        SearchField.set(name="Scaling Type", key="data.scaling_type"),
        SearchField.set(name="Instance Count", key="data.instance_count"),
        SearchField.set(name="Created", key="data.create_time", data_type="datetime"),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_account_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_runtime_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_environment_conf)),
    ]
)

# Export
CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_app_engine_version}),
]
