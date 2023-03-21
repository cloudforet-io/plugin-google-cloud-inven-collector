import time
import logging
from typing import Tuple, List

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.connector.compute_engine.vm_instance import VMInstanceConnector
from spaceone.inventory.manager.compute_engine.vm_instance.vm_instance_manager_resource_helper import \
    VMInstanceManagerResourceHelper
from spaceone.inventory.manager.compute_engine.vm_instance import InstanceGroupManagerResourceHelper
from spaceone.inventory.manager.compute_engine.vm_instance.disk_manager_resource_helper import DiskManagerResourceHelper
from spaceone.inventory.manager.compute_engine.vm_instance.firewall_manager_resource_helper import \
    FirewallManagerResourceHelper
from spaceone.inventory.manager.compute_engine.vm_instance.load_balancer_manager_resource_helper import \
    LoadBalancerManagerResourceHelper
from spaceone.inventory.manager.compute_engine.vm_instance.nic_manager_resource_helper import NICManagerResourceHelper
from spaceone.inventory.manager.compute_engine.vm_instance.vpc_manager_resource_helper import VPCManagerResourceHelper
from spaceone.inventory.model.compute_engine.instance.cloud_service import VMInstanceResource, VMInstanceResponse
from spaceone.inventory.model.compute_engine.instance.cloud_service_type import CLOUD_SERVICE_TYPES
from spaceone.inventory.libs.schema.cloud_service import ErrorResourceResponse
from spaceone.inventory.libs.schema.base import ReferenceModel

_LOGGER = logging.getLogger(__name__)


class VMInstanceManager(GoogleCloudManager):
    connector_name = 'VMInstanceConnector'
    cloud_service_types = CLOUD_SERVICE_TYPES
    instance_conn = None

    def collect_cloud_service(self, params) -> Tuple[List[VMInstanceResponse], List[ErrorResourceResponse]]:
        _LOGGER.debug(f'** VM Instance START **')
        '''
        params = {
            'zone_info': {
               'region': 'us-east-1,
               'zone': 'us-east-1a'
            },
            'query': query,
            'secret_data': 'secret_data'
        }
        '''
        resource_responses = []
        error_responses = []
        vm_id = ""

        start_time = time.time()
        secret_data = params.get('secret_data', {})
        project_id = secret_data.get('project_id', '')

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        self.instance_conn: VMInstanceConnector = self.locator.get_connector(self.connector_name, **params)
        all_resources = self.get_all_resources(project_id)
        compute_vms = self.instance_conn.list_instances()

        for compute_vm in compute_vms:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                vm_id = compute_vm.get('id')
                zone, region = self._get_zone_and_region(compute_vm)
                zone_info = {'zone': zone, 'region': region, 'project_id': project_id}

                ##################################
                # 2. Make Base Data
                ##################################
                resource = self.get_vm_instance_resource(project_id, zone_info, compute_vm, all_resources)

                ##################################
                # 4. Make Collected Region Code
                ##################################
                self.set_region_code(resource.get('region_code', ''))

                ##################################
                # 5. Make Resource Response Object
                # List of LoadBalancingResponse Object
                ##################################
                resource_responses.append(VMInstanceResponse({'resource': resource}))

            except Exception as e:
                _LOGGER.error(f'[list_resources] vm_id => {vm_id}, error => {e}', exc_info=True)
                error_response = self.generate_resource_error_response(e, 'ComputeEngine', 'Instance', vm_id)
                error_responses.append(error_response)

        _LOGGER.debug(f'** Compute VMs Finished {time.time() - start_time} Seconds **')
        return resource_responses, error_responses

    # To get all related resources from all regions
    def get_all_resources(self, project_id) -> dict:
        instancegroup_manager_helper: InstanceGroupManagerResourceHelper = InstanceGroupManagerResourceHelper(
            self.instance_conn)

        return {
            'disk': self.instance_conn.list_disks(),
            'autoscaler': self.instance_conn.list_autoscalers(),
            'instance_type': self.instance_conn.list_machine_types(),
            'instance_group': self.instance_conn.list_instance_group_managers(),
            'public_images': self.instance_conn.list_images(project_id),
            'vpcs': self.instance_conn.list_vpcs(),
            'subnets': self.instance_conn.list_subnetworks(),
            'firewalls': self.instance_conn.list_firewall(),
            'forwarding_rules': self.instance_conn.list_forwarding_rules(),
            'target_pools': self.instance_conn.list_target_pools(),
            'url_maps': self.instance_conn.list_url_maps(),
            'backend_svcs': self.instance_conn.list_back_end_services(),
            'managed_instances_in_instance_groups': instancegroup_manager_helper.list_managed_instances_in_instance_groups()
        }

    def get_vm_instance_resource(self, project_id, zone_info, instance, all_resources) -> VMInstanceResource:
        """ Prepare input params for call manager """
        # VPC
        vpcs = all_resources.get('vpcs', [])
        subnets = all_resources.get('subnets', [])

        # All Public Images
        public_images = all_resources.get('public_images', {})

        # URL Maps
        url_maps = all_resources.get('url_maps', [])
        backend_svcs = all_resources.get('backend_svcs', [])
        target_pools = all_resources.get('target_pools', [])

        # Forwarding Rules
        forwarding_rules = all_resources.get('forwarding_rules', [])

        # Firewall
        firewalls = all_resources.get('firewalls', [])

        # Get Instance Groups
        instance_group = all_resources.get('instance_group', [])

        # Get Machine Types
        instance_types = all_resources.get('instance_type', [])

        # Autoscaling group list
        autoscaler = all_resources.get('autoscaler', [])
        instance_in_managed_instance_groups = all_resources.get('managed_instances_in_instance_groups', [])

        # disks
        disks = all_resources.get('disk', [])

        '''Get related resources from managers'''
        vm_instance_manager_helper: VMInstanceManagerResourceHelper = \
            VMInstanceManagerResourceHelper(self.instance_conn)
        auto_scaler_manager_helper: InstanceGroupManagerResourceHelper = \
            InstanceGroupManagerResourceHelper(self.instance_conn)
        loadbalancer_manager_helper: LoadBalancerManagerResourceHelper = LoadBalancerManagerResourceHelper()
        disk_manager_helper: DiskManagerResourceHelper = DiskManagerResourceHelper()
        nic_manager_helper: NICManagerResourceHelper = NICManagerResourceHelper()
        vpc_manager_helper: VPCManagerResourceHelper = VPCManagerResourceHelper()
        firewall_manager_helper: FirewallManagerResourceHelper = FirewallManagerResourceHelper()
        autoscaler_vo = auto_scaler_manager_helper.get_autoscaler_info(instance, instance_group, autoscaler)
        load_balancer_vos = loadbalancer_manager_helper.get_loadbalancer_info(instance, instance_group, backend_svcs,
                                                                              url_maps,
                                                                              target_pools, forwarding_rules)
        disk_vos = disk_manager_helper.get_disk_info(instance, disks)
        vpc_vo, subnet_vo = vpc_manager_helper.get_vpc_info(instance, vpcs, subnets)
        nic_vos = nic_manager_helper.get_nic_info(instance, subnet_vo)
        firewall_vos = firewall_manager_helper.list_firewall_rules_info(instance, firewalls)

        firewall_names = [d.get('name') for d in firewall_vos if d.get('name', '') != '']
        server_data = vm_instance_manager_helper.get_server_info(instance, instance_types, disks, zone_info,
                                                                 public_images, instance_in_managed_instance_groups)
        google_cloud_filters = [{'key': 'resource.labels.instance_id', 'value': instance.get('id')}]
        google_cloud = server_data['data'].get('google_cloud', {})
        _google_cloud = google_cloud.to_primitive()
        labels = _google_cloud.get('labels', [])
        _name = instance.get('name', '')

        ''' Gather all resources information '''
        '''
        server_data.update({
            'nics': nic_vos,
            'disks': disk_vos,
        })
        '''
        server_data['data'].update({
            'nics': nic_vos,
            'disks': disk_vos,
        })
        server_data['data']['compute']['security_groups'] = firewall_names
        server_data['data'].update({
            'load_balancers': load_balancer_vos,
            'security_group': firewall_vos,
            'autoscaler': autoscaler_vo,
            'vpc': vpc_vo,
            'subnet': subnet_vo,
            'google_cloud_monitoring': self.set_google_cloud_monitoring(project_id,
                                                                        "compute.googleapis.com/instance",
                                                                        instance.get('id'),
                                                                        google_cloud_filters),
            'google_cloud_logging': self.set_google_cloud_logging(project_id,
                                                                  'gce_instance',
                                                                  instance.get('id'),
                                                                  google_cloud_filters)
        })
        ##################################
        # 3. Make Return Resource
        ##################################
        server_data.update({
            'name': _name,
            'account': project_id,
            'instance_type': server_data.get('data', {}).get('compute', {}).get('instance_type', ''),
            'instance_size': server_data.get('data', {}).get('hardware', {}).get('core', 0),
            'launched_at': server_data.get('data', {}).get('compute', {}).get('launched_at', ''),
            'tags': labels,
            'reference': ReferenceModel({
                'resource_id': server_data['data']['google_cloud']['self_link'],
                'external_link': f"https://console.cloud.google.com/compute/instancesDetail/zones/{zone_info.get('zone')}/instances/{server_data['name']}?project={server_data['data']['compute']['account']}"
            })
        })
        return VMInstanceResource(server_data, strict=False)

    def _get_zone_and_region(self, instance) -> (str, str):
        url_zone = instance.get('zone', '')
        zone = self.get_param_in_url(url_zone, 'zones')
        region = self.parse_region_from_zone(zone)
        return zone, region
