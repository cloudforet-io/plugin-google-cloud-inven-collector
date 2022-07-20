from schematics import Model
from schematics.types import ModelType, ListType, StringType, IntType, DateTimeType, BooleanType
from spaceone.inventory.libs.schema.cloud_service import BaseResource


class Labels(Model):
    key = StringType()
    value = StringType()


class Allowed(Model):
    ip_protocol = StringType(deserialize_from='IPProtocol')
    ports = ListType(StringType())


class LogConfig(Model):
    enable = BooleanType(serialize_when_none=False)
    metadata = StringType(serialize_when_none=False)


class ComputeVM(Model):
    id = StringType()
    name = StringType()
    region = StringType()
    zone = StringType()
    address = StringType()
    project = StringType()
    subnetwork = StringType()
    tags = ListType(StringType(), default=[])
    service_accounts = ListType(StringType(), default=[])
    creation_timestamp = DateTimeType()
    labels = ListType(ModelType(Labels), default=[])
    labels_display = ListType(StringType(), default=[])


class FirewallDisplay(Model):
    enforcement = StringType()
    network_display = StringType()
    direction_display = StringType()
    target_display = ListType(StringType(default=[]))
    filter = StringType(default='')
    protocols_port = ListType(StringType(), default=[])
    action = StringType(choices=('Allow', 'Deny'))
    logs = StringType(choices=('On', 'Off'))


class Firewall(BaseResource):
    description = StringType()
    network = StringType()
    priority = IntType()
    direction = StringType()
    source_ranges = ListType(StringType(), deserialize_from='sourceRanges', serialize_when_none=False)
    destination_ranges = ListType(StringType(), deserialize_from='destinationRanges', serialize_when_none=False)
    source_tags = ListType(StringType(), deserialize_from='sourceTags', serialize_when_none=False)
    target_tags = ListType(StringType(), deserialize_from='targetTags', serialize_when_none=False)
    source_service_accounts = ListType(StringType(), deserialize_from='sourceServiceAccounts', serialize_when_none=False)
    target_service_accounts = ListType(StringType(), deserialize_from='targetServiceAccounts', serialize_when_none=False)
    applicable_instance = ListType(ModelType(ComputeVM), default=[])
    allowed = ListType(ModelType(Allowed), serialize_when_none=False)
    denied = ListType(ModelType(Allowed), serialize_when_none=False)
    disabled = BooleanType(serialize_when_none=False)
    log_config = ModelType(LogConfig, deserialize_from='logConfig', serialize_when_none=False)
    creation_timestamp = DateTimeType(deserialize_from='creationTimestamp')
    display = ModelType(FirewallDisplay, serialize_when_none=False)

    def reference(self):
        return {
            "resource_id": self.self_link,
            "external_link": f"https://console.cloud.google.com/networking/firewalls/details/{self.name}?project={self.project}"
        }
