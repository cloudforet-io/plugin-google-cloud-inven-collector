import time
import logging

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.connector.compute_engine.machine_image import MachineImageConnector
from spaceone.inventory.model.compute_engine.machine_image.cloud_service_type import CLOUD_SERVICE_TYPES
from spaceone.inventory.model.compute_engine.machine_image.cloud_service import MachineImageResource, \
    MachineImageResponse
from spaceone.inventory.model.compute_engine.machine_image.data import MachineType, MachineImage, Disk

_LOGGER = logging.getLogger(__name__)


class MachineImageManager(GoogleCloudManager):
    connector_name = 'MachineImageConnector'
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug(f'** Machine Image START **')
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
        machine_image_id = ""

        secret_data = params['secret_data']
        project_id = secret_data['project_id']

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        machine_image_conn: MachineImageConnector = self.locator.get_connector(self.connector_name, **params)

        # Get machine image
        machine_images = machine_image_conn.list_machine_images()
        disk_types = []

        if machine_images:
            for zone in params.get('zones', []):
                list_disk_types = machine_image_conn.list_disks(zone)
                disk_types.extend(list_disk_types)

        for machine_image in machine_images:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                _name = machine_image.get('name', '')
                machine_image_id = machine_image.get('id')
                properties = machine_image.get('instanceProperties', {})
                tags = properties.get('tags', {})
                boot_image = self.get_boot_image_data(properties)
                disks = self.get_disks(properties, boot_image)
                region = self.get_matching_region(machine_image.get('storageLocations'))

                ##################################
                # 2. Make Base Data
                ##################################
                machine_image.update({
                    'project': secret_data['project_id'],
                    'deletion_protection': properties.get('deletionProtection', False),
                    'machine_type': MachineType(self.get_machine_type(properties), strict=False),
                    'network_tags': tags.get('items', []),
                    'disk_display': self._get_disk_type_display(disks, 'disk_type'),
                    'image': self._get_disk_type_display(disks, 'source_image_display'),
                    'disks': disks,
                    'scheduling': self._get_scheduling(properties),
                    'network_interfaces': self.get_network_interface(properties),
                    'total_storage_bytes': float(machine_image.get('totalStorageBytes', 0.0)),
                    'total_storage_display': self._convert_size(float(machine_image.get('totalStorageBytes', 0.0))),
                    'fingerprint': properties.get('metadata', {}).get('fingerprint', ''),
                    'location': properties.get('storageLocations', [])
                })

                svc_account = properties.get('serviceAccounts', [])
                if len(svc_account) > 0:
                    machine_image.update({'service_account': self._get_service_account(svc_account)})

                # No Labels
                machine_image_data = MachineImage(machine_image, strict=False)
                ##################################
                # 3. Make Return Resource
                ##################################
                machine_image_resource = MachineImageResource({
                    'name': _name,
                    'account': project_id,
                    'data': machine_image_data,
                    'reference': ReferenceModel(machine_image_data.reference()),
                    'region_code': region.get('region_code')
                })

                ##################################
                # 4. Make Collected Region Code
                ##################################
                self.set_region_code(region.get('region_code'))

                ##################################
                # 5. Make Resource Response Object
                # List of LoadBalancingResponse Object
                ##################################
                collected_cloud_services.append(MachineImageResponse({'resource': machine_image_resource}))
            except Exception as e:
                _LOGGER.error(f'[collect_cloud_service] => {e}', exc_info=True)
                error_response = self.generate_resource_error_response(e, 'ComputeEngine', 'MachineImage',
                                                                       machine_image_id)
                error_responses.append(error_response)

        _LOGGER.debug(f'** Machine Image Finished {time.time() - start_time} Seconds **')
        return collected_cloud_services, error_responses

    def get_disks(self, instance, boot_image):
        disk_info = []
        # if there's another option for disk encryption
        # encryption_list = instance.get('sourceDiskEncryptionKeys', [])
        for disk in instance.get('disks', []):
            size = self._get_bytes(int(disk.get('diskSizeGb', 0)))
            single_disk = {
                'device_index': disk.get('index'),
                'device': disk.get('deviceName'),
                'device_type': disk.get('type', ''),
                'device_mode': disk.get('mode', ''),
                'size': float(size),
                'tags': self.get_tags_info(disk)
            }
            if disk.get('boot', False):
                single_disk.update({'boot_image': boot_image, 'is_boot_image': True})

            # Check image is encrypted
            if 'machineImageEncryptionKey' in instance:
                single_disk.update({'encryption': 'Google managed'})
            elif 'kmsKeyServiceAccount' in instance:
                single_disk.update({'encryption': 'Customer managed'})
            else:
                single_disk.update({'encryption': 'Customer supplied'})

            disk_info.append(Disk(single_disk, strict=False))

        return disk_info

    def get_tags_info(self, disk):
        disk_size = float(disk.get('diskSizeGb', 0.0))
        disk_type = disk.get('diskType')
        return {
            'disk_type': disk_type,
            'auto_delete': disk.get('autoDelete'),
            'read_iops': self.get_iops_rate(disk_type, disk_size, 'read'),
            'write_iops': self.get_iops_rate(disk_type, disk_size, 'write'),
            'read_throughput': self.get_throughput_rate(disk_type, disk_size),
            'write_throughput': self.get_throughput_rate(disk_type, disk_size),
        }

    def get_network_interface(self, instance):
        network_interface_info = []
        for idx, network_interface in enumerate(instance.get('networkInterfaces', [])):
            access_configs = network_interface.get('accessConfigs', [])
            alias_ip_ranges = network_interface.get('AliasIPRanges', [])
            network_interface_vo = {
                'name': network_interface.get('name', ''),
                'network': network_interface.get('network', ''),
                'network_tier_display': access_configs[0].get('networkTier') if len(access_configs) > 0 else 'STANDARD',
                'subnetwork': network_interface.get('subnetwork', ''),
                'network_display': self.get_param_in_url(network_interface.get('network', ''), 'networks'),
                'subnetwork_display': self.get_param_in_url(network_interface.get('subnetwork', ''), 'subnetworks'),
                'primary_ip_address': network_interface.get('networkIP', ''),
                'public_ip_address': self._get_public_ip(access_configs),
                'access_configs': access_configs,
                'ip_ranges': self._get_alias_ip_range(alias_ip_ranges),
                'alias_ip_ranges': alias_ip_ranges,
                'kind': network_interface.get('kind', '')}
            if idx == 0:
                ip_forward = 'On' if instance.get('canIpForward', '') else 'Off'
                network_interface_vo.update({'ip_forward': ip_forward})

            network_interface_info.append(network_interface_vo)

        return network_interface_info

    def get_iops_rate(self, disk_type, disk_size, flag):
        const = self._get_iops_constant(disk_type, flag)
        return disk_size * const

    def get_throughput_rate(self, disk_type, disk_size):
        const = self._get_throughput_constant(disk_type)
        return disk_size * const

    def get_boot_image_data(self, instance):
        list_disk_info = instance.get("disks", [])
        bootdisk_info = self.get_boot_disk(list_disk_info)
        return bootdisk_info.get('deviceName', '')

    def get_matching_region(self, storage_location):
        region_code = storage_location[0] if len(storage_location) > 0 else 'global'
        matched_info = self.match_region_info(region_code)
        return {'region_code': region_code, 'location': 'regional'} if matched_info \
            else {'region_code': 'global', 'location': 'multi'}

    # Returns first boot disk of instance
    @staticmethod
    def get_boot_disk(list_disk_info) -> dict:
        for disk_info in list_disk_info:
            if disk_info.get('boot', False):
                return disk_info
        return {}

    def get_machine_type(self, instance):
        machine_vo = {
            'machine_type': instance.get('machineType', '')
        }
        disks = instance.get('disks', [])
        source_disk = disks[0] if len(disks) > 0 else {}
        url_source = source_disk.get('source', '')
        machine_vo.update({
            'source_image_from': self.get_param_in_url(url_source, 'disks')
        })

        return machine_vo

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
    def _get_throughput_constant(disk_type):
        constant = 0.0
        if disk_type == 'pd-standard':
            constant = 0.12
        elif disk_type == 'pd-balanced':
            constant = 0.28
        elif disk_type == 'pd-ssd':
            constant = 0.48

        return constant

    @staticmethod
    def _get_bytes(number):
        return 1024 * 1024 * 1024 * number

    @staticmethod
    def _get_scheduling(properties):
        scheduling = properties.get('scheduling', {})
        return {
            'on_host_maintenance': scheduling.get('onHostMaintenance', 'MIGRATE'),
            'automatic_restart': 'On' if scheduling.get('automaticRestart', False) else 'Off',
            'preemptibility': 'On' if scheduling.get('preemptible', False) else 'Off',
        }

    @staticmethod
    def _get_public_ip(access_configs):
        public_ip = ''
        if access_configs:
            public_ip = access_configs[0].get('natIP')
        return public_ip

    @staticmethod
    def _get_alias_ip_range(alias_ip_ranges):
        ip_range = []
        for ip in alias_ip_ranges:
            ip_range.append(ip.get('ipCidrRange', ''))
        return ip_range
