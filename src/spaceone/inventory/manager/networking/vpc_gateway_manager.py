import time
import logging

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.connector.networking.vpc_gateway import VPCGatewayConnector
from spaceone.inventory.model.networking.vpc_gateway.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.networking.vpc_gateway.cloud_service import (
    VPCGatewayResource,
    VPCGatewayResponse,
)
from spaceone.inventory.model.networking.vpc_gateway.data import VPCGateway

_LOGGER = logging.getLogger(__name__)


class VPCGatewayManager(GoogleCloudManager):
    connector_name = "VPCGatewayConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        """VPC Gateway 정보를 수집합니다."""
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

        # NAT Gateway 수집
        nat_gateways = vpc_gateway_conn.list_nat_gateways()
        _LOGGER.debug(f"** NAT Gateways: {len(nat_gateways)} **")

        for nat_gateway in nat_gateways:
            try:
                gateway_id = nat_gateway.get("name", "")
                
                ##################################
                # 1. Set Basic Information
                ##################################
                region = self.match_region_info(nat_gateway.get("region", "global"))
                
                # NAT Gateway 데이터 구성
                nat_gateway.update({
                    "gateway_type": "NAT_GATEWAY",
                    "project": project_id,
                    "nat_subnetworks": nat_gateway.get("subnetworks", []),
                    "nat_log_config": nat_gateway.get("log_config"),
                })

                # No labels for NAT Gateway
                _name = nat_gateway.get("name", "")

                vpc_gateway_data = VPCGateway(nat_gateway, strict=False)

                vpc_gateway_resource = VPCGatewayResource(
                    {
                        "name": _name,
                        "account": project_id,
                        "region_code": region.get("region_code"),
                        "data": vpc_gateway_data,
                        "reference": ReferenceModel(vpc_gateway_data.reference()),
                    }
                )

                # 응답 생성
                collected_cloud_services.append(
                    VPCGatewayResponse({"resource": vpc_gateway_resource})
                )

            except Exception as e:
                _LOGGER.error(f"Error processing NAT Gateway {gateway_id}: {str(e)}")
                error_response = self.generate_resource_error_response(
                    e, "Networking", "VPCGateway", gateway_id
                )
                error_responses.append(error_response)

        # VPN Gateway 수집
        vpn_gateways = vpc_gateway_conn.list_vpn_gateways()
        _LOGGER.debug(f"** VPN Gateways: {len(vpn_gateways)} **")

        for vpn_gateway in vpn_gateways:
            try:
                gateway_id = vpn_gateway.get("name", "")
                
                ##################################
                # 1. Set Basic Information
                ##################################
                region = self.match_region_info(vpn_gateway.get("region", "global"))
                
                # VPN Gateway 데이터 구성
                vpn_gateway.update({
                    "project": project_id,
                })

                # No labels for VPN Gateway
                _name = vpn_gateway.get("name", "")

                vpc_gateway_data = VPCGateway(vpn_gateway, strict=False)

                vpc_gateway_resource = VPCGatewayResource(
                    {
                        "name": _name,
                        "account": project_id,
                        "region_code": region.get("region_code"),
                        "data": vpc_gateway_data,
                        "reference": ReferenceModel(vpc_gateway_data.reference()),
                    }
                )

                # 응답 생성
                collected_cloud_services.append(
                    VPCGatewayResponse({"resource": vpc_gateway_resource})
                )

            except Exception as e:
                _LOGGER.error(f"Error processing VPN Gateway {gateway_id}: {str(e)}")
                error_response = self.generate_resource_error_response(
                    e, "Networking", "VPCGateway", gateway_id
                )
                error_responses.append(error_response)

        _LOGGER.debug(
            f"** VPC Gateway Finished {time.time() - start_time} Seconds **"
        )

        return collected_cloud_services, error_responses

    def get_network_name_from_url(self, network_url):
        """네트워크 URL에서 네트워크 이름을 추출합니다."""
        if network_url:
            return network_url.split("/")[-1]
        return ""

    def extract_router_name_from_self_link(self, self_link):
        """Self Link에서 라우터 이름을 추출합니다."""
        if self_link:
            return self_link.split("/")[-1]
        return ""
