import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["VPCGatewayConnector"]

_LOGGER = logging.getLogger(__name__)


class VPCGatewayConnector(GoogleCloudConnector):
    google_client_service = "compute"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_nat_gateways(self, **query):
        """NAT Gateway 정보를 수집합니다."""
        nat_gateways = []
        query.update({"project": self.project_id})
        
        try:
            request = self.client.routers().aggregatedList(**query)
            while request is not None:
                response = request.execute()
                for region, routers_scoped_list in response.get("items", {}).items():
                    if "routers" in routers_scoped_list:
                        for router in routers_scoped_list["routers"]:
                            # NAT 구성이 있는 라우터 찾기
                            if "nats" in router:
                                for nat in router["nats"]:
                                    nat_gateway = {
                                        "name": nat.get("name"),
                                        "router_name": router.get("name"),
                                        "region": self._get_region_from_zone(region),
                                        "router_self_link": router.get("selfLink"),
                                        "creation_timestamp": router.get("creationTimestamp"),
                                        "nat_ip_allocate_option": nat.get("natIpAllocateOption"),
                                        "source_subnetwork_ip_ranges_to_nat": nat.get("sourceSubnetworkIpRangesToNat"),
                                        "nat_ips": nat.get("natIps", []),
                                        "min_ports_per_vm": nat.get("minPortsPerVm"),
                                        "enable_endpoint_independent_mapping": nat.get("enableEndpointIndependentMapping"),
                                        "icmp_idle_timeout_sec": nat.get("icmpIdleTimeoutSec"),
                                        "tcp_established_idle_timeout_sec": nat.get("tcpEstablishedIdleTimeoutSec"),
                                        "tcp_transitory_idle_timeout_sec": nat.get("tcpTransitoryIdleTimeoutSec"),
                                        "tcp_time_wait_timeout_sec": nat.get("tcpTimeWaitTimeoutSec"),
                                        "udp_idle_timeout_sec": nat.get("udpIdleTimeoutSec"),
                                        "subnetworks": nat.get("subnetworks", []),
                                        "log_config": nat.get("logConfig"),
                                        "type": "NAT_GATEWAY",
                                        "project": self.project_id,
                                    }
                                    nat_gateways.append(nat_gateway)
                
                request = self.client.routers().aggregatedList_next(
                    previous_request=request, previous_response=response
                )
        except Exception as e:
            _LOGGER.error(f"Error listing NAT gateways: {str(e)}")
            
        return nat_gateways

    def list_vpn_gateways(self, **query):
        """VPN Gateway 정보를 수집합니다."""
        vpn_gateways = []
        query.update({"project": self.project_id})
        
        try:
            # VPN Gateway 수집
            request = self.client.vpnGateways().aggregatedList(**query)
            while request is not None:
                response = request.execute()
                for region, vpn_gateways_scoped_list in response.get("items", {}).items():
                    if "vpnGateways" in vpn_gateways_scoped_list:
                        for vpn_gateway in vpn_gateways_scoped_list["vpnGateways"]:
                            vpn_gateway.update({
                                "region": self._get_region_from_zone(region),
                                "type": "VPN_GATEWAY",
                                "project": self.project_id,
                            })
                            vpn_gateways.append(vpn_gateway)
                
                request = self.client.vpnGateways().aggregatedList_next(
                    previous_request=request, previous_response=response
                )
                
            # Target VPN Gateway도 수집 (legacy)
            request = self.client.targetVpnGateways().aggregatedList(**query)
            while request is not None:
                response = request.execute()
                for region, target_vpn_gateways_scoped_list in response.get("items", {}).items():
                    if "targetVpnGateways" in target_vpn_gateways_scoped_list:
                        for target_vpn_gateway in target_vpn_gateways_scoped_list["targetVpnGateways"]:
                            target_vpn_gateway.update({
                                "region": self._get_region_from_zone(region),
                                "type": "TARGET_VPN_GATEWAY",
                                "project": self.project_id,
                            })
                            vpn_gateways.append(target_vpn_gateway)
                
                request = self.client.targetVpnGateways().aggregatedList_next(
                    previous_request=request, previous_response=response
                )
                            
        except Exception as e:
            _LOGGER.error(f"Error listing VPN gateways: {str(e)}")
            
        return vpn_gateways

    def list_routers(self, **query):
        """라우터 정보를 수집합니다."""
        routers = []
        query.update({"project": self.project_id})
        
        try:
            request = self.client.routers().aggregatedList(**query)
            while request is not None:
                response = request.execute()
                for region, routers_scoped_list in response.get("items", {}).items():
                    if "routers" in routers_scoped_list:
                        for router in routers_scoped_list["routers"]:
                            router.update({
                                "region": self._get_region_from_zone(region),
                                "project": self.project_id,
                            })
                            routers.append(router)
                
                request = self.client.routers().aggregatedList_next(
                    previous_request=request, previous_response=response
                )
        except Exception as e:
            _LOGGER.error(f"Error listing routers: {str(e)}")
            
        return routers

    def _get_region_from_zone(self, zone_url):
        """Zone URL에서 region 정보를 추출합니다."""
        if "/regions/" in zone_url:
            return zone_url.split("/regions/")[1]
        elif "/zones/" in zone_url:
            # zones에서 region 추출
            zone_name = zone_url.split("/zones/")[1]
            return "-".join(zone_name.split("-")[:-1])
        return "global"
