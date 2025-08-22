import os

from spaceone.inventory.libs.common_parser import *
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    TextDyField,
    SearchField,
    DateTimeDyField,
    EnumDyField,
    SizeField,
    ListDyField,
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
count_by_version_conf = os.path.join(current_dir, "widget/count_by_version.yml")
total_node_count_conf = os.path.join(current_dir, "widget/total_node_count.yml")

# GKE Cluster (unified for v1 and v1beta)
cst_gke_cluster = CloudServiceTypeResource()
cst_gke_cluster.name = "Cluster"
cst_gke_cluster.provider = "google_cloud"
cst_gke_cluster.group = "Kubernetes Engine"
cst_gke_cluster.service_code = "Container"
cst_gke_cluster.is_primary = True
cst_gke_cluster.is_major = True
cst_gke_cluster.labels = ["Container", "Kubernetes Engine"]
cst_gke_cluster.tags = {
    "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/Google_Kubernetes_Engine.svg",
}

cst_gke_cluster._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("Location", "data.location"),
        TextDyField.data_source("Project", "data.project_id"),
        EnumDyField.data_source("Status", "data.status", default_state={
            "safe": ["RUNNING"],
            "warning": ["PROVISIONING", "RECONCILING"],
            "alert": ["STOPPING", "ERROR", "DEGRADED"],
        }),
        TextDyField.data_source("Kubernetes Version", "data.current_master_version"),
        TextDyField.data_source("Node Count", "data.current_node_count"),
        TextDyField.data_source("Node Pool Count", "data.node_pool_count"),
        TextDyField.data_source("Network", "data.network"),
        TextDyField.data_source("Subnetwork", "data.subnetwork"),
        TextDyField.data_source("Cluster IPV4 CIDR", "data.cluster_ipv4_cidr"),
        TextDyField.data_source("Services IPV4 CIDR", "data.services_ipv4_cidr"),
        DateTimeDyField.data_source("Created", "data.create_time"),
        DateTimeDyField.data_source("Updated", "data.update_time"),
        TextDyField.data_source("API Version", "data.api_version"),
        TextDyField.data_source("Fleet Info", "data.fleet_info"),
        TextDyField.data_source("Membership Info", "data.membership_info"),
    ],
    search=[
        SearchField.set(name="Cluster Name", key="data.name"),
        SearchField.set(name="Location", key="data.location"),
        SearchField.set(name="Status", key="data.status"),
        SearchField.set(name="Kubernetes Version", key="data.current_master_version"),
        SearchField.set(name="Network", key="data.network"),
        SearchField.set(name="Subnetwork", key="data.subnetwork"),
        SearchField.set(name="Project ID", key="data.project_id"),
        SearchField.set(name="Created", key="data.create_time", data_type="datetime"),
        SearchField.set(name="API Version", key="data.api_version"),
        SearchField.set(name="Fleet Info", key="data.fleet_info"),
        SearchField.set(name="Membership Info", key="data.membership_info"),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        CardWidget.set(**get_data_from_yaml(total_node_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_account_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_status_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_version_conf)),
    ]
)

# Export unified version
CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_gke_cluster}),
]
