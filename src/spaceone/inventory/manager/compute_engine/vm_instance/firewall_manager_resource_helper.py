import logging

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.model.compute_engine.instance.data import SecurityGroup

_LOGGER = logging.getLogger(__name__)


class FirewallManagerResourceHelper(GoogleCloudManager):
    connector_name = 'VMInstanceConnector'

    def list_firewall_rules_info(self, instance, firewall_rules) -> list:
        firewall_rules_results = []
        inst_network_info = self._get_instance_network_info(instance)

        for firewall_rule in firewall_rules:
            if firewall_rule.get('network') in inst_network_info:
                # 0. network target tag matching
                if self._chk_network_tag_is_matched(instance, firewall_rule):
                    firewall_rules_results.extend(self.list_firewall_rule_data(firewall_rule))
                # 1. target service account matching
                elif self._chk_service_account_is_matched(instance, firewall_rule):
                    firewall_rules_results.extend(self.list_firewall_rule_data(firewall_rule))
                # 2. FW rule applies to all instances in subnet
                elif ('targetTags' not in firewall_rule) & ('targetServiceAccounts' not in firewall_rule):
                    firewall_rules_results.extend(self.list_firewall_rule_data(firewall_rule))
            else:
                pass
        return firewall_rules_results

    def list_firewall_rule_data(self, firewall_rule) -> list:
        security_groups = []

        fw_origin = {
            'id': firewall_rule.get('id', ''),
            'name': firewall_rule.get('name', ''),
            'description': firewall_rule.get('description', ''),
            'priority': firewall_rule.get('priority', ''),
            'direction': firewall_rule.get('direction', '').lower(),
            'action': self._get_action(firewall_rule),
            'source_cidrs': firewall_rule.get('sourceRanges', []),
            'destination_cidrs': firewall_rule.get('destinationRanges', []),
            'source_tags': firewall_rule.get('sourceTags', []),
            'target_tags': [],
            'service_accounts': [],
            'protocols': self._list_protocols(firewall_rule)
        }
        # Translate firewall_rule into security group model
        '''
        Base of protocol/ports mappings are complex
        Tear them into single protocol/port set
        [{'IPProtocol': 'tcp', 'ports': ['100-200']}, {'IPProtocol': 'udp', 'ports': ['100-400']}]
        '''
        '''
            sg_translated = {
                'priority': fw_origin.get('priority', ''),
                'protocol': port_mappings.get('IPProtocol', ''),
                'remote': '',
                'remote_id': '',
                'remote_cidr': '',
                'security_group_name': fw_origin.get('name', ''),
                'port_range_min': '',
                'port_range_max': '',
                'security_group_id': fw_origin.get('id', ''),
                'description': fw_origin.get('description', ''),
                'direction': self._get_direction(fw_origin),
                'port': '',
                'action': fw_origin.get('action', '')
            }
        '''
        for protocol in fw_origin.get('protocols', []):
            sg_translated = {
                'priority': fw_origin.get('priority', ''),
                'protocol': protocol.get('IPProtocol', ''),
                'security_group_name': fw_origin.get('name', ''),
                'security_group_id': fw_origin.get('id', ''),
                'description': fw_origin.get('description', ''),
                'direction': self._get_direction(fw_origin),
                'action': fw_origin.get('action', '')
            }
            # Check if applies to all ports
            if sg_translated.get('IPProtocol') == 'all':
                sg_translated.update({
                    'port_range_min': '0',
                    'port_range_max': '65535'
                })
            else:
                for port in protocol.get('ports', []):
                    port_min, port_max = self._get_port_min_max(port)
                    sg_translated.update({
                        'port_range_min': port_min,
                        'port_range_max': port_max
                        })
                    security_groups.append(SecurityGroup(sg_translated, strict=False))

        return security_groups

    @staticmethod
    def _get_port_min_max(port) -> tuple:
        """
        :param port: ['80'] or ['70 - 200']
        :return: ('80', '80') or ('70', '200')
        """
        if len(port.split('-')) == 1:
            port_min = port.split('-')[0]
            port_max = port.split('-')[0]
        else:
            port_min = port.split('-')[0]
            port_max = port.split('-')[1]

        return port_min, port_max

    @staticmethod
    def _get_direction(firewall_rule):
        if firewall_rule.get('direction', '') == "INGRESS":
            return 'inbound'
        else:
            return 'outbound'

    @staticmethod
    def _get_action(firewall):
        if 'allowed' in firewall:
            return 'allow'
        else:
            return 'deny'

    @staticmethod
    def _chk_network_tag_is_matched(instance, firewall) -> bool:
        matched = False
        # compares all fw target tags and instance tags
        for fw_target_tag in firewall.get('targetTags', []):
            for tag in instance.get('tags', {}).get('items', []):
                if tag == fw_target_tag:
                    matched = True
        return matched

    @staticmethod
    def _chk_service_account_is_matched(instance, firewall) -> bool:
        matched = False
        # compares all fw target service account and instance service account
        for instance_service_account in instance.get('serviceAccounts', []):
            for fw_service_account in firewall.get('targetServiceAccounts', []):
                if instance_service_account.get('email', '') == fw_service_account:
                    matched = True
        return matched

    @staticmethod
    def _get_instance_network_info(instance):
        inst_network_interfaces = instance.get('networkInterfaces', [])
        return [d.get('network') for d in inst_network_interfaces if d.get('network', '') != '']

    @staticmethod
    def _list_protocols(firewall):
        protocols = []
        if 'allowed' in firewall:
            protocols = firewall.get('allowed')
        elif 'denied' in firewall:
            protocols = firewall.get('denied')
        return protocols


