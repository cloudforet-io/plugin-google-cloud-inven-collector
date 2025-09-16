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
            _LOGGER.debug(f"Listing routers for NAT gateways in project {self.project_id}")
            request = self.client.routers().aggregatedList(**query)
            while request is not None:
                response = request.execute()
                for region_key, routers_scoped_list in response.get("items", {}).items():
                    if "routers" in routers_scoped_list:
                        # region_key에서 실제 region 이름 추출 (예: "regions/us-central1")
                        region_name = self._extract_region_from_key(region_key)
                        _LOGGER.debug(f"Found {len(routers_scoped_list['routers'])} routers in {region_name}")
                        
                        for router in routers_scoped_list["routers"]:
                            # NAT 구성이 있는 라우터 찾기
                            if "nats" in router:
                                _LOGGER.debug(f"Router {router.get('name')} has {len(router['nats'])} NAT configurations")
                                for nat in router["nats"]:
                                    nat_gateway = {
                                        "name": nat.get("name"),
                                        "router_name": router.get("name"),
                                        "region": region_name,
                                        "router_self_link": router.get("selfLink"),
                                        "self_link": router.get("selfLink"),  # NAT Gateway는 Router의 일부이므로 Router의 selfLink 사용
                                        "creation_timestamp": router.get("creationTimestamp"),
                                        "description": router.get("description", ""),
                                        "network": router.get("network", ""),
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
            _LOGGER.debug(f"Listing VPN gateways in project {self.project_id}")
            request = self.client.vpnGateways().aggregatedList(**query)
            while request is not None:
                response = request.execute()
                for region_key, vpn_gateways_scoped_list in response.get("items", {}).items():
                    if "vpnGateways" in vpn_gateways_scoped_list:
                        region_name = self._extract_region_from_key(region_key)
                        
                        for vpn_gateway in vpn_gateways_scoped_list["vpnGateways"]:
                            vpn_gateway.update({
                                "region": region_name,
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
                for region_key, target_vpn_gateways_scoped_list in response.get("items", {}).items():
                    if "targetVpnGateways" in target_vpn_gateways_scoped_list:
                        region_name = self._extract_region_from_key(region_key)
                        
                        for target_vpn_gateway in target_vpn_gateways_scoped_list["targetVpnGateways"]:
                            target_vpn_gateway.update({
                                "region": region_name,
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
                for region_key, routers_scoped_list in response.get("items", {}).items():
                    if "routers" in routers_scoped_list:
                        region_name = self._extract_region_from_key(region_key)
                        
                        for router in routers_scoped_list["routers"]:
                            router.update({
                                "region": region_name,
                                "project": self.project_id,
                            })
                            routers.append(router)
                
                request = self.client.routers().aggregatedList_next(
                    previous_request=request, previous_response=response
                )
        except Exception as e:
            _LOGGER.error(f"Error listing routers: {str(e)}")
            
        return routers

    def _extract_region_from_key(self, region_key):
        """
        aggregatedList API 응답의 region key에서 실제 region 이름을 추출합니다.
        
        Args:
            region_key: API 응답의 키 (예: "regions/us-central1", "zones/us-central1-a")
            
        Returns:
            str: region 이름 (예: "us-central1")
        """
        if region_key.startswith("regions/"):
            return region_key.split("regions/")[1]
        elif region_key.startswith("zones/"):
            # zones에서 region 추출 (예: "zones/us-central1-a" -> "us-central1")
            zone_name = region_key.split("zones/")[1]
            return "-".join(zone_name.split("-")[:-1])
        elif region_key == "global":
            return "global"
        else:
            # 예상치 못한 형식의 경우 그대로 반환
            _LOGGER.warning(f"Unexpected region key format: {region_key}")
            return region_key
