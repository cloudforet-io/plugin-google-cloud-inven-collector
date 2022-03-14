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

        exp_conn: ExternalIPAddressConnector = self.locator.get_connector(self.connector_name, **params)
        regional_global_addresses = exp_conn.list_regional_addresses()
        compute_engine_vm_address = exp_conn.list_instance_for_networks()
        forwarding_rule_address = exp_conn.list_forwarding_rule()

        # Get lists that relate with snapshots through Google Cloud API
        all_external_ip_addresses = self.get_external_ip_addresses(regional_global_addresses,
                                                                   compute_engine_vm_address,
                                                                   forwarding_rule_address)

        for external_ip_juso in all_external_ip_addresses:
            try:
                region = external_ip_juso.get('region') if external_ip_juso.get('region') else 'global'
                external_ip_juso.update({'project': secret_data['project_id'],
                                         'status_display': external_ip_juso.get('status').replace('_', ' ').title()
                                         })
                if external_ip_juso.get('selfLink') is None:
                    external_ip_juso.update({'self_link': self._get_external_self_link_when_its_empty(external_ip_juso)})

                # No Labels (exists on console but No option on APIs)
                _name = external_ip_juso.get('name', '')
                external_ip_addr_id = external_ip_juso.get('id')
                external_ip_juso_data = ExternalIpAddress(external_ip_juso, strict=False)
                external_ip_juso_resource = ExternalIpAddressResource({
                    'name': _name,
                    'account': project_id,
                    'region_code': region,
                    'data': external_ip_juso_data,
                    'reference': ReferenceModel(external_ip_juso_data.reference())
                })

                self.set_region_code(region)
                collected_cloud_services.append(ExternalIpAddressResponse({'resource': external_ip_juso_resource}))
            except Exception as e:
                _LOGGER.error(f'[collect_cloud_service] => {e}', exc_info=True)
                error_response = self.generate_resource_error_response(e, 'VPC', 'ExternalIPAddress', external_ip_addr_id)
                error_responses.append(error_response)

        _LOGGER.debug(f'** External IP Address Finished {time.time() - start_time} Seconds **')
        return collected_cloud_services, error_responses

    def get_external_ip_addresses(self, regional_address, instances_over_region, forwarding_rules):

        all_ip_juso_vos = []
        all_ip_juso_only_check_dup = []

        for ip_juso in regional_address:
            if 'EXTERNAL' == ip_juso.get('addressType'):
                simple_region = ip_juso.get('region')
                users = ip_juso.get('users')
                ip_juso.update({
                    'region': simple_region[simple_region.rfind('/') + 1:] if simple_region else 'global',
                    'used_by': self._get_parse_users(users) if users else [],
                    'ip_version_display': self._valid_ip_address(ip_juso.get('address')),
                    'network_tier_display': self._get_network_tier_display(ip_juso),
                    'is_ephemeral': 'Static'
                })
                all_ip_juso_only_check_dup.append(ip_juso.get('address'))
                all_ip_juso_vos.append(ip_juso)

        for forwarding_rule in forwarding_rules:
            forwarding_ip_juso = forwarding_rule.get('IPAddress')
            if forwarding_rule.get(
                    'loadBalancingScheme') == 'EXTERNAL' and forwarding_ip_juso not in all_ip_juso_only_check_dup:
                rule_name = forwarding_rule.get('name')
                forwarding_rule.update({
                    'is_ephemeral': 'Ephemeral',
                    'ip_version_display': self._valid_ip_address(forwarding_ip_juso),
                    'network_tier_display': self._get_network_tier_display(forwarding_rule),
                    'address_type': forwarding_rule.get('loadBalancingScheme'),
                    'address': forwarding_ip_juso,
                    'region': self._get_region_from_forwarding_rule(forwarding_rule),
                    'status': 'IN_USE',
                    'users': [forwarding_rule.get('selfLink')],
                    'used_by': [f'Forwarding rule {rule_name}'],
                })
                all_ip_juso_only_check_dup.append(forwarding_ip_juso)
                all_ip_juso_vos.append(forwarding_rule)

        for instance in instances_over_region:
            network_interfaces = instance.get('networkInterfaces', [])
            zone = self._get_matched_last_target('zone', instance)
            region = zone[:-2]
            for network_interface in network_interfaces:
                external_ip_infos = network_interface.get('accessConfigs', [])
                for external_ip_info in external_ip_infos:
                    if 'natIP' in external_ip_info and external_ip_info.get('natIP') not in all_ip_juso_only_check_dup:
                        instance_name = instance.get('name')
                        external_ip = {
                            'id': instance.get('id'),
                            'address': external_ip_info.get('natIP'),
                            'zone': zone,
                            'region': region,
                            'address_type': 'EXTERNAL',
                            'is_ephemeral': 'Ephemeral',
                            'network_tier': external_ip_info.get('networkTier'),
                            'network_tier_display': self._get_network_tier_display(external_ip_info),
                            'status': 'IN_USE',
                            'ip_version_display': self._valid_ip_address(external_ip_info.get('natIP')),
                            'creation_timestamp': instance.get('creationTimestamp'),
                            'users': [instance.get('selfLink')],
                            'used_by': [f'Vm Instance {instance_name} ({zone})']
                        }
                        all_ip_juso_only_check_dup.append(external_ip_info.get('natIP'))
                        all_ip_juso_vos.append(external_ip)

        return all_ip_juso_vos

    @staticmethod
    def _valid_ip_address(ip):
        try:
            return "IPv4" if type(ip_address(ip)) is IPv4Address else "IPv6"
        except ValueError:
            return "Invalid"

    @staticmethod
    def _get_region_from_forwarding_rule(forwarding_rule):
        self_link = forwarding_rule.get('selfLink')
        parsed_link = self_link[self_link.find('projects/') + 9:]
        _parsed_link = self_link[self_link.find('/forwardingRules/') + 9:]
        return 'global' if parsed_link == '' else \
            parsed_link[parsed_link.find('regions/') + 8:parsed_link.find('/forwardingRules')] \
                if parsed_link.find('regions/') > -1 else parsed_link[parsed_link.find('/') + 1:parsed_link.find('/forwardingRules')]

    @staticmethod
    def _get_network_tier_display(external_ip_info):
        display_value = ''
        if external_ip_info.get('networkTier') is not None:
            display_value = external_ip_info.get('networkTier').capitalize()
        return display_value

    @staticmethod
    def _get_parse_users(users):
        parsed_used_by = []
        for user in users:
            zone = user[user.find('zones') + 6:user.find('/instances')]
            instance = user[user.rfind('/') + 1:]
            used = f'VM instance {instance} (Zone: {zone})'
            parsed_used_by.append(used)

        return parsed_used_by

    @staticmethod
    def _get_matched_last_target(key, source):
        a = source.get(key, '')
        return a[a.rfind('/') + 1:]

    @staticmethod
    def _get_external_self_link_when_its_empty(external_ip):
        ip_address = external_ip.get('address', '')
        project_id = external_ip.get('project_id')
        zone = external_ip.get('zone')
        region = external_ip.get('region')
        return f'https://console.cloud.google.com/networking/addresses/project={project_id}/zone={zone}/ip_address/{ip_address}' \
            if zone else f'https://console.cloud.google.com/networking/addresses/project={project_id}/region/{region}/ip_address/{ip_address}'