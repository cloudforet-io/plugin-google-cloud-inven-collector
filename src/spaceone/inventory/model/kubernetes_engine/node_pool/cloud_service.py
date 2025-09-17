from schematics import Model
from schematics.types import (
    BooleanType,
    DateTimeType,
    DictType,
    IntType,
    ListType,
    ModelType,
    StringType,
    PolyModelType,
)

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.libs.schema.google_cloud_monitoring import GoogleCloudMonitoringModel
from spaceone.inventory.libs.schema.google_cloud_logging import GoogleCloudLoggingModel
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


class NodeConfig(Model):
    machine_type = StringType(deserialize_from="machineType")
    disk_size_gb = IntType(deserialize_from="diskSizeGb")
    disk_type = StringType(deserialize_from="diskType")
    image_type = StringType(deserialize_from="imageType")
    preemptible = BooleanType()
    oauth_scopes = ListType(StringType, deserialize_from="oauthScopes")
    service_account = StringType(deserialize_from="serviceAccount")
    metadata = DictType(StringType)
    labels = DictType(StringType)
    tags = ListType(StringType)
    local_ssd_count = IntType(deserialize_from="localSsdCount")
    spot = BooleanType()
    min_cpu_platform = StringType(deserialize_from="minCpuPlatform")


class AutoScaling(Model):
    enabled = BooleanType()
    min_node_count = IntType(deserialize_from="minNodeCount")
    max_node_count = IntType(deserialize_from="maxNodeCount")
    total_min_node_count = IntType(deserialize_from="totalMinNodeCount")
    total_max_node_count = IntType(deserialize_from="totalMaxNodeCount")
    location_policy = StringType(deserialize_from="locationPolicy")


class Management(Model):
    auto_upgrade = BooleanType(deserialize_from="autoUpgrade")
    auto_repair = BooleanType(deserialize_from="autoRepair")
    upgrade_options = DictType(StringType, deserialize_from="upgradeOptions")


class MaxPodsConstraint(Model):
    max_pods_per_node = IntType(deserialize_from="maxPodsPerNode")


class NetworkConfig(Model):
    pod_range = StringType(deserialize_from="podRange")
    pod_ipv4_cidr_block = StringType(deserialize_from="podIpv4CidrBlock")
    create_pod_range = BooleanType(deserialize_from="createPodRange")
    enable_private_nodes = BooleanType(deserialize_from="enablePrivateNodes")


class NodeInfo(Model):
    name = StringType()
    status = StringType()
    machine_type = StringType(deserialize_from="machineType")
    zone = StringType()
    internal_ip = StringType(deserialize_from="internalIP")
    external_ip = StringType(deserialize_from="externalIP")
    create_time = StringType(deserialize_from="createTime")
    labels = DictType(StringType)
    taints = ListType(StringType)


class InstanceGroupInfo(Model):
    name = StringType()
    type = StringType()
    location = StringType()
    self_link = StringType(deserialize_from="selfLink")
    creation_timestamp = StringType(deserialize_from="creationTimestamp")
    description = StringType()
    network = StringType()
    subnetwork = StringType()
    zone = StringType()
    region = StringType()
    size = IntType()
    named_ports = ListType(DictType(StringType), deserialize_from="namedPorts")
    instances = ListType(ModelType(NodeInfo))


class Metrics(Model):
    node_count = StringType(deserialize_from="node_count")
    initial_node_count = StringType(deserialize_from="initial_node_count")
    machine_type = StringType(deserialize_from="machine_type")
    disk_size_gb = StringType(deserialize_from="disk_size_gb")
    status = StringType()


class NodePool(Model):
    name = StringType()
    cluster_name = StringType()
    location = StringType()
    project_id = StringType()
    status = StringType()
    status_message = StringType(deserialize_from="statusMessage")
    initial_node_count = IntType(deserialize_from="initialNodeCount")
    total_nodes = IntType(serialize_when_none=False)
    create_time = DateTimeType(deserialize_from="createTime")
    update_time = DateTimeType(deserialize_from="updateTime")
    api_version = StringType()
    config = ModelType(NodeConfig)
    autoscaling = ModelType(AutoScaling)
    management = ModelType(Management)
    max_pods_constraint = ModelType(MaxPodsConstraint, deserialize_from="maxPodsConstraint")
    network_config = ModelType(NetworkConfig, deserialize_from="networkConfig")
    version = StringType()
    instance_group_urls = ListType(StringType, deserialize_from="instanceGroupUrls")
    pod_ipv4_cidr_size = IntType(deserialize_from="podIpv4CidrSize")
    upgrade_settings = DictType(StringType, deserialize_from="upgradeSettings")
    
    # Google Cloud monitoring and logging (previously from BaseResource)
    self_link = StringType(deserialize_from="selfLink", serialize_when_none=False)
    google_cloud_monitoring = ModelType(GoogleCloudMonitoringModel, serialize_when_none=False)
    google_cloud_logging = ModelType(GoogleCloudLoggingModel, serialize_when_none=False)
    
    # Additional fields for extended node pool information
    nodes = ListType(ModelType(NodeInfo), serialize_when_none=False)
    instance_groups = ListType(ModelType(InstanceGroupInfo), serialize_when_none=False)
    metrics = ModelType(Metrics, serialize_when_none=False)
    total_groups = IntType(serialize_when_none=False)

    def reference(self, region_code):
        return {
            "resource_id": self.self_link,
            "external_link": f"https://console.cloud.google.com/kubernetes/nodepool/detail/{self.location}/{self.cluster_name}/{self.name}/details?project={self.project_id}",
        }


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
