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
count_by_status_conf = os.path.join(current_dir, "widget/count_by_status.yml")
count_by_machine_type_conf = os.path.join(current_dir, "widget/count_by_machine_type.yml")
total_node_count_conf = os.path.join(current_dir, "widget/total_node_count.yml")

# GKE NodePool
cst_gke_node_pool = CloudServiceTypeResource()
cst_gke_node_pool.name = "NodePool"
cst_gke_node_pool.provider = "google_cloud"
cst_gke_node_pool.group = "KubernetesEngine"
cst_gke_node_pool.service_code = "Container"
cst_gke_node_pool.is_primary = False
cst_gke_node_pool.is_major = False
cst_gke_node_pool.labels = ["Container", "KubernetesEngine"]
cst_gke_node_pool.tags = {
    "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/Kubernetes_Engine.svg",
}

cst_gke_node_pool._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("Cluster Name", "data.cluster_name"),
        TextDyField.data_source("Location", "data.location"),
        TextDyField.data_source("Project", "data.project_id"),
        EnumDyField.data_source("Status", "data.status", default_state={
            "safe": ["RUNNING"],
            "warning": ["PROVISIONING", "RECONCILING"],
            "alert": ["STOPPING", "ERROR", "DEGRADED"],
        }),
        TextDyField.data_source("Node Count", "data.initial_node_count"),
        TextDyField.data_source("Machine Type", "data.config.machine_type"),
        TextDyField.data_source("Disk Size (GB)", "data.config.disk_size_gb"),
        TextDyField.data_source("Disk Type", "data.config.disk_type"),
        TextDyField.data_source("Image Type", "data.config.image_type"),
        TextDyField.data_source("Preemptible", "data.config.preemptible"),
        TextDyField.data_source("Autoscaling Enabled", "data.autoscaling.enabled"),
        TextDyField.data_source("Min Node Count", "data.autoscaling.min_node_count"),
        TextDyField.data_source("Max Node Count", "data.autoscaling.max_node_count"),
        TextDyField.data_source("Auto Upgrade", "data.management.auto_upgrade"),
        TextDyField.data_source("Auto Repair", "data.management.auto_repair"),
        DateTimeDyField.data_source("Created", "data.create_time"),
        DateTimeDyField.data_source("Updated", "data.update_time"),
        TextDyField.data_source("API Version", "data.api_version"),
    ],
    search=[
        SearchField.set(name="NodePool Name", key="data.name"),
        SearchField.set(name="Cluster Name", key="data.cluster_name"),
        SearchField.set(name="Location", key="data.location"),
        SearchField.set(name="Status", key="data.status"),
        SearchField.set(name="Machine Type", key="data.config.machine_type"),
        SearchField.set(name="Image Type", key="data.config.image_type"),
        SearchField.set(name="Project ID", key="data.project_id"),
        SearchField.set(name="Preemptible", key="data.config.preemptible"),
        SearchField.set(name="Created", key="data.create_time", data_type="datetime"),
        SearchField.set(name="Updated", key="data.update_time", data_type="datetime"),
        SearchField.set(name="API Version", key="data.api_version"),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        CardWidget.set(**get_data_from_yaml(total_node_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_account_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_status_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_machine_type_conf)),
    ]
)

# Export
CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_gke_node_pool}),
]
