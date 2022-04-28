import time
import logging

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.connector.networking.route import RouteConnector
from spaceone.inventory.model.networking.route.cloud_service_type import CLOUD_SERVICE_TYPES
from spaceone.inventory.model.networking.route.cloud_service import RouteResource, RouteResponse
from spaceone.inventory.model.networking.route.data import Route, ComputeVM

_LOGGER = logging.getLogger(__name__)


class RouteManager(GoogleCloudManager):
    connector_name = 'RouteConnector'
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug('** Route START **')
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
        route_id = ""

        secret_data = params['secret_data']
        project_id = secret_data['project_id']

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        route_conn: RouteConnector = self.locator.get_connector(self.connector_name, **params)

        # Get lists that relate with snapshots through Google Cloud API
        routes = route_conn.list_routes()
        compute_vms = route_conn.list_instance()
        region = 'global'

        for route in routes:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                display = {
                    'network_display': self.get_param_in_url(route.get('network', ''), 'networks'),
                    'next_hop': self._get_next_hop(route),
                    'instance_tags_on_list': self._get_tags_display(route, 'list'),
                    'instance_tags': self._get_tags_display(route, 'not list'),

                }

                route.update({
                    'display': display,
                    'project': secret_data['project_id'],
                    'applicable_instance': self._get_matched_instance(route, secret_data['project_id'], compute_vms),
                })

                ##################################
                # 2. Make Base Data
                ##################################
                # No Labels
                route_data = Route(route, strict=False)
                _name = route_data.get('name', '')
                route_id = route.get('id')

                ##################################
                # 3. Make Return Resource
                ##################################
                route_resource = RouteResource({
                    'name': _name,
                    'account': project_id,
                    'region_code': region,
                    'data': route_data,
                    'reference': ReferenceModel(route_data.reference())
                })

                ##################################
                # 4. Make Collected Region Code
                ##################################
                self.set_region_code(region)

                ##################################
                # 5. Make Resource Response Object
                # List of LoadBalancingResponse Object
                ##################################
                collected_cloud_services.append(RouteResponse({'resource': route_resource}))
            except Exception as e:
                _LOGGER.error(f'[collect_cloud_service] => {e}', exc_info=True)
                error_response = self.generate_resource_error_response(e, 'VPC', 'Route', route_id)
                error_responses.append(error_response)

        _LOGGER.debug(f'** Route Finished {time.time() - start_time} Seconds **')
        return collected_cloud_services, error_responses

    def _get_matched_instance(self, route, project_id, instances_over_region):
        matched_instances = []

        for instance in instances_over_region:
            network_interfaces = instance.get('networkInterfaces', [])
            zone = self.get_param_in_url(instance.get('zone', ''), 'zones')
            region = self.parse_region_from_zone(zone)

            for network_interface in network_interfaces:
                if self._check_instance_is_matched(route, instance):
                    instance_name = instance.get('name')
                    url_subnetwork = instance.get('subnetwork', '')
                    instance = {
                        'id': instance.get('id'),
                        'name': instance_name,
                        'zone': zone,
                        'region': region,
                        'address': network_interface.get('networkIP'),
                        'subnetwork': self.get_param_in_url(url_subnetwork, 'subnetworks'),
                        'project': project_id,
                        'service_accounts': self._get_service_accounts(instance.get('serviceAccounts', [])),
                        'creation_timestamp': instance.get('creationTimestamp'),
                        'labels': self.convert_labels_format(instance.get('labels', {})),
                        'labels_display': self._get_label_display(instance.get('labels', {})),
                        'tags': instance.get('tags', {}).get('items', []),
                    }
                    matched_instances.append(ComputeVM(instance, strict=False))
        return matched_instances

    def _get_next_hop(self, route):
        next_hop = ''
        if 'nextHopInstance' in route:
            url_next_hop_instance = route.get('nextHopInstance', '')
            target = self.get_param_in_url(url_next_hop_instance, 'instances').capitalize()
            zone = self.get_param_in_url(url_next_hop_instance, 'zones').capitalize()
            next_hop = f'Instance {target} (zone  {zone})'

        elif 'nextHopIp' in route:
            # IP address
            target = route.get('nextHopIp', '')
            next_hop = f'IP address lie within {target}'

        elif 'nextHopNetwork' in route:
            url_next_hop_network = route.get('nextHopNetwork', '')
            target = self.get_param_in_url(url_next_hop_network, 'networks')
            next_hop = f'Virtual network {target}'

        elif 'nextHopGateway' in route:
            url_next_hop_gateway = route.get('nextHopGateway')
            target = self.get_param_in_url(url_next_hop_gateway, 'gateways')
            next_hop = f'{target} internet gateway'

        elif 'nextHopIlb' in route:
            # Both ip address and Url string are possible value
            next_hop_ilb = route.get('nextHopIlb', '')
            if self.check_is_ipaddress(next_hop_ilb):
                target = next_hop_ilb
            else:
                target = self.get_param_in_url(next_hop_ilb, 'forwardingRules')
            next_hop = f'Loadbalancer on {target}'

        elif 'nextHopPeering' in route:
            target = route.get('nextHopPeering', '')
            next_hop = f'Peering : {target}'

        return next_hop

    @staticmethod
    def _get_tags_display(route, flag):
        contents = [] if flag == 'list' else ['This route applies to all instances within the specified network']
        return contents if not route.get('tags', []) else route.get('tags', [])

    @staticmethod
    def _get_service_accounts(service_accounts):
        service_accounts_list = []
        for service_account in service_accounts:
            service_accounts_list.append(service_account.get('email'))

        if not service_accounts_list:
            service_accounts_list.append('None')
        return service_accounts_list

    @staticmethod
    def _get_label_display(labels):
        displays = []
        for label in labels:
            value = labels.get(label, '')
            displays.append(f'{label}: {value}')
        return displays

    @staticmethod
    def _check_instance_is_matched(route, instance):
        """
        - instance network is matched to route network(VPC network)
        - instance tags is matched to route tags
        """
        matched = False
        route_network = route.get('network')
        network_interfaces = instance.get('networkInterfaces', [])

        for network_interface in network_interfaces:
            if route_network == network_interface.get('network'):
                if 'tags' in route:
                    if instance.get('tags', {}).get('items', []) in route.get('tags', []):
                        matched = True
                    else:
                        matched = False
                else:
                    matched = True

        return matched
