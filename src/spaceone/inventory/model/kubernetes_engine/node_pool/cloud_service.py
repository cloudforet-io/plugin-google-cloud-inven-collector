from schematics.types import (
    ModelType,
    StringType,
    PolyModelType,
)

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.model.kubernetes_engine.node_pool.data import NodePool
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    EnumDyField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    TableDynamicLayout,
)


"""
Node Pool
"""
node_pool_overview = ItemDynamicLayout.set_fields(
    "Node Pool Overview",
    fields=[
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("Cluster Name", "data.cluster_name"),
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
        TextDyField.data_source("Initial Node Count", "data.initial_node_count"),
        TextDyField.data_source("Total Nodes", "data.total_nodes"),
        TextDyField.data_source("Version", "data.version"),
    ],
)

node_configuration = ItemDynamicLayout.set_fields(
    "Node Configuration",
    fields=[
        TextDyField.data_source("Machine Type", "data.config.machine_type"),
        TextDyField.data_source("Disk Size (GB)", "data.config.disk_size_gb"),
        TextDyField.data_source("Disk Type", "data.config.disk_type"),
        TextDyField.data_source("Image Type", "data.config.image_type"),
        EnumDyField.data_source(
            "Preemptible",
            "data.config.preemptible",
            default_badge={"indigo.500": ["true"], "coral.600": ["false"]},
        ),
        EnumDyField.data_source(
            "Spot",
            "data.config.spot",
            default_badge={"indigo.500": ["true"], "coral.600": ["false"]},
        ),
        TextDyField.data_source("Service Account", "data.config.service_account"),
        TextDyField.data_source("Min CPU Platform", "data.config.min_cpu_platform"),
        TextDyField.data_source("Local SSD Count", "data.config.local_ssd_count"),
    ],
)

autoscaling_config = ItemDynamicLayout.set_fields(
    "Autoscaling Configuration",
    fields=[
        EnumDyField.data_source(
            "Enabled",
            "data.autoscaling.enabled",
            default_badge={"indigo.500": ["true"], "coral.600": ["false"]},
        ),
        TextDyField.data_source("Min Node Count", "data.autoscaling.min_node_count"),
        TextDyField.data_source("Max Node Count", "data.autoscaling.max_node_count"),
        TextDyField.data_source("Total Min Node Count", "data.autoscaling.total_min_node_count"),
        TextDyField.data_source("Total Max Node Count", "data.autoscaling.total_max_node_count"),
        TextDyField.data_source("Location Policy", "data.autoscaling.location_policy"),
    ],
)

management_config = ItemDynamicLayout.set_fields(
    "Management Configuration",
    fields=[
        EnumDyField.data_source(
            "Auto Upgrade",
            "data.management.auto_upgrade",
            default_badge={"indigo.500": ["true"], "coral.600": ["false"]},
        ),
        EnumDyField.data_source(
            "Auto Repair",
            "data.management.auto_repair",
            default_badge={"indigo.500": ["true"], "coral.600": ["false"]},
        ),
    ],
)

network_configuration = ItemDynamicLayout.set_fields(
    "Network Configuration",
    fields=[
        TextDyField.data_source("Pod Range", "data.network_config.pod_range"),
        TextDyField.data_source("Pod IPv4 CIDR Block", "data.network_config.pod_ipv4_cidr_block"),
        EnumDyField.data_source(
            "Create Pod Range",
            "data.network_config.create_pod_range",
            default_badge={"indigo.500": ["true"], "coral.600": ["false"]},
        ),
        EnumDyField.data_source(
            "Enable Private Nodes",
            "data.network_config.enable_private_nodes",
            default_badge={"indigo.500": ["true"], "coral.600": ["false"]},
        ),
        TextDyField.data_source("Pod IPv4 CIDR Size", "data.pod_ipv4_cidr_size"),
    ],
)

oauth_scopes = TableDynamicLayout.set_fields(
    "OAuth Scopes",
    root_path="data.config.oauth_scopes",
    fields=[
        TextDyField.data_source("Scope", ".")
    ],
)

tags = TableDynamicLayout.set_fields(
    "Tags",
    root_path="data.config.tags",
    fields=[
        TextDyField.data_source("Tag", ".")
    ],
)

node_pool_meta = CloudServiceMeta.set_layouts([
    node_pool_overview,
    node_configuration,
    autoscaling_config,
    management_config,
    network_configuration,
    oauth_scopes,
    tags,
])


class KubernetesEngineResource(CloudServiceResource):
    cloud_service_group = StringType(default="KubernetesEngine")


class NodePoolResource(KubernetesEngineResource):
    cloud_service_type = StringType(default="NodePool")
    data = ModelType(NodePool)  # App Engine과 동일하게 명시적 ModelType 정의
    _metadata = ModelType(
        CloudServiceMeta, default=node_pool_meta, serialized_name="metadata"
    )


class NodePoolResponse(CloudServiceResponse):
    resource = PolyModelType(NodePoolResource)