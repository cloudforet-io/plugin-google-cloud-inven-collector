from schematics import Model
from schematics.types import (
    BooleanType,
    DictType,
    IntType,
    ListType,
    ModelType,
    StringType,
)

from spaceone.inventory.libs.schema.cloud_service import BaseResource


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


class NodePool(BaseResource):
    """GKE NodePool 데이터 모델 (SpaceONE 표준 패턴)"""

    name = StringType(serialize_when_none=False)
    cluster_name = StringType()
    location = StringType()
    project_id = StringType()
    status = StringType()
    status_message = StringType(deserialize_from="statusMessage")
    initial_node_count = IntType(deserialize_from="initialNodeCount")
    total_nodes = IntType(serialize_when_none=False)
    config = ModelType(NodeConfig)
    autoscaling = ModelType(AutoScaling)
    management = ModelType(Management)
    max_pods_constraint = ModelType(
        MaxPodsConstraint, deserialize_from="maxPodsConstraint"
    )
    network_config = ModelType(NetworkConfig, deserialize_from="networkConfig")
    version = StringType()
    instance_group_urls = ListType(StringType, deserialize_from="instanceGroupUrls")
    pod_ipv4_cidr_size = IntType(deserialize_from="podIpv4CidrSize")
    upgrade_settings = DictType(StringType, deserialize_from="upgradeSettings")

    # BaseResource에서 상속받는 필드들:
    # - self_link
    # - google_cloud_monitoring
    # - google_cloud_logging

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
