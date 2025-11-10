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

total_count_conf = os.path.join(current_dir, "widget/total_count.yml")
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yml")
count_by_account_conf = os.path.join(current_dir, "widget/count_by_account.yml")
count_by_status_conf = os.path.join(current_dir, "widget/count_by_status.yml")
count_by_version_conf = os.path.join(current_dir, "widget/count_by_version.yml")

# GKE Cluster (unified for v1 and v1beta)
cst_gke_cluster = CloudServiceTypeResource()
cst_gke_cluster.name = "Cluster"
cst_gke_cluster.provider = "google_cloud"
cst_gke_cluster.group = "KubernetesEngine"
cst_gke_cluster.service_code = "KubernetesEngine"
cst_gke_cluster.is_primary = True
cst_gke_cluster.is_major = True
cst_gke_cluster.labels = ["Container", "KubernetesEngine"]
cst_gke_cluster.tags = {
    "spaceone:icon": f"{ASSET_URL}/Google-Kubernetes-Engine.svg",
}

cst_gke_cluster._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Location", "data.location"),
        EnumDyField.data_source(
            "Status",
            "data.status",
            default_state={
                "safe": ["RUNNING"],
                "warning": ["PROVISIONING", "RECONCILING"],
                "alert": ["STOPPING", "ERROR", "DEGRADED"],
            },
        ),
        TextDyField.data_source("Kubernetes Version", "data.current_master_version"),
        TextDyField.data_source("Node Count", "data.current_node_count"),
        TextDyField.data_source("Network", "data.network"),
        TextDyField.data_source("Subnetwork", "data.subnetwork"),
        TextDyField.data_source("Cluster IPV4 CIDR", "data.cluster_ipv4_cidr"),
        TextDyField.data_source("Services IPV4 CIDR", "data.services_ipv4_cidr"),
        DateTimeDyField.data_source("Created", "data.create_time"),
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
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_account_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_status_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_version_conf)),
    ],
)

# Export unified version
CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_gke_cluster}),
]
