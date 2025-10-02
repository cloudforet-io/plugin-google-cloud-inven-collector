import logging
import time

from spaceone.inventory.connector.networking.vpc_gateway import VPCGatewayConnector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import (
    ReferenceModel,
    log_state_summary,
    reset_state_counters,
)
from spaceone.inventory.libs.schema.cloud_service import ErrorResourceResponse
from spaceone.inventory.model.networking.vpc_gateway.cloud_service import (
    VPCGatewayResource,
    VPCGatewayResponse,
)
from spaceone.inventory.model.networking.vpc_gateway.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.networking.vpc_gateway.data import VPCGateway

_LOGGER = logging.getLogger(__name__)


class VPCGatewayManager(GoogleCloudManager):
    connector_name = "VPCGatewayConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug("** VPC Gateway START **")
        start_time = time.time()
        """
        Args:
            params:
                - options
                - schema
                - secret_data
                - filter
                - zones
        Response:
            CloudServiceResponse/ErrorResourceResponse
        """

        # v2.0 상태 추적 초기화
        reset_state_counters()

        collected_cloud_services = []
        error_responses = []
        gateway_id = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        vpc_gateway_conn: VPCGatewayConnector = self.locator.get_connector(
            self.connector_name, **params
        )

        # Get lists that relate with gateways through Google Cloud API
        nat_gateways = vpc_gateway_conn.list_nat_gateways()
        vpn_gateways = vpc_gateway_conn.list_vpn_gateways()

        # Process NAT Gateways
        for nat_gateway in nat_gateways:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                gateway_id = nat_gateway.get("name", "")
                region = self.match_region_info(nat_gateway.get("region", "global"))

                # 네트워크 정보 파싱
                network_name = self._get_network_name_from_url(
                    nat_gateway.get("network", "")
                )

                nat_gateway.update(
                    {
                        "gateway_type": "NAT_GATEWAY",
                        "project": project_id,
                        "network_name": network_name,
                        "nat_subnetworks": self._process_nat_subnetworks(
                            nat_gateway.get("subnetworks", [])
                        ),
                        "nat_log_config": nat_gateway.get("log_config"),
                        "timeouts": self._get_nat_timeouts(nat_gateway),
                    }
                )

                # No labels
                _name = nat_gateway.get("name", "")

                ##################################
                # 2. Make Base Data
                ##################################
                vpc_gateway_data = VPCGateway(nat_gateway, strict=False)

                ##################################
                # 3. Make Return Resource
                ##################################
                vpc_gateway_resource = VPCGatewayResource(
                    {
                        "name": _name,
                        "account": project_id,
                        "region_code": region.get("region_code"),
                        "data": vpc_gateway_data,
                        "reference": ReferenceModel(vpc_gateway_data.reference()),
                    }
                )

                ##################################
                # 4. Make Collected Region Code
                ##################################
                self.set_region_code(region.get("region_code"))

                ##################################
                # 5. Make Resource Response Object
                # v2.0 로깅 시스템 사용
                ##################################
                collected_cloud_services.append(
                    VPCGatewayResponse.create_with_logging(
                        resource=vpc_gateway_resource,
                        message=f"Successfully collected NAT Gateway: {_name}",
                    )
                )

            except Exception as e:
                _LOGGER.error(
                    f"[collect_cloud_service] NAT Gateway => {e}", exc_info=True
                )
                error_response = ErrorResourceResponse.create_with_logging(
                    error_message=f"Failed to collect NAT Gateway {gateway_id}: {str(e)}",
                    resource_type="inventory.CloudService",
                )
                error_responses.append(error_response)

        # Process VPN Gateways
        for vpn_gateway in vpn_gateways:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                gateway_id = vpn_gateway.get("name", "")
                region = self.match_region_info(vpn_gateway.get("region", "global"))

                # 네트워크 정보 파싱
                network_name = self._get_network_name_from_url(
                    vpn_gateway.get("network", "")
                )

                vpn_gateway.update(
                    {
                        "gateway_type": vpn_gateway.get("type", "VPN_GATEWAY"),
                        "project": project_id,
                        "network_name": network_name,
                        "vpn_interfaces_display": self._process_vpn_interfaces(
                            vpn_gateway.get("vpnInterfaces", [])
                        ),
                    }
                )

                # No labels
                _name = vpn_gateway.get("name", "")

                ##################################
                # 2. Make Base Data
                ##################################
                vpc_gateway_data = VPCGateway(vpn_gateway, strict=False)

                ##################################
                # 3. Make Return Resource
                ##################################
                vpc_gateway_resource = VPCGatewayResource(
                    {
                        "name": _name,
                        "account": project_id,
                        "region_code": region.get("region_code"),
                        "data": vpc_gateway_data,
                        "reference": ReferenceModel(vpc_gateway_data.reference()),
                    }
                )

                ##################################
                # 4. Make Collected Region Code
                ##################################
                self.set_region_code(region.get("region_code"))

                ##################################
                # 5. Make Resource Response Object
                # v2.0 로깅 시스템 사용
                ##################################
                collected_cloud_services.append(
                    VPCGatewayResponse.create_with_logging(
                        resource=vpc_gateway_resource,
                        message=f"Successfully collected VPN Gateway: {_name}",
                    )
                )

            except Exception as e:
                _LOGGER.error(
                    f"[collect_cloud_service] VPN Gateway => {e}", exc_info=True
                )
                error_response = ErrorResourceResponse.create_with_logging(
                    error_message=f"Failed to collect VPN Gateway {gateway_id}: {str(e)}",
                    resource_type="inventory.CloudService",
                )
                error_responses.append(error_response)

        # v2.0 수집 결과 요약 로깅
        log_state_summary()

        _LOGGER.debug(f"** VPC Gateway Finished {time.time() - start_time} Seconds **")
        return collected_cloud_services, error_responses

    def _get_network_name_from_url(self, network_url):
        """네트워크 URL에서 네트워크 이름을 추출합니다."""
        if network_url:
            return self.get_param_in_url(network_url, "networks")
        return ""

    def _process_nat_subnetworks(self, subnetworks):
        """NAT 서브네트워크 정보를 처리합니다."""
        processed_subnetworks = []
        for subnetwork in subnetworks:
            subnetwork_name = self.get_param_in_url(
                subnetwork.get("name", ""), "subnetworks"
            )
            processed_data = {
                "name": subnetwork_name,
                "source_ip_ranges_to_nat": subnetwork.get("sourceIpRangesToNat", []),
                "secondary_ip_range_names": subnetwork.get("secondaryIpRangeNames", []),
            }
            processed_subnetworks.append(processed_data)
        return processed_subnetworks

    def _process_vpn_interfaces(self, vpn_interfaces):
        """VPN 인터페이스 정보를 처리합니다."""
        processed_interfaces = []
        for interface in vpn_interfaces:
            interface_data = {
                "id": interface.get("id"),
                "ip_address": interface.get("ipAddress"),
                "interconnect_attachment": interface.get("interconnectAttachment", ""),
            }
            processed_interfaces.append(interface_data)
        return processed_interfaces

    def _get_nat_timeouts(self, nat_gateway):
        """NAT Gateway의 타임아웃 설정을 정리하여 반환합니다."""
        timeouts = {}

        if "icmpIdleTimeoutSec" in nat_gateway:
            timeouts["icmp_idle_timeout"] = f"{nat_gateway['icmpIdleTimeoutSec']}s"

        if "tcpEstablishedIdleTimeoutSec" in nat_gateway:
            timeouts["tcp_established_idle_timeout"] = (
                f"{nat_gateway['tcpEstablishedIdleTimeoutSec']}s"
            )

        if "tcpTransitoryIdleTimeoutSec" in nat_gateway:
            timeouts["tcp_transitory_idle_timeout"] = (
                f"{nat_gateway['tcpTransitoryIdleTimeoutSec']}s"
            )

        if "tcpTimeWaitTimeoutSec" in nat_gateway:
            timeouts["tcp_time_wait_timeout"] = (
                f"{nat_gateway['tcpTimeWaitTimeoutSec']}s"
            )

        if "udpIdleTimeoutSec" in nat_gateway:
            timeouts["udp_idle_timeout"] = f"{nat_gateway['udpIdleTimeoutSec']}s"

        return timeouts

    def get_network_name_from_url(self, network_url):
        """네트워크 URL에서 네트워크 이름을 추출합니다. (하위 호환성)"""
        return self._get_network_name_from_url(network_url)

    def extract_router_name_from_self_link(self, self_link):
        """Self Link에서 라우터 이름을 추출합니다."""
        if self_link:
            return self.get_param_in_url(self_link, "routers")
        return ""
