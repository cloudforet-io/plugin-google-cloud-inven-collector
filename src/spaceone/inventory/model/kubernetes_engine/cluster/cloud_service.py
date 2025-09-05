from schematics.types import ModelType, StringType, PolyModelType

from spaceone.inventory.model.kubernetes_engine.cluster.data import GKECluster
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    TextDyField,
    EnumDyField,
    DateTimeDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    TableDynamicLayout,
)
from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)

"""
GKE Cluster
"""
gke_cluster = ItemDynamicLayout.set_fields(
    "GKE Cluster",
    fields=[
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("Location", "data.location"),
        TextDyField.data_source("Project ID", "data.project_id"),
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
        TextDyField.data_source("Node Pool Count", "data.node_pool_count"),
        TextDyField.data_source("Network", "data.network"),
        TextDyField.data_source("Subnetwork", "data.subnetwork"),
        TextDyField.data_source("Cluster IPV4 CIDR", "data.cluster_ipv4_cidr"),
        TextDyField.data_source("Services IPV4 CIDR", "data.services_ipv4_cidr"),
        DateTimeDyField.data_source("Created", "data.create_time"),
        DateTimeDyField.data_source("Updated", "data.update_time"),
        TextDyField.data_source("API Version", "data.api_version"),
    ],
)

# Node Pools 정보는 별도 NodePool 서비스로 분리됨

network_config = ItemDynamicLayout.set_fields(
    "Network Configuration",
    fields=[
        TextDyField.data_source("Network", "data.network_config.network"),
        TextDyField.data_source("Subnetwork", "data.network_config.subnetwork"),
        EnumDyField.data_source(
            "Intra Node Visibility",
            "data.network_config.enable_intra_node_visibility",
            default_badge={"indigo.500": ["true"], "coral.600": ["false"]},
        ),
        EnumDyField.data_source(
            "L4 ILB Subsetting",
            "data.network_config.enable_l4ilb_subsetting",
            default_badge={"indigo.500": ["true"], "coral.600": ["false"]},
        ),
    ],
)

addons_config = ItemDynamicLayout.set_fields(
    "Addons Configuration",
    fields=[
        EnumDyField.data_source(
            "HTTP Load Balancing",
            "data.addons_config.http_load_balancing.disabled",
            default_badge={"indigo.500": ["false"], "coral.600": ["true"]},
        ),
        EnumDyField.data_source(
            "Horizontal Pod Autoscaling",
            "data.addons_config.horizontal_pod_autoscaling.disabled",
            default_badge={"indigo.500": ["false"], "coral.600": ["true"]},
        ),
        EnumDyField.data_source(
            "Kubernetes Dashboard",
            "data.addons_config.kubernetes_dashboard.disabled",
            default_badge={"indigo.500": ["false"], "coral.600": ["true"]},
        ),
        EnumDyField.data_source(
            "Network Policy",
            "data.addons_config.network_policy_config.disabled",
            default_badge={"indigo.500": ["false"], "coral.600": ["true"]},
        ),
    ],
)

labels = TableDynamicLayout.set_fields(
    "Labels",
    root_path="data.resource_labels",
    fields=[
        TextDyField.data_source("Key", "key"),
        TextDyField.data_source("Value", "value"),
    ],
)

gke_cluster_meta = CloudServiceMeta.set_layouts(
    [gke_cluster, network_config, addons_config, labels]
)


class KubernetesEngineResource(CloudServiceResource):
    cloud_service_group = StringType(default="KubernetesEngine")


class GKEClusterResource(KubernetesEngineResource):
    cloud_service_type = StringType(default="Cluster")
    data = ModelType(GKECluster)
    _metadata = ModelType(
        CloudServiceMeta, default=gke_cluster_meta, serialized_name="metadata"
    )


class GKEClusterResponse(CloudServiceResponse):
    resource = PolyModelType(GKEClusterResource)
