import time
import logging

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.machine_image.data import *
from spaceone.inventory.model.machine_image.cloud_service import *
from spaceone.inventory.connector.machine_image import MachineImageConnector
from spaceone.inventory.model.machine_image.cloud_service_type import CLOUD_SERVICE_TYPES

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
        machine_image_conn: MachineImageConnector = self.locator.get_connector(self.connector_name, **params)

        # Get Instance Templates
        machine_images = machine_image_conn.list_machine_images()
        machine_types = []
        disk_types = []
        public_images = {}

        if machine_images:
            public_images = machine_image_conn.list_public_images()
            for zone in params.get('zones', []):
                if not machine_types:
                    list_machine_types = machine_image_conn.list_machine_types(zone)
                    machine_types.extend(list_machine_types)

                if not disk_types:
                    list_disk_types = machine_image_conn.list_disks(zone)
                    disk_types.extend(list_disk_types)

        for machine_image in machine_images:
            try:
                machine_image_id = machine_image.get('id')
                properties = machine_image.get('sourceInstanceProperties', {})
                tags = properties.get('tags', {})

                boot_image = self.get_boot_image_data(properties, public_images)
                disks = self.get_disks(properties, boot_image)

                region = self.get_matching_region(machine_image.get('storageLocations'))

                machine_image.update({
                    'project': secret_data['project_id'],
                    'deletion_protection': properties.get('deletionProtection', False),
                    'machine': MachineType(self._get_machine_type(properties, machine_types), strict=False),
                    'network_tags': tags.get('items', []),
                    'disk_display': self._get_disk_type_display(disks, 'disk_type'),
                    'image': self._get_disk_type_display(disks, 'source_image_display'),
                    'disks': disks,
                    'scheduling': self._get_scheduling(properties),
                    'network_interfaces': self.get_network_interface(properties, properties.get('canIpForward', False)),
                    'total_storage_bytes': float(machine_image.get('totalStorageBytes', 0.0)),
                    'total_storage_display': self._convert_size(float(machine_image.get('totalStorageBytes', 0.0))),
                    'fingerprint': self._get_properties_item(properties, 'metadata', 'fingerprint'),
                    'location': region.get('location')
                })

                svc_account = properties.get('serviceAccounts', [])
                if len(svc_account) > 0:
                    machine_image.update({'service_account': self._get_service_account(svc_account)})

                _name = machine_image.get('name', '')
                # No Labels
                machine_image_data = MachineImage(machine_image, strict=False)

                machine_image_resource = MachineImageResource({
                    'name': _name,
                    'account': project_id,
                    'data': machine_image_data,
                    'reference': ReferenceModel(machine_image_data.reference()),
                    'region_code': region.get('region_code')
                })
                self.set_region_code(region.get('region_code'))
                collected_cloud_services.append(MachineImageResponse({'resource': machine_image_resource}))
            except Exception as e:
                _LOGGER.error(f'[collect_cloud_service] => {e}', exc_info=True)
                error_response = self.generate_resource_error_response(e, 'ComputeEngine', 'MachineImage', machine_image_id)
                error_responses.append(error_response)

        _LOGGER.debug(f'** Machine Image Finished {time.time() - start_time} Seconds **')
        return collected_cloud_services, error_responses

    def get_disks(self, instance, boot_image):
        disk_info = []

        encryption_dict = instance.get('machineImageEncryptionKey', {})

        # if there's another option for disk encryption
        # encryption_list = instance.get('sourceDiskEncryptionKeys', [])
        for idx, disk in enumerate(instance.get('disks', [])):
            size = self._get_bytes(int(disk.get('diskSizeGb')))
            single_disk = {
                'device_index': disk.get('index'),
                'device': disk.get('deviceName'),
                'device_type': disk.get('type', ''),
                'device_mode': disk.get('mode', ''),
                'size': float(size),
                'tags': self.get_tags_info(disk)
            }
            if idx == 0:
                single_disk.update({'boot_image': boot_image, 'is_boot_image': True})

            if not encryption_dict:
                single_disk.update({'encryption': 'Google managed'})
            elif 'kmsKeyServiceAccount' in encryption_dict:
                single_disk.update({'encryption': 'Customer managed'})
            else:
                single_disk.update({'encryption': 'Customer supplied'})

            disk_info.append(Disk(single_disk, strict=False))

        return disk_info

    def get_tags_info(self, disk):
        disk_size = float(disk.get('diskSizeGb'))
        disk_type = disk.get('diskType')
        return {
            'disk_type': disk_type,
            'auto_delete': disk.get('autoDelete'),
            'read_iops': self.get_iops_rate(disk_type, disk_size, 'read'),
            'write_iops': self.get_iops_rate(disk_type, disk_size, 'write'),
            'read_throughput': self.get_throughput_rate(disk_type, disk_size),
            'write_throughput': self.get_throughput_rate(disk_type, disk_size),
        }

    def get_network_interface(self, instance, can_ip_forward):
        network_interface_info = []
        for idx, network_interface in enumerate(instance.get('networkInterfaces', [])):
            access_configs = network_interface.get('accessConfigs', [])
            alias_ip_ranges = network_interface.get('AliasIPRanges', [])
            network_interface_vo = {'name': network_interface.get('name', ''),
                                    'network': network_interface.get('network', ''),
                                    'network_tier_display': access_configs[0].get('networkTier') if len(
                                        access_configs) > 0 else 'STANDARD',
                                    'subnetwork': network_interface.get('subnetwork', ''),
                                    'network_display': self._get_display_info(
                                        network_interface.get('network', '')),
                                    'subnetwork_display': self._get_display_info(
                                        network_interface.get('subnetwork', '')),
                                    'primary_ip_address': network_interface.get('networkIP', ''),
                                    'public_ip_address': self._get_public_ip(access_configs),
                                    'access_configs': access_configs,
                                    'ip_ranges': [ipr.get('ipCidrRange') for ipr in alias_ip_ranges],
                                    'alias_ip_ranges': alias_ip_ranges,
                                    'kind': network_interface.get('kind', [])}
            if idx == 0:
                ip_forward = 'On' if can_ip_forward else 'Off'
                network_interface_vo.update({'ip_forward': ip_forward})

            network_interface_info.append(network_interface_vo)

        return network_interface_info

    def get_iops_rate(self, disk_type, disk_size, flag):
        const = self._get_iops_constant(disk_type, flag)
        return disk_size * const

    def get_throughput_rate(self, disk_type, disk_size):
        const = self._get_throughput_constant(disk_type)
        return disk_size * const

    def get_boot_image_data(self, instance, public_images):

        disk_info = instance.get("disks", [])
        os_dists = disk_info[0].get('licenses', []) if len(disk_info) > 0 else []
        licenses = disk_info[0].get('licenses', []) if len(disk_info) > 0 else []
        os_type = "LINUX"
        os_identity = ''

        for idx, val in enumerate(os_dists):
            os_items = val.split("/")
            os_identity = os_items[-1].lower()
            if idx == 0:
                if "windows" in os_identity:
                    os_type = "WINDOWS"
                break

        os_data = self.get_appropriate_image_info(os_identity, licenses, public_images)
        os_data.update({
            'os_type': os_type
        })
        return BootImage(os_data, strict=False)

    def get_appropriate_image_info(self, os_identity, licenses, public_images):
        # temp arch lists will be updated when full list has prepared.
        arch_list = ['x86_64', 'x86_32', 'x64', 'x86', 'amd64']
        os_data = {'name': '', 'details': '', 'os_distro': '', 'os_arch': ''}
        for key, images in public_images.items():
            find = False
            if key in os_identity:
                for image in images:
                    image_license = image.get('licenses', [])
                    if self._check_matched(licenses, image_license):
                        os_arch_index = [i for i, e in enumerate(arch_list) if e in image.get('description', '')]
                        os_data.update({'os_distro': 'windows-server' if key == 'windows' else key,
                                        'details': image.get('description', ''),
                                        'name': image.get('name'),
                                        'os_arch': arch_list[os_arch_index[0]] if len(os_arch_index) > 0 else ''})
                        find = True
                        break
            if find:
                break

        return os_data

    def get_matching_region(self, svc_location):
        region_code = svc_location[0] if len(svc_location) > 0 else 'global'
        matched_info = self.match_region_info(region_code)
        return {'region_code': region_code, 'location': 'regional'} if matched_info \
            else {'region_code': 'global', 'location': 'multi'}

    @staticmethod
    def _check_matched(licenses, image):
        check_matched = False
        if len(licenses) > 0 and len(image) > 0:
            check_license = licenses[0][licenses[0].find('/global/'):]
            matching_license = image[0][image[0].find('/global/'):]
            if check_license == matching_license:
                check_matched = True
        return check_matched

    @staticmethod
    def _get_machine_type(instance, machine_types):
        machine = None
        machine_type = instance.get('machineType', '')
        machine_vo = {'machine_type': machine_type}
        disks = instance.get('disks', [])
        source_disk = disks[0] if len(disks) > 0 else {}
        if machine_type != '':
            for item in machine_types:
                if item.get('name') == machine_type:
                    machine = item

        if machine:
            core = machine.get('guestCpus')
            memory = float(machine.get('memoryMb')) * 0.0009765625
            m_str = str(memory)
            display_memory = m_str if m_str[m_str.find('.'):] != '.0' else m_str[:m_str.find('.')]
            machine_vo.update({
                'machine_display': f'{machine_type} : {core} vCPUs {display_memory} GB RAM',
                'machine_detail': machine.get('description'),
                'core': core,
                'memory': memory,

            })
        # source_image_from
        sdn = source_disk.get('source', '')
        machine_vo.update({
            'source_image_from': sdn[sdn.rfind('/')+1:]
        })

        return machine_vo

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
    def _get_properties_item(properties: dict, item_key: str, key: str):
        item = properties.get(item_key)
        selected_prop_item = item.get(key) if item else ''
        return selected_prop_item

    @staticmethod
    def _get_display_info(network):
        network_display = ''
        if network != '':
            network_display = network[network.rfind('/') + 1:]
        return network_display

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
            'automatic_restart': 'On' if scheduling.get('automaticRestart', False) == True else 'Off',
            'preemptibility': 'On' if scheduling.get('preemptible', False) == True else 'Off',
        }

    @staticmethod
    def _get_public_ip(access_configs):
        public_ip = ''
        if access_configs:
            public_ip = access_configs[0].get('natIP')
        return public_ip
