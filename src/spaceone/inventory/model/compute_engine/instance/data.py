from schematics import Model
from schematics.types import (
    ModelType,
    ListType,
    StringType,
    IntType,
    DateTimeType,
    BooleanType,
    FloatType,
    DictType,
)
from spaceone.inventory.libs.schema.google_cloud_monitoring import (
    GoogleCloudMonitoringModel,
)
from spaceone.inventory.libs.schema.google_cloud_logging import GoogleCloudLoggingModel


# common
class Labels(Model):
    key = StringType()
    value = StringType()


class Tags(Model):
    key = StringType()


class Description(Model):
    description = StringType()


class AccessPolicy(Model):
    service_account = StringType()
    display_name = StringType()
    scopes = ListType(ModelType(Description))


# InstanceGroup
class InstanceGroup(Model):
    id = StringType()
    self_link = StringType()
    name = StringType()
    instance_template_name = StringType()


class AutoScaler(Model):
    id = StringType()
    self_link = StringType()
    name = StringType()
    instance_group = ModelType(InstanceGroup, serialize_when_none=False)


# Server = compute, google_cloud, hardware, os, server,
class Compute(Model):
    keypair = StringType(default="")
    public_ip_address = StringType()
    az = StringType()
    instance_id = StringType()
    instance_name = StringType(default="")
    instance_state = StringType(
        choices=(
            "PROVISIONING",
            "STAGING",
            "RUNNING",
            "STOPPING",
            "REPAIRING",
            "SUSPENDING",
            "SUSPENDED",
            "TERMINATED",
        )
    )
    instance_type = StringType()
    account = StringType()
    image = StringType()
    launched_at = DateTimeType()
    security_groups = ListType(StringType, default=[])
    tags = DictType(StringType, default={})


class Scheduling(Model):
    on_host_maintenance = StringType(default="MIGRATE")
    automatic_restart = BooleanType(default=True)
    preemptible = BooleanType(default=False)


class Key(Model):
    user_name = StringType()
    ssh_key = StringType()
    display_name = StringType()


class SSHKey(Model):
    block_project_ssh_keys = StringType()
    ssh_keys = ListType(ModelType(Key))


class GoogleCloud(Model):
    self_link = StringType()
    fingerprint = StringType()
    reservation_affinity = StringType(default="ANY_RESERVATION")
    deletion_protection = BooleanType(default=False)
    scheduling = ModelType(Scheduling)
    tags = ListType(ModelType(Tags))
    labels = ListType(ModelType(Labels), default=[])
    ssh_keys = ModelType(SSHKey)
    service_accounts = ListType(ModelType(AccessPolicy), default=[])
    is_managed_instance = BooleanType(default=False)


class Hardware(Model):
    core = IntType(default=0)
    memory = FloatType(default=0.0)
    is_vm = BooleanType(default=True)
    cpu_model = StringType(default="")


class OS(Model):
    os_type = StringType(serialize_when_none=False)
    details = StringType(choices=("LINUX", "WINDOWS"), serialize_when_none=False)
    os_distro = StringType(serialize_when_none=False)
    os_arch = StringType(serialize_when_none=False)


# disk
class DiskTags(Model):
    disk_id = StringType(serialize_when_none=False)
    disk_name = StringType(serialize_when_none=False)
    description = StringType(serialize_when_none=False)
    zone = StringType(serialize_when_none=False)
    disk_type = StringType(
        choices=("local-ssd", "pd-balanced", "pd-ssd", "pd-standard"),
        serialize_when_none=False,
    )
    encrypted = BooleanType(default=True)
    read_iops = FloatType(serialize_when_none=False)
    write_iops = FloatType(serialize_when_none=False)
    read_throughput = FloatType(serialize_when_none=False)
    write_throughput = FloatType(serialize_when_none=False)
    labels = ListType(ModelType(Labels), default=[], serialize_when_none=False)


class Disk(Model):
    device_index = IntType()
    device = StringType(default="")
    disk_type = StringType(default="disk")
    size = FloatType()
    tags = ModelType(DiskTags, default={})


# loadbalancing = load_balancer
class LoadBalancer(Model):
    type = StringType(choices=("HTTP", "TCP", "UDP"))
    name = StringType()
    dns = StringType(default="")
    port = ListType(IntType())
    protocol = ListType(StringType())
    scheme = StringType(choices=("EXTERNAL", "INTERNAL"))
    tags = DictType(StringType, default={})


# nic
class NIC(Model):
    device_index = IntType()
    device = StringType(default="")
    cidr = StringType()
    nic_type = StringType(default="Virtual")  # 확인 필요
    ip_addresses = ListType(StringType())  # 확인필요 (accessConfig)
    mac_address = StringType(default="")
    public_ip_address = StringType()
    tags = DictType(StringType, default={})


# Firewall
class SecurityGroup(Model):
    priority = IntType(serialize_when_none=False)
    protocol = StringType()
    remote = StringType()  # mimic
    remote_id = StringType(serialize_when_none=False)  # filter value
    remote_cidr = StringType(serialize_when_none=False)  # cidr
    security_group_name = StringType(default="")
    port_range_min = IntType(serialize_when_none=False)
    port_range_max = IntType(serialize_when_none=False)
    security_group_id = StringType()
    description = StringType(default="")
    direction = StringType(choices=("inbound", "outbound"))
    port = StringType(serialize_when_none=False)
    action = StringType(choices=("allow", "deny"))


# vpc
class VPC(Model):
    vpc_id = StringType()
    vpc_name = StringType(default="")
    description = StringType(default="")
    self_link = StringType(default="")


# subnet
class Subnet(Model):
    subnet_id = StringType()
    cidr = StringType()
    subnet_name = StringType()
    gateway_address = StringType()
    vpc = ModelType(VPC)
    self_link = StringType()


class GPU(Model):
    gpu_machine_type = StringType(serialize_when_none=False)
    gpu_count = IntType(serialize_when_none=False)


class Display(Model):
    gpus = ListType(StringType, default=[])
    has_gpu = BooleanType(default=False)


class VMInstance(Model):
    os = ModelType(OS)
    google_cloud = ModelType(GoogleCloud)
    primary_ip_address = StringType()
    hardware = ModelType(Hardware)
    compute = ModelType(Compute)
    gpus = ListType(ModelType(GPU))
    total_gpu_count = IntType()
    load_balancers = ListType(ModelType(LoadBalancer))
    security_group = ListType(ModelType(SecurityGroup))
    vpc = ModelType(VPC)
    subnet = ModelType(Subnet)
    nics = ListType(ModelType(NIC))
    disks = ListType(ModelType(Disk))
    autoscaler = ModelType(AutoScaler, serialize_when_none=False)
    google_cloud_monitoring = ModelType(
        GoogleCloudMonitoringModel, serialize_when_none=False
    )
    google_cloud_logging = ModelType(GoogleCloudLoggingModel, serialize_when_none=False)
    display = ModelType(Display, serialize_when_none=False)
