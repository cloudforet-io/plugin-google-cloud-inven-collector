from schematics import Model
from schematics.types import ListType, StringType, DateTimeType
from spaceone.inventory.libs.schema.cloud_service import BaseResource


class Labels(Model):
    key = StringType()
    value = StringType()


class ExternalIpAddress(BaseResource):
    status = StringType(choices=("RESERVED", "RESERVING", "IN_USE"))
    status_display = StringType(choices=("Reserved", "Reserving", "In Use"))
    description = StringType(default="")
    address = StringType()
    subnet_name = StringType(serialize_when_none=False)
    address_type = StringType(
        choices=("INTERNAL", "EXTERNAL"), deserialize_from="addressType"
    )
    is_ephemeral = StringType(choices=("Static", "Ephemeral"))
    purpose = StringType(
        choices=("GCE_ENDPOINT", "DNS_RESOLVER", "VPC_PEERING", "IPSEC_INTERCONNECT"),
        serialize_when_none=False,
    )
    network_tier = StringType(
        choices=("PREMIUM", "STANDARD"),
        deserialize_from="networkTier",
        serialize_when_none=False,
    )
    network_tier_display = StringType()
    used_by = ListType(StringType(), default=[])
    ip_version = StringType(
        choices=("IPV4", "IPV6"),
        deserialize_from="ipVersion",
        serialize_when_none=False,
    )
    ip_version_display = StringType()
    users = ListType(StringType(), default=[])
    creation_timestamp = DateTimeType(deserialize_from="creationTimestamp")

    def reference(self):
        return {
            "resource_id": self.self_link,
            "external_link": f"https://console.cloud.google.com/networking/addresses/list/project={self.project}",
        }
