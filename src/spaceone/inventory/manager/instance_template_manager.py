import time
import logging

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.instance_template.data import *
from spaceone.inventory.model.instance_template.cloud_service import *
from spaceone.inventory.connector.instance_template import InstanceTemplateConnector
from spaceone.inventory.model.instance_template.cloud_service_type import CLOUD_SERVICE_TYPES

_LOGGER = logging.getLogger(__name__)


class InstanceTemplateManager(GoogleCloudManager):
    connector_name = 'InstanceTemplateConnector'
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug(f'** Instance Template START **')
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
        inst_template_id = ""

        secret_data = params['secret_data']
        project_id = secret_data['project_id']

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        instance_template_conn: InstanceTemplateConnector = self.locator.get_connector(self.connector_name, **params)
        # Get Instance Templates
        instance_templates = instance_template_conn.list_instance_templates()
        instance_groups = instance_template_conn.list_instance_group_managers()

        for inst_template in instance_templates:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                inst_template_id = inst_template.get('id')
                properties = inst_template.get('properties', {})
                tags = properties.get('tags', {})

                in_used_by, matched_instance_group = self._match_instance_group(inst_template, instance_groups)
                disks = self._get_disks(properties)
                labels = self.convert_labels_format(properties.get('labels', {}))



                inst_template.update({
                    'project': secret_data['project_id'],
                    'in_used_by': in_used_by,
                    'ip_forward': properties.get('canIpForward', False),
                    'machine_type': properties.get('machineType', ''),
                    'network_tags': tags.get('items', []),
                    'scheduling': self._get_scheduling(properties),
                    'disk_display': self._get_disk_type_display(disks, 'disk_type'),
                    'image': self._get_disk_type_display(disks, 'source_image_display'),
                    'instance_groups': matched_instance_group,
                    'network_interfaces': self._get_network_interface(properties),
                    'fingerprint': self._get_properties_item(properties, 'metadata', 'fingerprint'),
                    'labels': labels,
                    'disks': disks
                })

                svc_account = properties.get('serviceAccounts', [])
                if len(svc_account) > 0:
                    inst_template.update({'service_account': self._get_service_account(svc_account)})
                _name = inst_template.get('name', '')


                ##################################
                # 2. Make Base Data
                ##################################
                instance_template_data = InstanceTemplate(inst_template, strict=False)
                # labels -> tags
                default_region = 'global'

                ##################################
                # 3. Make Return Resource
                ##################################
                instance_template_resource = InstanceTemplateResource({
                    'name': _name,
                    'account': project_id,
                    'tags': labels,
                    'data': instance_template_data,
                    'reference': ReferenceModel(instance_template_data.reference()),
                    'region_code': default_region
                })

                ##################################
                # 4. Make Collected Region Code
                ##################################
                self.set_region_code(default_region)

                ##################################
                # 5. Make Resource Response Object
                # List of LoadBalancingResponse Object
                ##################################
                collected_cloud_services.append(InstanceTemplateResponse({'resource': instance_template_resource}))
            except Exception as e:
                _LOGGER.error(f'[collect_cloud_service] => {e}', exc_info=True)
                error_response = self.generate_resource_error_response(e, 'ComputeEngine', 'InstanceTemplate', inst_template_id)
                error_responses.append(error_response)

        _LOGGER.debug(f'** Instance Template Finished {time.time() - start_time} Seconds **')
        return collected_cloud_services, error_responses

    # Returns matched instance group and user(instance) related to instance template.
    def _match_instance_group(self, instance_template, instance_group_managers: list):
        in_used_by = []
        instance_group_infos = []
        for instance_group in instance_group_managers:
            template_self_link_source = instance_template.get('selfLink', '')
            template_self_link_target = instance_group.get('instanceTemplate', '')
            if template_self_link_source != '' and template_self_link_target != '' and \
                    template_self_link_source == template_self_link_target:
                in_used_by.append(instance_group.get('name', ''))
                instance_group_infos.append(InstanceGroup(instance_group, strict=False))

        return in_used_by, instance_group_infos

    def _get_disks(self, instance):
        disk_info = []
        for disk in instance.get('disks', []):
            init_param = disk.get('initializeParams', {})
            '''
            # initializeParams: {diskSizeGb: ""} can be Null
            if init_param.get('diskSizeGb') is not None:
                size = self._get_bytes(int(init_param.get('diskSizeGb')))
            else:
                size = 0
            '''
            disk_info.append(Disk({
                'device_index': disk.get('index'),
                'device': disk.get('deviceName'),
                'device_type': disk.get('type', ''),
                'device_mode': disk.get('mode', ''),
                'size': self._get_disk_size(init_param),
                'tags': self._get_tags_info(disk)
            }, strict=False))
        return disk_info

    def _get_tags_info(self, disk):
        init_param = disk.get('initializeParams', {})
        disk_size = self._get_disk_size(init_param)
        disk_type = init_param.get('diskType')
        sc_image = init_param.get('sourceImage', '')
        return {
            'disk_type': init_param.get('diskType'),
            'source_image': sc_image,
            'source_image_display': self.get_param_in_url(sc_image, 'images'),
            'auto_delete': disk.get('autoDelete'),
            'read_iops': self._get_iops_rate(disk_type, disk_size, 'read'),
            'write_iops': self._get_iops_rate(disk_type, disk_size, 'write'),
            'read_throughput': self._get_throughput_rate(disk_type, disk_size),
            'write_throughput': self._get_throughput_rate(disk_type, disk_size),
        }

    def _get_network_interface(self, instance):
        network_interface_info = []
        for network_interface in instance.get('networkInterfaces', []):
            configs, tiers = self._get_access_configs_type_and_tier(network_interface.get('accessConfigs', []))
            network_interface_info.append({
                'idx_name': network_interface.get('name', ''),
                'network': network_interface.get('network', ''),
                'network_display': self.get_param_in_url(network_interface.get('network', ''), 'networks'),
                'configs': configs,
                'network_tier': tiers,
                'access_configs': network_interface.get('accessConfigs', []),
                'kind': network_interface.get('kind', [])
            })

        return network_interface_info

    def _get_iops_rate(self, disk_type, disk_size, flag):
        const = self._get_iops_constant(disk_type, flag)
        return disk_size * const

    def _get_throughput_rate(self, disk_type, disk_size):
        const = self._get_throughput_constant(disk_type)
        return disk_size * const

    def _get_disk_size(self, init_param) -> float:
        # initializeParams: {diskSizeGb: ""} can be Null
        if init_param.get('diskSizeGb') is not None:
            disk_size = self._get_bytes(int(init_param.get('diskSizeGb')))
        else:
            disk_size = 0
        return disk_size

    @staticmethod
    def _get_access_configs_type_and_tier(access_configs):
        configs = []
        tiers = []
        for access_config in access_configs:
            ac_name = access_config.get('name', '')
            ac_type = access_config.get('type', '')
            configs.append(f' {ac_name} : {ac_type}')
            tiers.append(access_config.get('networkTier', ''))
        return configs, tiers

    @staticmethod
    def _get_service_account(svc_account):
        service_account = svc_account[0]
        return {
            'email': service_account.get('email', ''),
            'scopes': service_account.get('scopes', [])
        }

    @staticmethod
    def _get_iops_constant(disk_type, flag):
        constant = 0.0
        if flag == 'read':
            if disk_type == 'pd-standard':
                constant = 0.75
            elif disk_type == 'pd-balanced':
                constant = 6.0
            elif disk_type == 'pd-ssd':
                constant = 30.0
        else:
            if disk_type == 'pd-standard':
                constant = 1.5
            elif disk_type == 'pd-balanced':
                constant = 6.0
            elif disk_type == 'pd-ssd':
                constant = 30.0
        return constant

    @staticmethod
    def _get_disk_type_display(disk, key):
        if len(disk) > 0:
            tag = disk[0].get('tags', {})
            disk_type = tag.get(key, '')
            return disk_type
        else:
            return ''

    @staticmethod
    def _get_bytes(number):
        return 1024 * 1024 * 1024 * number

    @staticmethod
    def _get_properties_item(properties: dict, item_key: str, key: str):
        item = properties.get(item_key)
        selected_prop_item = item.get(key) if item else ''
        return selected_prop_item

    @staticmethod
    def _get_scheduling(properties):
        scheduling = properties.get('scheduling', {})
        return {
            'on_host_maintenance': scheduling.get('onHostMaintenance', 'MIGRATE'),
            'automatic_restart': 'On' if scheduling.get('automaticRestart', False) == True else 'Off',
            'preemptibility': 'On' if scheduling.get('preemptible', False) == True else 'Off',
        }

    @staticmethod
    def _get_throughput_constant(disk_type):
        constant = 0.0
        if disk_type == 'pd-standard':
            constant = 0.12
        elif disk_type == 'pd-balanced':
            constant = 0.28
        elif disk_type == 'pd-ssd':
            constant = 0.48

        return constant
