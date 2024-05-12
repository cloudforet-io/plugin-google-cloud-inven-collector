from schematics import Model
from schematics.types import (
    ModelType,
    ListType,
    StringType,
    IntType,
    DateTimeType,
    BooleanType,
    FloatType,
)
from spaceone.inventory.libs.schema.cloud_service import BaseResource


class Labels(Model):
    key = StringType()
    value = StringType()


class AccessConfig(Model):
    type = StringType()
    name = StringType()
    nat_ip = StringType(deserialize_from="natIP")
    set_public_ptr = BooleanType(
        deserialize_from="setPublicPtr", serialize_when_none=False
    )
    public_ptr_domain_name = StringType(
        deserialize_from="publicPtrDomainName", serialize_when_none=False
    )
    network_tier = StringType(
        choices=("STANDARD", "PREMIUM"), deserialize_from="networkTier"
    )
    kind = StringType()


class AliasIPRanges(Model):
    ip_cidr_range = StringType()
    subnetwork_range_name = StringType()


class NetworkInterface(Model):
    name = StringType()
    network_display = StringType()
    network_tier_display = StringType(choices=("STANDARD", "PREMIUM"))
    subnetwork_display = StringType()
    ip_range = ListType(StringType(), default=[])
    ip_forward = StringType(choices=("On", "Off"), serialize_when_none=False)
    network = StringType()
    subnetwork = StringType()
    primary_ip_address = StringType()
    public_ip_address = StringType()
    alias_ip_ranges = ListType(ModelType(AliasIPRanges), default=[])
    access_configs = ListType(ModelType(AccessConfig), default=[])
    kind = StringType()


class DiskTags(Model):
    disk_type = StringType(
        choices=("local-ssd", "pd-balanced", "pd-ssd", "pd-standard"),
        serialize_when_none=False,
    )
    auto_delete = BooleanType()
    read_iops = FloatType(serialize_when_none=False)
    write_iops = FloatType(serialize_when_none=False)
    read_throughput = FloatType(serialize_when_none=False)
    write_throughput = FloatType(serialize_when_none=False)


class BootImage(Model):
    name = StringType(serialize_when_none=False)
    details = StringType(serialize_when_none=False)
    os_type = StringType(serialize_when_none=False)
    os_distro = StringType(serialize_when_none=False)
    os_arch = StringType(serialize_when_none=False)


class Disk(Model):
    device_index = IntType()
    device = StringType(default="")
    device_type = StringType(choices=("SCRATCH", "PERSISTENT"))
    device_mode = StringType(choices=("READ_WRITE", "READ_ONLY"))
    size = FloatType()
    boot_image = StringType(serialize_when_none=False)
    is_boot_image = BooleanType(default=False)
    encryption = StringType(
        choices=("Google managed", "Customer managed, Customer supplied")
    )
    tags = ModelType(DiskTags, default={})


class MachineType(Model):
    machine_type = StringType()
    source_image_from = StringType(serialize_when_none=False)


class Scheduling(Model):
    on_host_maintenance = StringType(choices=("MIGRATE", "TERMINATE"))
    automatic_restart = StringType(choices=("On", "Off"))
    preemptibility = StringType(choices=("On", "Off"))


class ServiceAccount(Model):
    email = StringType(default="")
    scopes = ListType(StringType(), default=[], serialize_when_none=False)


class MachineImage(BaseResource):
    """
    ('ID', 'data.id'),
    ('Name', 'data.name'),
    ('Description', 'data.description'),
    ('Fingerprint', 'data.fingerprint'),
    ('In Used By', 'data.in_used_by'),
    ('Machine Type', 'data.machine_type'),
    ('Affected Rules', 'data.affected_rules'),
    ('IP Forward', 'data.ip_forward'
    ('Self Link', 'data.self_link'),
    ('Creation Time', 'data.creation_timestamp')
    """

    description = StringType()
    status = StringType(
        choices=("INVALID", "CREATING", "READY", "DELETING", "UPLOADING")
    )
    fingerprint = StringType()
    machine = ModelType(
        MachineType, deserialize_from="machine_type", serialize_when_none=False
    )
    network_tags = ListType(StringType(), default=[])
    deletion_protection = BooleanType(default=False)
    total_storage_bytes = FloatType()
    total_storage_display = StringType()
    storage_locations = ListType(
        StringType(), default=[], deserialize_from="storageLocations"
    )
    scheduling = ModelType(Scheduling, default={})
    network_interfaces = ListType(ModelType(NetworkInterface), default=[])
    disks = ListType(ModelType(Disk), default=[])
    service_account = ModelType(ServiceAccount, serialize_when_none=False)
    kind = StringType(serialize_when_none=False)
    location = ListType(StringType(), serialize_when_none=False)
    creation_timestamp = DateTimeType(deserialize_from="creationTimestamp")

    def reference(self):
        return {
            "resource_id": self.self_link,
            "external_link": f"https://console.cloud.google.com/compute/machineImages/details/{self.name}?project={self.project}",
        }
