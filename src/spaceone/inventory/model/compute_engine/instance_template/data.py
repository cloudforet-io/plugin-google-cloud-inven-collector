from schematics import Model
from schematics.types import ModelType, ListType, StringType, IntType, DateTimeType, BooleanType, FloatType
from spaceone.inventory.libs.schema.cloud_service import BaseResource


class Labels(Model):
    key = StringType()
    value = StringType()


class InstanceGroup(Model):
    id = StringType()
    name = StringType()
    description = StringType()
    self_link = StringType(deserialize_from='selfLink')
    creation_timestamp = DateTimeType(deserialize_from='creationTimestamp')


class AccessConfig(Model):
    type = StringType()
    name = StringType()
    network_tier = StringType(choices=('STANDARD', 'PREMIUM'), deserialize_from='networkTier')
    kind = StringType()


class NetworkInterface(Model):
    name = StringType()
    network = StringType()
    network_display = StringType()
    configs = ListType(StringType(), default=[])
    network_tier = ListType(StringType(choices=('STANDARD', 'PREMIUM')), default=[])
    access_configs = ListType(ModelType(AccessConfig, default=[]))
    kind = StringType()


class DiskTags(Model):
    disk_type = StringType(choices=('local-ssd', 'pd-balanced', 'pd-ssd', 'pd-standard'), serialize_when_none=False)
    source_image = StringType()
    source_image_display = StringType()
    auto_delete = BooleanType()
    read_iops = FloatType(serialize_when_none=False)
    write_iops = FloatType(serialize_when_none=False)
    read_throughput = FloatType(serialize_when_none=False)
    write_throughput = FloatType(serialize_when_none=False)


class Disk(Model):
    device_index = IntType()
    device = StringType(default="")
    device_type = StringType(choices=('SCRATCH', 'PERSISTENT'))
    device_mode = StringType(choices=('READ_WRITE', 'READ_ONLY'))
    size = FloatType()
    tags = ModelType(DiskTags, default={})


class MachineType(Model):
    machine_type = StringType()
    machine_display = StringType(serialize_when_none=False)
    machine_detail = StringType(serialize_when_none=False)
    core = IntType(default=0)
    memory = FloatType(default=0.0)


class Labels(Model):
    key = StringType()
    value = StringType()


class ServiceAccount(Model):
    email = StringType(default="")
    scopes = ListType(StringType(), default=[], serialize_when_none=False)


class Scheduling(Model):
    on_host_maintenance = StringType(choices=('MIGRATE', 'TERMINATE'))
    automatic_restart = StringType(choices=('On', 'Off'))
    preemptibility = StringType(choices=('On', 'Off'))


class InstanceTemplate(BaseResource):
    '''
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
    '''
    description = StringType()
    fingerprint = StringType()
    disk_display = StringType()
    image = StringType()
    machine_type = StringType(serialize_when_none=False)
    in_used_by = ListType(StringType(), default=[])
    ip_forward = BooleanType(default=False)
    scheduling = ModelType(Scheduling, default={})
    network_tags = ListType(StringType(), default=[])
    instance_groups = ListType(ModelType(InstanceGroup), default=[])
    disks = ListType(ModelType(Disk), default=[])
    network_interfaces = ListType(ModelType(NetworkInterface), default=[])
    service_account = ModelType(ServiceAccount, serialize_when_none=False)
    labels = ListType(ModelType(Labels), default=[])
    kind = StringType()
    creation_timestamp = DateTimeType(deserialize_from='creationTimestamp')

    def reference(self):
        return {
            "resource_id": self.self_link,
            "external_link": f"https://console.cloud.google.com/compute/instanceTemplates/details/{self.name}?project={self.project}"
        }
