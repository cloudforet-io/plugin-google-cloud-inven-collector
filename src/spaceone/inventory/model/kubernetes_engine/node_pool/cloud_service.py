from schematics import Model
from schematics.types import ModelType, StringType, IntType, DateTimeType, BooleanType, ListType, DictType
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, DateTimeDyField, EnumDyField, ListDyField
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, TableDynamicLayout, ListDynamicLayout, SimpleTableDynamicLayout


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


class NodePool(CloudServiceResource):
    name = StringType()
    cluster_name = StringType()
    location = StringType()
    project_id = StringType()
    status = StringType()
    status_message = StringType(deserialize_from="statusMessage")
    initial_node_count = IntType(deserialize_from="initialNodeCount")
    config = ModelType(NodeConfig)
    autoscaling = ModelType(AutoScaling)
    management = ModelType(Management)
    max_pods_constraint = ModelType(MaxPodsConstraint, deserialize_from="maxPodsConstraint")
    network_config = ModelType(NetworkConfig, deserialize_from="networkConfig")
    self_link = StringType(deserialize_from="selfLink")
    version = StringType()
    instance_group_urls = ListType(StringType, deserialize_from="instanceGroupUrls")
    pod_ipv4_cidr_size = IntType(deserialize_from="podIpv4CidrSize")
    upgrade_settings = DictType(StringType, deserialize_from="upgradeSettings")
    create_time = DateTimeType(deserialize_from="createTime")
    update_time = DateTimeType(deserialize_from="updateTime")
    api_version = StringType()

    def reference(self, region_code):
        return {
            "resource_id": self.self_link,
            "external_link": f"https://console.cloud.google.com/kubernetes/nodepool/detail/{self.location}/{self.cluster_name}/{self.name}/details?project={self.project_id}",
        }


class NodePoolResource(CloudServiceResource):
    cloud_service_type = StringType(default="NodePool")
    cloud_service_group = StringType(default="KubernetesEngine")
    provider = StringType(default="google_cloud")
    data = ModelType(NodePool)
    _metadata = ModelType(CloudServiceMeta, default=CloudServiceMeta, serialized_name="metadata")

    @classmethod
    def _set_meta(cls):
        meta = CloudServiceMeta.set_meta(
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
                DateTimeDyField.data_source("Created", "data.create_time"),
                DateTimeDyField.data_source("Updated", "data.update_time"),
            ],
            layouts=[
                ItemDynamicLayout.set_fields("NodePool Details", fields=[
                    TextDyField.data_source("Name", "data.name"),
                    TextDyField.data_source("Cluster Name", "data.cluster_name"),
                    TextDyField.data_source("Location", "data.location"),
                    EnumDyField.data_source("Status", "data.status", default_state={
                        "safe": ["RUNNING"],
                        "warning": ["PROVISIONING", "RECONCILING"],
                        "alert": ["STOPPING", "ERROR", "DEGRADED"],
                    }),
                    TextDyField.data_source("Initial Node Count", "data.initial_node_count"),
                    TextDyField.data_source("Version", "data.version"),
                    DateTimeDyField.data_source("Created", "data.create_time"),
                    DateTimeDyField.data_source("Updated", "data.update_time"),
                ]),
                ItemDynamicLayout.set_fields("Node Configuration", fields=[
                    TextDyField.data_source("Machine Type", "data.config.machine_type"),
                    TextDyField.data_source("Disk Size (GB)", "data.config.disk_size_gb"),
                    TextDyField.data_source("Disk Type", "data.config.disk_type"),
                    TextDyField.data_source("Image Type", "data.config.image_type"),
                    TextDyField.data_source("Preemptible", "data.config.preemptible"),
                    TextDyField.data_source("Spot", "data.config.spot"),
                    TextDyField.data_source("Service Account", "data.config.service_account"),
                    TextDyField.data_source("Min CPU Platform", "data.config.min_cpu_platform"),
                ]),
                ItemDynamicLayout.set_fields("Autoscaling", fields=[
                    TextDyField.data_source("Enabled", "data.autoscaling.enabled"),
                    TextDyField.data_source("Min Node Count", "data.autoscaling.min_node_count"),
                    TextDyField.data_source("Max Node Count", "data.autoscaling.max_node_count"),
                    TextDyField.data_source("Location Policy", "data.autoscaling.location_policy"),
                ]),
                ItemDynamicLayout.set_fields("Management", fields=[
                    TextDyField.data_source("Auto Upgrade", "data.management.auto_upgrade"),
                    TextDyField.data_source("Auto Repair", "data.management.auto_repair"),
                ]),
                ItemDynamicLayout.set_fields("Network Configuration", fields=[
                    TextDyField.data_source("Pod Range", "data.network_config.pod_range"),
                    TextDyField.data_source("Pod IPv4 CIDR Block", "data.network_config.pod_ipv4_cidr_block"),
                    TextDyField.data_source("Enable Private Nodes", "data.network_config.enable_private_nodes"),
                ]),
            ]
        )
        return meta


class NodePoolResponse(CloudServiceResponse):
    resource = ModelType(NodePoolResource)
