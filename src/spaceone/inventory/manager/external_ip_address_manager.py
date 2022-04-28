import time
import logging
from ipaddress import ip_address, IPv4Address

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.external_ip_address.cloud_service import *
from spaceone.inventory.connector.external_ip_address import ExternalIPAddressConnector
from spaceone.inventory.model.external_ip_address.cloud_service_type import CLOUD_SERVICE_TYPES

_LOGGER = logging.getLogger(__name__)


class ExternalIPAddressManager(GoogleCloudManager):
    connector_name = 'ExternalIPAddressConnector'
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug(f'** External IP Address START **')
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
        external_ip_addr_id = ""

        secret_data = params['secret_data']
        project_id = secret_data['project_id']

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        exp_conn: ExternalIPAddressConnector = self.locator.get_connector(self.connector_name, **params)
        all_addresses = exp_conn.list_addresses()
        vm_instances = exp_conn.list_instance_for_networks()
        forwarding_rule_address = exp_conn.list_forwarding_rule()

        # External IP contains, reserved IP(static) + vm IP(ephemeral) + forwarding rule IP
        all_external_ip_addresses = self._get_external_ip_addresses(all_addresses,
                                                                    vm_instances,
                                                                    forwarding_rule_address)

        for external_ip_addr in all_external_ip_addresses:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                region = external_ip_addr.get('region') if external_ip_addr.get('region', '') else 'global'
                external_ip_addr_id = external_ip_addr.get('id', '')

                ##################################
                # 2. Make Base Data
                ##################################
                external_ip_addr.update({
                    'project': secret_data['project_id'],
                    'status_display': external_ip_addr.get('status', '').replace('_', ' ').title()
                })
                if external_ip_addr.get('selfLink') is None:
                    external_ip_addr.update({
                        'self_link': self._get_external_self_link_when_its_empty(external_ip_addr)
                    })
                # No Labels (exists on console but No option on APIs)
                external_ip_addr_data = ExternalIpAddress(external_ip_addr, strict=False)

                ##################################
                # 3. Make Return Resource
                ##################################
                external_ip_addr_resource = ExternalIpAddressResource({
                    'name': external_ip_addr.get('name', ''),
                    'account': project_id,
                    'region_code': region,
                    'data': external_ip_addr_data,
                    'reference': ReferenceModel(external_ip_addr_data.reference())
                })

                ##################################
                # 4. Make Collected Region Code
                ##################################
                self.set_region_code(region)

                ##################################
                # 5. Make Resource Response Object
                # List of ExternalIpAddressResponse Object
                ##################################
                collected_cloud_services.append(ExternalIpAddressResponse({'resource': external_ip_addr_resource}))
            except Exception as e:
                _LOGGER.error(f'[collect_cloud_service] => {e}', exc_info=True)
                error_response = self.generate_resource_error_response(e, 'VPC', 'ExternalIPAddress', external_ip_addr_id)
                error_responses.append(error_response)

        _LOGGER.debug(f'** External IP Address Finished {time.time() - start_time} Seconds **')
        return collected_cloud_services, error_responses

    def _get_external_ip_addresses(self, all_addresses, all_instances, forwarding_rules):
        """
        Aggregates public ip address from different resource types
        - Static IP : all_addresses
        - Ephermeral IP : all_instances
        - Forwarding Rule(LoadBalancer) IP : forwarding_rules
        """
        all_ip_addr_vos = []
        all_ip_addr_only_check_dup = []

        for ip_addr in all_addresses:
            if 'EXTERNAL' == ip_addr.get('addressType'):
                url_region = ip_addr.get('region', '')
                users = ip_addr.get('users', [])
                ip_addr.update({
                    'region': self.get_param_in_url(url_region, 'regions') if url_region == '' else 'global',
                    'used_by': self._get_parse_users(users),
                    'ip_version_display': self._get_ip_address_version(ip_addr.get('address')),
                    'network_tier_display': ip_addr.get('networkTier', '').capitalize(),
                    'is_ephemeral': 'Static'
                })
                all_ip_addr_only_check_dup.append(ip_addr.get('address'))
                all_ip_addr_vos.append(ip_addr)

        for forwarding_rule in forwarding_rules:
            forwarding_ip_addr = forwarding_rule.get('IPAddress')
            if forwarding_rule.get(
                    'loadBalancingScheme') == 'EXTERNAL' and forwarding_ip_addr not in all_ip_addr_only_check_dup:
                rule_name = forwarding_rule.get('name')
                url_region = forwarding_rule.get('region', '')
                forwarding_rule.update({
                    'is_ephemeral': 'Ephemeral',
                    'ip_version_display': self._get_ip_address_version(forwarding_ip_addr),
                    'network_tier_display': forwarding_rule.get('networkTier', '').capitalize(),
                    'address_type': forwarding_rule.get('loadBalancingScheme'),
                    'address': forwarding_ip_addr,
                    'region': self.get_param_in_url(url_region, 'regions') if url_region != '' else 'global',
                    'status': 'IN_USE',
                    'users': [forwarding_rule.get('selfLink', '')],
                    'used_by': [f'Forwarding rule {rule_name}'],
                })
                all_ip_addr_only_check_dup.append(forwarding_ip_addr)
                all_ip_addr_vos.append(forwarding_rule)

        for instance in all_instances:
            network_interfaces = instance.get('networkInterfaces', [])
            zone = self.get_param_in_url(instance.get('zone', ''), 'zones')
            region = self.parse_region_from_zone(zone)
            for network_interface in network_interfaces:
                external_ip_infos = network_interface.get('accessConfigs', [])
                for external_ip_info in external_ip_infos:
                    if 'natIP' in external_ip_info and external_ip_info.get('natIP') not in all_ip_addr_only_check_dup:
                        instance_name = instance.get('name')
                        external_ip = {
                            'id': instance.get('id'),
                            'address': external_ip_info.get('natIP'),
                            'zone': zone,
                            'region': region,
                            'address_type': 'EXTERNAL',
                            'is_ephemeral': 'Ephemeral',
                            'network_tier': external_ip_info.get('networkTier'),
                            'network_tier_display': external_ip_info.get('networkTier', '').capitalize(),
                            'status': 'IN_USE',
                            'ip_version_display': self._get_ip_address_version(external_ip_info.get('natIP')),
                            'creation_timestamp': instance.get('creationTimestamp'),
                            'users': [instance.get('selfLink', '')],
                            'used_by': [f'Vm Instance {instance_name} ({zone})']
                        }
                        all_ip_addr_only_check_dup.append(external_ip_info.get('natIP', ''))
                        all_ip_addr_vos.append(external_ip)

        return all_ip_addr_vos

    @staticmethod
    def _get_ip_address_version(ip):
        try:
            return "IPv4" if type(ip_address(ip)) is IPv4Address else "IPv6"
        except ValueError:
            return "Invalid"

    def _get_parse_users(self, users):
        list_user = []
        for url_user in users:
            zone = self.get_param_in_url(url_user, 'zones')
            instance = self.get_param_in_url(url_user, 'instances')
            used_by = f'VM instance {instance} (Zone: {zone})'
            list_user.append(used_by)

        return list_user

    @staticmethod
    def _get_external_self_link_when_its_empty(external_ip):
        ip_address = external_ip.get('address', '')
        project_id = external_ip.get('project_id')
        zone = external_ip.get('zone')
        region = external_ip.get('region')
        return f'https://console.cloud.google.com/networking/addresses/project={project_id}/zone={zone}/ip_address/{ip_address}' \
            if zone else f'https://console.cloud.google.com/networking/addresses/project={project_id}/region/{region}/ip_address/{ip_address}'