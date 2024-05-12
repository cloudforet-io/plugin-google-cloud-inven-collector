from schematics import Model
from schematics.types import (
    ModelType,
    ListType,
    StringType,
    IntType,
    DateTimeType,
    BooleanType,
    DictType,
    FloatType,
)
from spaceone.inventory.libs.schema.cloud_service import BaseResource


class InstanceGroupManagerVersionTargetSize(Model):
    fixed = IntType(serialize_when_none=False)
    percent = IntType(serialize_when_none=False)
    calculated = IntType(serialize_when_none=False)


class AutoScalingPolicyScaleInControl(Model):
    max_scaled_in_replicas = ModelType(
        InstanceGroupManagerVersionTargetSize, deserialize_from="maxScaledInReplicas"
    )
    time_window_sec = IntType(deserialize_from="timeWindowSec")


class AutoScalerPolicyCPUUtilization(Model):
    utilization_target = FloatType(deserialize_from="utilizationTarget")


class LoadBalancingUtilization(Model):
    utilization_target = FloatType(deserialize_from="utilizationTarget")


class AutoScalerPolicyCustomMetricUtilization(Model):
    metric = StringType(serialize_when_none=False)
    filter = StringType(serialize_when_none=False)
    utilization_target_type = StringType(
        choices=("GAUGE", "DELTA_PER_SECOND", "DELTA_PER_MINUTE"),
        deserialize_from="utilizationTargetType",
        serialize_when_none=False,
    )
    utilization_target = FloatType(deserialize_from="utilizationTarget")
    single_instance_assignment = FloatType(
        deserialize_from="singleInstanceAssignment", serialize_when_none=False
    )


class AutoScalerPolicy(Model):
    min_num_replicas = IntType(deserialize_from="minNumReplicas")
    max_num_replicas = IntType(deserialize_from="maxNumReplicas")
    scaler_in_control = ModelType(
        AutoScalingPolicyScaleInControl,
        deserialize_from="scaleInControl",
        serialize_when_none=False,
    )
    cool_down_period_sec = IntType(deserialize_from="coolDownPeriodSec")
    cpu_utilization = ModelType(
        AutoScalerPolicyCPUUtilization, deserialize_from="cpuUtilization"
    )
    custom_metric_utilizations = ListType(
        ModelType(AutoScalerPolicyCustomMetricUtilization),
        deserialize_from="customMetricUtilizations",
        serialize_when_none=False,
    )
    loadbalancing_utilization = ModelType(
        LoadBalancingUtilization,
        deserialize_from="loadBalancingUtilization",
        serialize_when_none=False,
    )
    mode = StringType()


class AutoScalerStatusDetail(Model):
    message = StringType()
    type = StringType(
        choices=(
            "ALL_INSTANCES_UNHEALTHY",
            "BACKEND_SERVICE_DOES_NOT_EXIST",
            "CAPPED_AT_MAX_NUM_REPLICAS",
            "CUSTOM_METRIC_DATA_POINTS_TOO_SPARSE",
            "CUSTOM_METRIC_INVALID",
            "MIN_EQUALS_MAX",
            "MISSING_CUSTOM_METRIC_DATA_POINTS",
            "MISSING_LOAD_BALANCING_DATA_POINTS",
            "MODE_OFF",
            "MODE_ONLY_UP",
            "MORE_THAN_ONE_BACKEND_SERVICE",
            "NOT_ENOUGH_QUOTA_AVAILABLE",
            "REGION_RESOURCE_STOCKOUT",
            "SCALING_TARGET_DOES_NOT_EXIST",
            "UNSUPPORTED_MAX_RATE_LOAD_BALANCING_CONFIGURATION",
            "ZONE_RESOURCE_STOCKOUT",
        )
    )


class AutoScaler(Model):
    id = StringType()
    name = StringType()
    kind = StringType()
    recommended_size = IntType(deserialize_from="recommendedSize")
    description = StringType(default="")
    target = StringType(serialize_when_none=False)
    autoscaling_policy = ModelType(
        AutoScalerPolicy, deserialize_from="autoscalingPolicy"
    )
    zone = StringType(serialize_when_none=False)
    region = StringType(serialize_when_none=False)
    self_link = StringType(deserialize_from="selfLink")
    status = StringType(choices=("PENDING", "DELETING", "ACTIVE", "ERROR"))
    status_details = ListType(
        ModelType(AutoScalerStatusDetail),
        deserialize_from="statusDetails",
        serialize_when_none=False,
    )
    creation_timestamp = DateTimeType(deserialize_from="creationTimestamp")


class InstanceTemplate(Model):
    id = StringType()
    name = StringType()
    kind = StringType()
    self_link = StringType(deserialize_from="selfLink")
    source_instance = StringType(
        deserialize_from="sourceInstance", serialize_when_none=False
    )
    description = StringType(default="")
    creation_timestamp = DateTimeType(deserialize_from="creationTimestamp")


class NamedPort(Model):
    name = StringType()
    port = IntType()


class Instance(Model):
    name = StringType()
    instance = StringType()
    status = StringType(
        choices=(
            "PROVISIONING",
            "STAGING",
            "RUNNING",
            "STOPPING",
            "SUSPENDING",
            "SUSPENDED",
            "REPAIRING",
            "TERMINATED",
        )
    )
    name_ports = ListType(
        ModelType(NamedPort), deserialize_from="namedPorts", default=[]
    )


class DistributionPolicyZone(Model):
    zone = StringType()


class DistributionPolicy(Model):
    zones = ListType(ModelType(DistributionPolicyZone))


class InstanceGroupManagerStatusStatefulPerInstanceConfig(Model):
    all_effective = BooleanType(deserialize_from="allEffective")


class InstanceGroupManagerStatusStateful(Model):
    has_stateful_config = BooleanType(deserialize_from="hasStatefulConfig")
    per_instance_configs = ModelType(
        InstanceGroupManagerStatusStatefulPerInstanceConfig,
        deserialize_from="perInstanceConfigs",
    )


class InstanceGroupManagerStatusVersionTarget(Model):
    is_reached = BooleanType(deserialize_from="isReached")


class InstanceGroupManagerStatus(Model):
    is_stable = BooleanType(deserialize_from="isStable")
    version_target = ModelType(
        InstanceGroupManagerStatusVersionTarget, deserialize_from="versionTarget"
    )
    stateful = ModelType(InstanceGroupManagerStatusStateful)
    autoscaler = StringType()


class InstanceGroupManagerVersion(Model):
    name = StringType(serialize_when_none=False)
    instanceTemplate = StringType()
    target_size = ModelType(
        InstanceGroupManagerVersionTargetSize, deserialize_from="targetSize"
    )


class InstanceGroupManagerCurrentAction(Model):
    none = IntType()
    creating = IntType()
    creating_without_retries = IntType(deserialize_from="creatingWithoutRetries")
    verifying = IntType()
    recreating = IntType()
    deleting = IntType()
    abandoning = IntType()
    restarting = IntType()
    refreshing = IntType()


class InstanceGroupManagerAutoHealingPolicy(Model):
    health_check = StringType(deserialize_from="healthCheck")
    initial_delay_sec = IntType(deserialize_from="initialDelaySec")


class InstanceGroupManagerUpdatePolicyMaxSurge(Model):
    fixed = IntType()
    percent = IntType()
    calculated = IntType()


class InstanceGroupManagerUpdatePolicy(Model):
    type = StringType(choices=("PROACTIVE", "OPPORTUNISTIC"))
    instance_redistribution_type = StringType(
        choices=("PROACTIVE", "NONE"), deserialize_from="instanceRedistributionType"
    )
    minimal_action = StringType(
        choices=("RESTART", "REPLACE", "RESTART"), deserialize_from="minimalAction"
    )
    max_surge = ModelType(InstanceGroupManagerUpdatePolicyMaxSurge)
    max_unavailable = ModelType(InstanceGroupManagerUpdatePolicyMaxSurge)
    replacement_method = StringType(deserialize_from="replacementMethod")


class DiskModel(Model):
    key = StringType()
    value = DictType(StringType())


class InstanceGroupManagerStatefulPolicyPreservedState(Model):
    disks = ListType(ModelType(DiskModel), default=[])


class InstanceGroupManagerStatefulPolicy(Model):
    preserved_state = ModelType(
        InstanceGroupManagerStatefulPolicyPreservedState,
        deserialize_from="preservedState",
    )


class InstanceGroupManagers(Model):
    id = StringType()
    name = StringType()
    description = StringType(default="")
    zone = StringType()
    distribution_policy = ModelType(
        DistributionPolicy,
        deserialize_from="distributionPolicy",
        serialize_when_none=False,
    )
    instance_template = StringType(deserialize_from="instanceTemplate")
    instance_group = StringType(deserialize_from="instanceGroup")
    target_pools = ListType(
        StringType, deserialize_from="targetPools", serialize_when_none=False
    )
    fingerprint = StringType()
    current_actions = ModelType(
        InstanceGroupManagerCurrentAction, deserialize_from="currentActions"
    )
    status = ModelType(InstanceGroupManagerStatus)
    target_size = IntType(deserialize_from="targetSize")
    self_link = StringType(deserialize_from="selfLink")
    auto_healing_policies = ListType(
        ModelType(InstanceGroupManagerAutoHealingPolicy),
        deserialize_from="autoHealingPolicies",
    )
    update_policy = ModelType(
        InstanceGroupManagerUpdatePolicy,
        deserialize_from="updatePolicy",
        serialize_when_none=False,
    )
    named_ports = ListType(
        ModelType(NamedPort), deserialize_from="namedPorts", serialize_when_none=False
    )
    stateful_policy = ModelType(
        InstanceGroupManagerStatefulPolicy,
        deserialize_from="statefulPolicy",
        serialize_when_none=False,
    )
    base_instance_name = StringType(deserialize_from="baseInstanceName")

    versions = ListType(ModelType(InstanceGroupManagerVersion))
    creation_timestamp = DateTimeType(deserialize_from="creationTimestamp")


class Scheduler(Model):
    type = StringType()
    instance_group_type = StringType()
    mode = StringType(serialize_when_none=False)
    origin_max_size = IntType(serialize_when_none=False)
    origin_min_size = IntType(serialize_when_none=False)
    recommend_size = IntType(serialize_when_none=False)


class DisplayLocation(Model):
    region = StringType(default="")
    zone = StringType(default="")


class InstanceGroup(BaseResource):
    kind = StringType()
    instance_group_type = StringType(choices=("STATELESS", "STATEFUL", "UNMANAGED"))
    description = StringType(default="")
    network = StringType()
    fingerprint = StringType()
    display_location = ModelType(DisplayLocation, serialize_when_none=False)
    zone = StringType(serialize_when_none=False)
    size = IntType()
    power_scheduler = ModelType(Scheduler)
    subnetwork = StringType()
    instance_counts = IntType(default=0)
    template = ModelType(InstanceTemplate, serialize_when_none=False)
    instance_group_manager = ModelType(InstanceGroupManagers, serialize_when_none=False)
    autoscaler = ModelType(AutoScaler, serialize_when_none=False)
    instances = ListType(ModelType(Instance), default=[])
    named_ports = ListType(
        ModelType(NamedPort), deserialize_from="namedPorts", serialize_when_none=False
    )
    autoscaling_display = StringType(default="")
    creation_timestamp = DateTimeType(deserialize_from="creationTimestamp")

    def reference(self):
        return {
            "resource_id": self.self_link,
            "external_link": f"https://console.cloud.google.com/compute/instanceGroups/details/{self.zone}/{self.name}?authuser=1&project={self.project}",
        }
