from schematics import Model
from schematics.types import (
    ModelType,
    ListType,
    StringType,
    IntType,
    DateTimeType,
    BooleanType,
)
from spaceone.inventory.libs.schema.cloud_service import BaseResource


class Labels(Model):
    key = StringType()
    value = StringType()


class SecondaryIpRanges(Model):
    range_name = StringType()
    ip_cidr_range = StringType()


class LogConfigSubnet(Model):
    enable = BooleanType(serialize_when_none=False)
    aggregation_interval = StringType(
        deserialize_from="aggregationInterval", serialize_when_none=False
    )
    flow_sampling = IntType(deserialize_from="flowSampling", serialize_when_none=False)
    metadata = StringType(deserialize_from="metadata", serialize_when_none=False)
    metadata_fields = ListType(
        StringType(),
        default=[],
        deserialize_from="metadataFields",
        serialize_when_none=False,
    )
    filter_expr = StringType(deserialize_from="filterExpr", serialize_when_none=False)


class IPAddress(Model):
    id = StringType(default="")
    name = StringType(default="")
    address = StringType()
    region = StringType()
    subnet_name = StringType()
    address_type = StringType(
        choices=("INTERNAL", "EXTERNAL"), deserialize_from="addressType"
    )
    is_ephemeral = StringType(choices=("Static", "Ephemeral"))
    purpose = StringType(
        choices=("GCE_ENDPOINT", "DNS_RESOLVER", "VPC_PEERING", "IPSEC_INTERCONNECT"),
        serialize_when_none=False,
    )
    description = StringType()
    network_tier = StringType(deserialize_from="networkTier")
    used_by = ListType(StringType(), default=[])
    self_link = StringType(deserialize_from="selfLink")
    ip_version = StringType(
        choices=("IPV4", "IPV6"),
        deserialize_from="ipVersion",
        serialize_when_none=False,
    )
    ip_version_display = StringType()
    status = StringType(choices=("RESERVED", "RESERVING", "IN_USE"))
    users = ListType(StringType(), default=[])
    labels = ListType(ModelType(Labels), default=[])
    creation_timestamp = DateTimeType(deserialize_from="creationTimestamp")


class VPCSubnet(BaseResource):
    description = StringType()
    network = StringType()
    network_display = StringType()
    region = StringType()
    google_access = StringType(choices=("On", "Off"))
    flow_log = StringType(choices=("On", "Off"))
    ip_cidr_range = StringType(deserialize_from="ipCidrRange")
    gateway_address = StringType(deserialize_from="gatewayAddress")
    secondary_ip_ranges = ListType(
        ModelType(SecondaryIpRanges), default=[], serialize_when_none=False
    )
    self_link = StringType(deserialize_from="selfLink")
    fingerprint = StringType()
    enable_flow_logs = BooleanType(
        deserialize_from="enableFlowLogs", serialize_when_none=False
    )
    private_ipv6_google_access = StringType(
        deserialize_from="privateIpv6GoogleAccess", serialize_when_none=False
    )
    ipv6_cidr_range = StringType(
        deserialize_from="ipv6CidrRange", serialize_when_none=False
    )
    purpose = StringType(
        choices=("PRIVATE_RFC_1918", "INTERNAL_HTTPS_LOAD_BALANCER"),
        serialize_when_none=False,
    )
    role = StringType(choices=("ACTIVE", "BACKUP"), serialize_when_none=False)
    state = StringType(choices=("READY", "DRAINING"), serialize_when_none=False)
    log_config = ModelType(LogConfigSubnet, serialize_when_none=False)
    ip_address_data = ListType(ModelType(IPAddress), default=[])
    creation_timestamp = DateTimeType(deserialize_from="creationTimestamp")

    def reference(self):
        return {
            "resource_id": self.self_link,
            "external_link": f"https://console.cloud.google.com/networking/networks/details/default?project={self.project}&pageTab=SUBNETS",
        }
