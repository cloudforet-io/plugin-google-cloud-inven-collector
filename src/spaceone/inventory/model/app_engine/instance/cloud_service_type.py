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
count_by_vm_status_conf = os.path.join(current_dir, "widget/count_by_vm_status.yml")
total_memory_usage_conf = os.path.join(current_dir, "widget/total_memory_usage.yml")
total_cpu_usage_conf = os.path.join(current_dir, "widget/total_cpu_usage.yml")

# AppEngine Instance
cst_app_engine_instance = CloudServiceTypeResource()
cst_app_engine_instance.name = "Instance"
cst_app_engine_instance.provider = "google_cloud"
cst_app_engine_instance.group = "AppEngine"
cst_app_engine_instance.service_code = "AppEngine"
cst_app_engine_instance.is_primary = False
cst_app_engine_instance.is_major = False
cst_app_engine_instance.labels = ["Compute", "AppEngine"]
cst_app_engine_instance.tags = {
    "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/App_Engine.svg",
}

cst_app_engine_instance._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("Project", "data.project_id"),
        TextDyField.data_source("Service ID", "data.service_id"),
        TextDyField.data_source("Version ID", "data.version_id"),
        TextDyField.data_source("Instance ID", "data.instance_id"),
        EnumDyField.data_source("VM Status", "data.vm_status", default_state={
            "safe": ["RUNNING"],
            "warning": ["PENDING", "STAGING"],
            "alert": ["STOPPED", "TERMINATED"],
        }),
        TextDyField.data_source("VM Debug Enabled", "data.vm_debug_enabled"),
        TextDyField.data_source("VM Liveness", "data.vm_liveness"),
        TextDyField.data_source("Request Count", "data.request_count"),
        TextDyField.data_source("Memory Usage", "data.memory_usage"),
        TextDyField.data_source("CPU Usage", "data.cpu_usage"),
        DateTimeDyField.data_source("Created", "data.create_time"),
        DateTimeDyField.data_source("Updated", "data.update_time"),
    ],
    search=[
        SearchField.set(name="Name", key="data.name"),
        SearchField.set(name="Instance ID", key="data.instance_id"),
        SearchField.set(name="Service ID", key="data.service_id"),
        SearchField.set(name="Version ID", key="data.version_id"),
        SearchField.set(name="Project", key="data.project_id"),
        SearchField.set(name="VM Status", key="data.vm_status"),
        SearchField.set(name="VM Debug Enabled", key="data.vm_debug_enabled"),
        SearchField.set(name="VM Liveness", key="data.vm_liveness"),
        SearchField.set(name="Request Count", key="data.request_count"),
        SearchField.set(name="Created", key="data.create_time", data_type="datetime"),
        SearchField.set(name="Updated", key="data.update_time", data_type="datetime"),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_account_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_vm_status_conf)),
        CardWidget.set(**get_data_from_yaml(total_memory_usage_conf)),
        CardWidget.set(**get_data_from_yaml(total_cpu_usage_conf)),
    ]
)

# Export
CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_app_engine_instance}),
]
