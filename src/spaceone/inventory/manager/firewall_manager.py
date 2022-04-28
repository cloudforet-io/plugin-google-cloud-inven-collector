import time
import logging
from ipaddress import ip_address, IPv4Address

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.firewall.cloud_service import *
from spaceone.inventory.connector.firewall import FirewallConnector
from spaceone.inventory.model.firewall.cloud_service_type import CLOUD_SERVICE_TYPES

_LOGGER = logging.getLogger(__name__)


class FirewallManager(GoogleCloudManager):
    connector_name = 'FirewallConnector'
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug(f'** Firewall START **')
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
        firewall_id = ""

        secret_data = params['secret_data']
        project_id = secret_data['project_id']

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        firewall_conn: FirewallConnector = self.locator.get_connector(self.connector_name, **params)

        # Get lists that relate with snapshots through Google Cloud API
        firewalls = firewall_conn.list_firewall()
        all_instances = firewall_conn.list_instance_for_networks()
        region = 'global'

        for firewall in firewalls:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                firewall_id = firewall.get('id')
                target_tag = firewall.get('targetTags', [])
                filter_range = ', '.join(firewall.get('sourceRanges', ''))
                log_config = firewall.get('log_config', {})

                ##################################
                # 2. Make Base Data
                ##################################
                protocol_port = []
                flag = 'allowed' if 'allowed' in firewall else 'denied'
                for allowed in firewall.get(flag, []):
                    ip_protocol = allowed.get('IPProtocol', '')

                    for port in allowed.get('ports', []):
                        protocol_port.append(f'{ip_protocol}: {port}')

                display = {
                    'enforcement': 'Disabled' if firewall.get('disabled') else 'Enabled',
                    'network_display': self.get_param_in_url(firewall.get('network', ''), 'networks'),
                    'direction_display': 'Ingress' if firewall.get('direction') == 'INGRESS' else 'Egress',
                    'target_display': ['Apply to all'] if not target_tag else target_tag,
                    'filter': f'IP ranges: {filter_range}',
                    'protocols_port': protocol_port,
                    'action': 'Allow' if 'allowed' in firewall else 'Deny',
                    'logs': 'On' if log_config.get('enable') else 'Off'
                }

                firewall.update({
                    'project': secret_data['project_id'],
                    'applicable_instance': self._get_matched_instance(firewall,
                                                                      secret_data['project_id'],
                                                                      all_instances),
                    'display': display
                })

                # No Labels on API
                _name = firewall.get('data', '')
                firewall_data = Firewall(firewall, strict=False)


                ##################################
                # 3. Make Return Resource
                ##################################
                firewall_resource = FirewallResource({
                    'name': _name,
                    'account': project_id,
                    'region_code': region,
                    'data': firewall_data,
                    'reference': ReferenceModel(firewall_data.reference())
                })


                ##################################
                # 4. Make Collected Region Code
                ##################################
                self.set_region_code(region)

                ##################################
                # 5. Make Resource Response Object
                # List of LoadBalancingResponse Object
                ##################################
                collected_cloud_services.append(FirewallResponse({'resource': firewall_resource}))
            except Exception as e:
                _LOGGER.error(f'[collect_cloud_service] => {e}', exc_info=True)
                error_response = self.generate_resource_error_response(e, 'VPC', 'Firewall', firewall_id)
                error_responses.append(error_response)

        _LOGGER.debug(f'** Firewall Finished {time.time() - start_time} Seconds **')
        return collected_cloud_services, error_responses

    def _get_matched_instance(self, firewall, project_id, all_instances):
        matched_instances_vos = []
        firewall_network = firewall.get('network')
        for instance in all_instances:
            network_interfaces = instance.get('networkInterfaces', [])
            zone = self.get_param_in_url(instance.get('zone', ''), 'zones')
            region = self.parse_region_from_zone(zone)
            for network_interface in network_interfaces:
                if firewall_network == network_interface.get('network', ''):
                    instance = {
                        'id': instance.get('id'),
                        'name': instance.get('name'),
                        'zone': zone,
                        'region': region,
                        'address': network_interface.get('networkIP'),
                        'subnetwork': self.get_param_in_url(network_interface.get('subnetwork', ''), 'subnetworks'),
                        'tags': instance.get('tags', {}).get('items', []),
                        'project': project_id,
                        'service_accounts': self._get_service_accounts(instance.get('serviceAccounts', [])),
                        'creation_timestamp': instance.get('creationTimestamp'),
                        'labels': self.convert_labels_format(instance.get('labels', {})),
                        'labels_display': self._get_label_display(instance.get('labels', {})),
                    }
                    matched_instances_vos.append(ComputeVM(instance, strict=False))
        return matched_instances_vos

    @staticmethod
    def _get_label_display(labels):
        displays = []
        for label in labels:
            value = labels.get(label, '')
            displays.append(f'{label}: {value}')
        return displays

    @staticmethod
    def _valid_ip_address(ip):
        try:
            return "IPv4" if type(ip_address(ip)) is IPv4Address else "IPv6"
        except ValueError:
            return "Invalid"

    @staticmethod
    def _get_service_accounts(service_accounts):
        service_accounts_list = []
        for service_account in service_accounts:
            service_accounts_list.append(service_account.get('email'))

        if not service_accounts_list:
            service_accounts_list.append('None')
        return service_accounts_list
