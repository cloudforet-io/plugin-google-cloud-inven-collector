from schematics.types import (
    ModelType,
    StringType,
    IntType,
    DateTimeType,
    ListType,
    BooleanType,
    DictType,
)
from schematics.models import Model

from spaceone.inventory.libs.schema.cloud_service import BaseResource

"""
NAT Gateway Data Model
"""


class NATSubnetwork(Model):
    name = StringType()
    source_ip_ranges_to_nat = ListType(StringType(), default=[])
    secondary_ip_range_names = ListType(StringType(), default=[])


class NATLogConfig(Model):
    enable = BooleanType()
    filter = StringType(choices=("ERRORS_ONLY", "TRANSLATIONS_ONLY", "ALL"))


class NATGateway(Model):
    name = StringType(required=True)
    router_name = StringType()
    router_self_link = StringType()
    region = StringType()
    nat_ip_allocate_option = StringType(choices=("MANUAL_ONLY", "AUTO_ONLY"))
    source_subnetwork_ip_ranges_to_nat = StringType(choices=("ALL_SUBNETWORKS_ALL_IP_RANGES", "ALL_SUBNETWORKS_ALL_PRIMARY_IP_RANGES", "LIST_OF_SUBNETWORKS"))
    nat_ips = ListType(StringType(), default=[])
    min_ports_per_vm = IntType()
    enable_endpoint_independent_mapping = BooleanType()
    icmp_idle_timeout_sec = IntType()
    tcp_established_idle_timeout_sec = IntType()
    tcp_transitory_idle_timeout_sec = IntType()
    tcp_time_wait_timeout_sec = IntType()
    udp_idle_timeout_sec = IntType()
    subnetworks = ListType(ModelType(NATSubnetwork), default=[])
    log_config = ModelType(NATLogConfig)
    type = StringType(default="NAT_GATEWAY")
    project = StringType()
    creation_timestamp = DateTimeType(deserialize_from="creationTimestamp")


"""
VPN Gateway Data Model
"""


class VPNGatewayInterface(Model):
    id = IntType()
    ip_address = StringType()
    interconnect_attachment = StringType()


class VPNGateway(Model):
    name = StringType(required=True)
    description = StringType()
    region = StringType()
    network = StringType()
    vpn_interfaces = ListType(ModelType(VPNGatewayInterface), default=[])
    type = StringType(default="VPN_GATEWAY")
    project = StringType()
    creation_timestamp = DateTimeType(deserialize_from="creationTimestamp")
    self_link = StringType()


class TargetVPNGateway(Model):
    name = StringType(required=True)
    description = StringType()
    region = StringType()
    network = StringType()
    status = StringType()
    type = StringType(default="TARGET_VPN_GATEWAY")
    project = StringType()
    creation_timestamp = DateTimeType(deserialize_from="creationTimestamp")
    self_link = StringType()
    forwarding_rules = ListType(StringType(), default=[])
    tunnels = ListType(StringType(), default=[])


"""
VPC Gateway (통합 모델)
"""


class VPCGateway(BaseResource):
    gateway_type = StringType(choices=("NAT_GATEWAY", "VPN_GATEWAY", "TARGET_VPN_GATEWAY"))
    region = StringType()
    status = StringType()
    network = StringType()
    network_name = StringType()
    description = StringType()
    
    # NAT Gateway 관련 필드
    router_name = StringType()
    router_self_link = StringType()
    nat_ip_allocate_option = StringType()
    source_subnetwork_ip_ranges_to_nat = StringType()
    nat_ips = ListType(StringType(), default=[])
    min_ports_per_vm = IntType()
    enable_endpoint_independent_mapping = BooleanType()
    nat_subnetworks = ListType(ModelType(NATSubnetwork), default=[])
    nat_log_config = ModelType(NATLogConfig)
    
    # 타임아웃 관련 필드
    icmp_idle_timeout_sec = IntType()
    tcp_established_idle_timeout_sec = IntType()
    tcp_transitory_idle_timeout_sec = IntType()
    tcp_time_wait_timeout_sec = IntType()
    udp_idle_timeout_sec = IntType()
    timeouts = DictType(StringType(), default={})
    
    # VPN Gateway 관련 필드
    vpn_interfaces = ListType(ModelType(VPNGatewayInterface), default=[])
    vpn_interfaces_display = ListType(DictType(StringType()), default=[])
    forwarding_rules = ListType(StringType(), default=[])
    tunnels = ListType(StringType(), default=[])
    
    # 공통 필드
    creation_timestamp = DateTimeType(deserialize_from="creationTimestamp")
    self_link = StringType()
    type = StringType()

    def reference(self):
        if self.gateway_type == "NAT_GATEWAY":
            # NAT Gateway의 경우 router_self_link 또는 name을 사용
            resource_id = self.router_self_link or f"projects/{self.project}/regions/{self.region}/routers/{self.router_name}"
            return {
                "resource_id": resource_id,
                "external_link": f"https://console.cloud.google.com/net-services/nat/list?project={self.project}",
            }
        elif self.gateway_type in ["VPN_GATEWAY", "TARGET_VPN_GATEWAY"]:
            # VPN Gateway의 경우 self_link 또는 name을 사용
            resource_id = getattr(self, 'self_link', None) or f"projects/{self.project}/regions/{self.region}/vpnGateways/{self.name}"
            return {
                "resource_id": resource_id,
                "external_link": f"https://console.cloud.google.com/net-security/vpn/list?project={self.project}",
            }
        # 기본값
        resource_id = getattr(self, 'self_link', None) or f"projects/{self.project}/regions/{self.region}/gateways/{self.name}"
        return {
            "resource_id": resource_id,
            "external_link": f"https://console.cloud.google.com/networking?project={self.project}",
        }


