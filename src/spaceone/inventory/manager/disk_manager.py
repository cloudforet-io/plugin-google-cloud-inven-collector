import logging
import time
from datetime import datetime

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.disk.cloud_service import *
from spaceone.inventory.connector.disk import DiskConnector
from spaceone.inventory.model.disk.cloud_service_type import CLOUD_SERVICE_TYPES


_LOGGER = logging.getLogger(__name__)


class DiskManager(GoogleCloudManager):
    connector_name = 'DiskConnector'
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug(f'** Disk START **')
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
        disk_id = ""

        secret_data = params['secret_data']
        project_id = secret_data['project_id']

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        disk_conn: DiskConnector = self.locator.get_connector(self.connector_name, **params)
        disks = disk_conn.list_disks()
        resource_policies = disk_conn.list_resource_policies()

        for disk in disks:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                disk_id = disk.get('id')
                disk_type = self.get_param_in_url(disk.get('type',''), 'diskTypes')
                disk_size = float(disk.get('sizeGb', 0.0))
                zone = self.get_param_in_url(disk.get('zone', ''), 'zones')
                region = self.parse_region_from_zone(zone)
                labels = self.convert_labels_format(disk.get('labels', {}))

                ##################################
                # 2. Make Base Data
                ##################################
                disk.update({
                    'project': secret_data['project_id'],
                    'id': disk_id,
                    'zone': zone,
                    'region': region,
                    'in_used_by': self._get_in_used_by(disk.get('users', [])),
                    'source_image_display': self._get_source_image_display(disk),
                    'disk_type': disk_type,
                    'snapshot_schedule': self._get_matched_snapshot_schedule_detail(region, disk, resource_policies),
                    'snapshot_schedule_display': self._get_snapshot_schedule_name(disk),
                    'encryption': self.get_disk_encryption_type(disk.get('diskEncryptionKey')),
                    'size': float(self._get_bytes(int(disk.get('sizeGb', 0)))),
                    'read_iops': self._get_iops_rate(disk_type, disk_size, 'read'),
                    'write_iops': self._get_iops_rate(disk_type, disk_size, 'write'),
                    'read_throughput': self._get_throughput_rate(disk_type, disk_size),
                    'write_throughput': self._get_throughput_rate(disk_type, disk_size),
                    'labels': labels
                })
                disk_data = Disk(disk, strict=False)

                ##################################
                # 3. Make Return Resource
                ##################################
                disk_resource = DiskResource({
                    'name': disk.get('name', ''),
                    'account': project_id,
                    'region_code': disk.get('region'),
                    'tags': labels,
                    'data': disk_data,
                    'reference': ReferenceModel(disk_data.reference())
                })

                ##################################
                # 4. Make Collected Region Code
                ##################################
                self.set_region_code(disk['region'])

                ##################################
                # 5. Make Resource Response Object
                # List of LoadBalancingResponse Object
                ##################################
                collected_cloud_services.append(DiskResponse({'resource': disk_resource}))
            except Exception as e:
                _LOGGER.error(f'[collect_cloud_service] => {e}', exc_info=True)
                error_response = self.generate_resource_error_response(e, 'ComputeEngine', 'Disk', disk_id)
                error_responses.append(error_response)

        _LOGGER.debug(f'** Disk Finished {time.time() - start_time} Seconds **')
        return collected_cloud_services, error_responses

    def _get_iops_rate(self, disk_type, disk_size, flag):
        const = self._get_iops_constant(disk_type, flag)
        return disk_size * const

    def _get_throughput_rate(self, disk_type, disk_size):
        const = self._get_throughput_constant(disk_type)
        return disk_size * const

    # Get disk snapshot detailed configurations
    def _get_matched_snapshot_schedule_detail(self, region, disk, resource_policies):
        matched_policies = []
        policy_self_links = disk.get('resourcePolicies', [])
        policies = resource_policies.get(region)

        for self_link in policy_self_links:
            for policy in policies:
                if policy.get('selfLink') == self_link:
                    snapshot_schedule_policy = policy.get('snapshotSchedulePolicy', {})
                    snapshot_prop = snapshot_schedule_policy.get('snapshotProperties', {})
                    retention = snapshot_schedule_policy.get('retentionPolicy', {})
                    retention.update({'max_retention_days_display': str(retention.get('maxRetentionDays')) + ' days'})
                    policy_schedule = snapshot_schedule_policy.get('schedule', {})

                    policy.update({
                        'snapshot_schedule_policy': {
                            'schedule_display': self._get_schedule_display(policy_schedule),
                            'schedule': policy_schedule,
                            'retention_policy': retention
                        },
                        'region': self.get_param_in_url(policy.get('region', ''), 'regions'),
                        'labels': self.convert_labels_format(snapshot_prop.get('labels', {})),
                        'tags': self.convert_labels_format(snapshot_prop.get('labels', {})),
                        'storage_locations': snapshot_prop.get('storageLocations', [])
                    })
                    matched_policies.append(policy)

        return matched_policies

    def _get_in_used_by(self, users):
        in_used_by = []
        for user in users:
            used_single = self.get_param_in_url(user, 'instances')
            in_used_by.append(used_single)
        return in_used_by

    def _get_schedule_display(self, schedule):
        schedule_display = []
        if 'weeklySchedule' in schedule:
            week_schedule = schedule.get('weeklySchedule', {})
            weeks = week_schedule.get('dayOfWeeks', [])
            for week in weeks:
                schedule_display.append(week.get('day').title() + self._get_readable_time(week))

        elif 'dailySchedule' in schedule:
            daily = schedule.get('dailySchedule')
            schedule_display.append(f'Every day{self._get_readable_time(daily)}')

        elif 'hourlySchedule' in schedule:
            hourly = schedule.get('hourlySchedule')
            cycle = str(hourly.get('hoursInCycle'))
            hourly_schedule = f'Every {cycle} hours'
            schedule_display.append(hourly_schedule)

        return schedule_display

    @staticmethod
    def _get_readable_time(day_of_weeks):
        start_time = day_of_weeks.get('startTime')
        time_frame = start_time.split(':')
        first = int(time_frame[0]) + 1
        second = int(time_frame[1])

        d = datetime.strptime(start_time, "%H:%M")
        start = d.strftime("%I:%M %p")
        e = datetime.strptime(f'{first}:{second}', "%H:%M")
        end = e.strftime("%I:%M %p")

        return f' between {start} and {end}'

    @staticmethod
    def _get_iops_constant(disk_type, flag):
        constant = 0
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
    def _get_throughput_constant(disk_type):
        constant = 0
        if disk_type == 'pd-standard':
            constant = 0.12
        elif disk_type == 'pd-balanced':
            constant = 0.28
        elif disk_type == 'pd-ssd':
            constant = 0.48

        return constant

    def _get_source_image_display(self, disk):
        source_image_display = ''
        url_source_image = disk.get('sourceImage')
        if url_source_image:
            source_image_display = self.get_param_in_url(url_source_image, 'images')
        return source_image_display

    # Get name of snapshot schedule
    def _get_snapshot_schedule_name(self, disk):
        snapshot_schedule = []
        policies = disk.get('resourcePolicies', [])
        for url_policy in policies:
            str_policy = self.get_param_in_url(url_policy, 'resourcePolicies')
            snapshot_schedule.append(str_policy)

        return snapshot_schedule

    @staticmethod
    def _get_bytes(number):
        return 1024 * 1024 * 1024 * number
