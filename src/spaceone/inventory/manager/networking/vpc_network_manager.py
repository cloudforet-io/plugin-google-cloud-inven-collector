import time
import logging
from ipaddress import ip_address, IPv4Address

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.connector.networking.vpc_network import VPCNetworkConnector
from spaceone.inventory.model.networking.vpc_network.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.networking.vpc_network.cloud_service import (
    VPCNetworkResource,
    VPCNetworkResponse,
)
from spaceone.inventory.model.networking.vpc_network.data import VPCNetwork, IPAddress

_LOGGER = logging.getLogger(__name__)


class VPCNetworkManager(GoogleCloudManager):
    connector_name = "VPCNetworkConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug(f"** VPC Network START **")
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
        network_id = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        vpc_conn: VPCNetworkConnector = self.locator.get_connector(
            self.connector_name, **params
        )

        # Get lists that relate with snapshots through Google Cloud API
        networks = vpc_conn.list_networks()
        firewalls = vpc_conn.list_firewall()
        subnets = vpc_conn.list_subnetworks()
        routes = vpc_conn.list_routes()
        regional_address = vpc_conn.list_regional_addresses()

        for network in networks:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                network_id = network.get("id")
                network_identifier = network.get("selfLink")
                matched_firewall = self._get_matched_firewalls(
                    network_identifier, firewalls
                )
                matched_route = self.get_matched_route(network_identifier, routes)
                matched_subnets = self._get_matched_subnets(network_identifier, subnets)
                region = self.match_region_info("global")
                peerings = self.get_peering(network)

                network.update(
                    {
                        "mode": (
                            "Auto" if network.get("autoCreateSubnetworks") else "Custom"
                        ),
                        "project": secret_data["project_id"],
                        "global_dynamic_route": self._get_global_dynamic_route(
                            network, "not_mode"
                        ),
                        "dynamic_routing_mode": self._get_global_dynamic_route(
                            network, "mode"
                        ),
                        "subnet_creation_mode": (
                            "Auto" if network.get("autoCreateSubnetworks") else "Custom"
                        ),
                        "ip_address_data": self.get_internal_ip_address_in_use(
                            network, regional_address
                        ),
                        "peerings": peerings,
                        "route_data": {
                            "total_number": len(matched_route),
                            "route": matched_route,
                        },
                        "firewall_data": {
                            "total_number": len(matched_firewall),
                            "firewall": matched_firewall,
                        },
                        "subnetwork_data": {
                            "total_number": len(matched_subnets),
                            "subnets": matched_subnets,
                        },
                    }
                )

                # No labels
                _name = network.get("name", "")

                ##################################
                # 2. Make Base Data
                ##################################
                vpc_data = VPCNetwork(network, strict=False)

                ##################################
                # 3. Make Return Resource
                ##################################
                vpc_resource = VPCNetworkResource(
                    {
                        "name": _name,
                        "account": project_id,
                        "region_code": region.get("region_code"),
                        "data": vpc_data,
                        "reference": ReferenceModel(vpc_data.reference()),
                    }
                )

                ##################################
                # 4. Make Collected Region Code
                ##################################
                self.set_region_code("global")

                ##################################
                # 5. Make Resource Response Object
                # List of LoadBalancingResponse Object
                ##################################
                collected_cloud_services.append(
                    VPCNetworkResponse({"resource": vpc_resource})
                )
            except Exception as e:
                _LOGGER.error(f"[collect_cloud_service] => {e}", exc_info=True)
                error_response = self.generate_resource_error_response(
                    e, "VPC", "VPCNetwork", network_id
                )
                error_responses.append(error_response)

        _LOGGER.debug(f"** VPC Network Finished {time.time() - start_time} Seconds **")
        return collected_cloud_services, error_responses

    def get_internal_ip_address_in_use(self, network, regional_address):
        all_internal_addresses = []

        for ip_address in regional_address:
            ip_type = ip_address.get("addressType", "")
            subnetwork = ip_address.get("subnetwork", "")

            if ip_type == "INTERNAL" and subnetwork in network.get("subnetworks", []):
                url_region = ip_address.get("region")
                users = ip_address.get("users")
                ip_address.update(
                    {
                        "subnet_name": network.get("name"),
                        "ip_version_display": self._valid_ip_address(
                            ip_address.get("address")
                        ),
                        "region": (
                            self.get_param_in_url(url_region, "regions")
                            if url_region
                            else "global"
                        ),
                        "used_by": self._get_parse_users(users) if users else ["None"],
                        "is_ephemeral": "Static",
                    }
                )

                all_internal_addresses.append(IPAddress(ip_address, strict=False))

        return all_internal_addresses

    def get_peering(self, network):
        updated_peering = []
        for peer in network.get("peerings", []):
            url_network = peer.get("network", "")

            ex_custom = "None"
            if peer.get("exportCustomRoutes") and peer.get("importCustomRoutes"):
                ex_custom = "Import & Export custom routes"
            elif peer.get("exportCustomRoutes"):
                ex_custom = "Export custom routes"
            elif peer.get("importCustomRoutes"):
                ex_custom = "Import custom routes"

            ex_route = "None"
            if peer.get("exportSubnetRoutesWithPublicIp") and peer.get(
                "importSubnetRoutesWithPublicIp"
            ):
                ex_route = "Import & Export subnet routes with public IP"
            elif peer.get("exportSubnetRoutesWithPublicIp"):
                ex_route = "Export subnet routes with public IP"
            elif peer.get("importSubnetRoutesWithPublicIp"):
                ex_route = "Import subnet routes with public IP"

            display = {
                "your_network": network.get("name", ""),
                "peered_network": self.get_param_in_url(url_network, "networks"),
                "project_id": self.get_param_in_url(url_network, "projects"),
                "state_display": peer.get("state").capitalize(),
                "ex_custom_route": ex_custom,
                "ex_route_public_ip_display": ex_route,
            }
            peer.update({"display": display})
            updated_peering.append(peer)
        return updated_peering

    def get_matched_route(self, network, routes):
        route_vos = []

        for route in routes:
            if network == route.get("network", ""):
                next_hop = ""
                if "nextHopInstance" in route:
                    url_next_hop_instance = route.get("nextHopInstance", "")
                    target = self.get_param_in_url(url_next_hop_instance, "instances")
                    zone = self.get_param_in_url(url_next_hop_instance, "zones")
                    next_hop = f"Instance {target} (zone  {zone})"

                elif "nextHopIp" in route:
                    target = route.get("nextHopIp")
                    next_hop = f"IP address lie within {target}"

                elif "nextHopNetwork" in route:
                    url_next_hop_network = route.get("nextHopNetwork", "")
                    target = self.get_param_in_url(url_next_hop_network, "networks")
                    next_hop = f"Virtual network {target}"

                elif "nextHopGateway" in route:
                    url_next_hop_gateway = route.get("nextHopGateway", "")
                    target = self.get_param_in_url(url_next_hop_gateway, "gateways")
                    next_hop = f"{target} internet gateway"
                # TODO: some type is ipaddress => 10.128.0.56
                elif "nextHopIlb" in route:
                    url_next_hop_ilb = route.get("nextHopIlb", "")
                    target = self.get_param_in_url(url_next_hop_ilb, "forwardingRules")
                    next_hop = f" Loadbalancer on {target}"

                elif "nextHopPeering" in route:
                    target = route.get("nextHopPeering")
                    next_hop = f"Peering : {target}"

                route.update(
                    {
                        "next_hop": next_hop,
                    }
                )
                route_vos.append(route)
        return route_vos

    def _get_matched_subnets(self, network, subnets):
        matched_subnet = []
        for subnet in subnets:
            if network == subnet.get("network", ""):
                log_config = subnet.get("logConfig", {})
                url_region = subnet.get("region")
                subnet.update(
                    {
                        "region": self.get_param_in_url(url_region, "regions"),
                        "google_access": (
                            "On" if subnet.get("privateIpGoogleAccess") else "Off"
                        ),
                        "flow_log": "On" if log_config.get("enable") else "Off",
                    }
                )
                matched_subnet.append(subnet)
        return matched_subnet

    @staticmethod
    def _get_matched_firewalls(network, firewalls):
        firewall_vos = []

        for firewall in firewalls:
            if network == firewall.get("network", ""):
                target_tag = firewall.get("targetTags", [])
                filter_range = ", ".join(firewall.get("sourceRanges", ""))
                log_config = firewall.get("log_config", {})

                protocol_port = []
                flag = "allowed" if "allowed" in firewall else "denied"
                for allowed in firewall.get(flag, []):
                    ip_protocol = allowed.get("IPProtocol", "")

                    for port in allowed.get("ports", []):
                        protocol_port.append(f"{ip_protocol}: {port}")

                display = {
                    "type_display": (
                        "Ingress"
                        if firewall.get("direction") == "INGRESS"
                        else "Egress"
                    ),
                    "target_display": (
                        ["Apply to all"] if not target_tag else target_tag
                    ),
                    "filter": f"IP ranges: {filter_range}",
                    "protocols_port": protocol_port,
                    "action": "Allow" if "allowed" in firewall else "Deny",
                    "logs": "On" if log_config.get("enable") else "Off",
                }

                firewall.update({"display": display})

                firewall_vos.append(firewall)
        return firewall_vos

    @staticmethod
    def _valid_ip_address(ip):
        try:
            return "IPv4" if type(ip_address(ip)) is IPv4Address else "IPv6"
        except ValueError:
            return "Invalid"

    @staticmethod
    def _get_global_dynamic_route(network, flag):
        routing_config = network.get("routingConfig", {})
        if flag == "mode":
            return "Regional" if routing_config == "REGIONAL" else "Global"
        else:
            return "Off" if routing_config == "REGIONAL" else "On"

    def _get_parse_users(self, users):
        parsed_used_by = []
        for url_user in users:
            zone = self.get_param_in_url(url_user, "zones")
            instance = self.get_param_in_url(url_user, "instances")
            used = f"VM instance {instance} (Zone: {zone})"
            parsed_used_by.append(used)

        return parsed_used_by
