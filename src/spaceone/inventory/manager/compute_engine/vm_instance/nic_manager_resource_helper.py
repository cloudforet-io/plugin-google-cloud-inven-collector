from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.model.compute_engine.instance.data import NIC


class NICManagerResourceHelper(GoogleCloudManager):

    connector_name = 'VMInstanceConnector'

    def get_nic_info(self, instance, subnet_vo):
        """
        nic_data = {
            "device_index": 0,
            "device": "",
            "cidr": "",
            "ip_addresses": [],
            "mac_address": "",
            "public_ip_address": "",
            "tags": {
                "public_dns": "",
            }
        }
        """
        nics = []
        network_interfaces = instance.get('networkInterfaces', [])
        for idx, network in enumerate(network_interfaces):
            ip_addresses, public_ip = self._get_ip_addresses(network)
            nic_data = {
                'device_index': idx,
                'ip_addresses': ip_addresses,
                'device': '',
                'nic_type': 'Virtual',
                'cidr': subnet_vo.get('cidr', ''),
                'public_ip_address': public_ip,
                'tags': {}
            }

            nics.append(NIC(nic_data, strict=False))

        return nics

    @staticmethod
    def _get_ip_addresses(network):
        ip_addresses = []
        public_ip_address = ''
        private_ip = network.get('networkIP', '')
        access_configs = network.get('accessConfigs', [])
        if private_ip != '':
            ip_addresses.append(private_ip)

        for idx, access_config in enumerate(access_configs):
            nat_ip = access_config.get('natIP', '')
            if nat_ip != '':
                # ip_addresses.append(nat_ip)
                if idx == 0:
                    public_ip_address = nat_ip

        return ip_addresses, public_ip_address

