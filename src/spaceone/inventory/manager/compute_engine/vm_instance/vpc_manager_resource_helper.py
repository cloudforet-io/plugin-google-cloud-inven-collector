import logging

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.model.compute_engine.instance.data import VPC, Subnet

_LOGGER = logging.getLogger(__name__)


class VPCManagerResourceHelper(GoogleCloudManager):

    connector_name = 'VMInstanceConnector'

    def get_vpc_info(self, instance, vpcs, subnets):
        """
        vpc_data = {
            "vpc_id": "",
            "vpc_name": "",
            "description": "",
            "self_link": ""
        }

        subnet_data = {
            "subnet_id": "",
            "subnet_name": "",
            "self_link": "",
            "gateway_address": "",
            "vpc" : VPC
            "cidr": ""
        }
        """

        vpc_data = {}
        subnet_data = {}

        # To get vpc, subnet related to instance
        matched_subnet = self._get_matching_subnet(instance, subnets)
        matched_vpc = self._get_matching_vpc(matched_subnet, vpcs)

        vpc_data.update({
            'vpc_id': matched_vpc.get('id', ''),
            'vpc_name': matched_vpc.get('name', ''),
            'description': matched_vpc.get('description', ''),
            'self_link': matched_vpc.get('selfLink', ''),
        })

        subnet_data.update({
            'subnet_id': matched_subnet.get('id', ''),
            'cidr': matched_subnet.get('ipCidrRange', ''),
            'subnet_name': matched_subnet.get('name', ''),
            'gateway_address': matched_subnet.get('gatewayAddress', ''),
            'vpc': vpc_data,
            'self_link': matched_subnet.get('selfLink', '')
        })

        return VPC(vpc_data, strict=False), Subnet(subnet_data, strict=False)

    @staticmethod
    def _get_matching_vpc(matched_subnet, vpcs) -> dict:
        matching_vpc = {}
        network = matched_subnet.get('selfLink', None)
        # Instance cannot be placed in multiple VPCs(Break after first matched result)
        if network is not None:
            for vpc in vpcs:
                if network in vpc.get('subnetworks', []):
                    matching_vpc = vpc
                    break

        return matching_vpc

    @staticmethod
    def _get_matching_subnet(instance, subnets) -> dict:
        subnet_data = {}
        subnetwork_links = []

        network_interfaces = instance.get('networkInterfaces', [])
        for network_interface in network_interfaces:
            """ 
            Subnet Type
            - auto subnet/custom subnet : reference selfLink is supported 
            - legacy : reference selfLink is not supported
            """
            subnetwork = network_interface.get('subnetwork', '')
            if subnetwork != '':
                subnetwork_links.append(subnetwork)
        # Need to enhanced(multiple networkInterface in multiple subnets)
        for subnet in subnets:
            if subnet.get('selfLink', '') in subnetwork_links:
                subnet_data = subnet
                break

        return subnet_data

    @staticmethod
    def _get_network_str(subnet):
        network = subnet.get('network', '')
        return network[network.find('/projects/'):len(network)] if network != '' else None
