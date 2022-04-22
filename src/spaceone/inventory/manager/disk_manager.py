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

        disk_conn: DiskConnector = self.locator.get_connector(self.connector_name, **params)
        disks = disk_conn.list_disks()
        resource_policies = disk_conn.list_resource_policies()

        for disk in disks:
            try:
                disk_id = disk.get('id')
                disk_type = self._get_last_target(disk.get('type'))
                disk_size = float(disk.get('sizeGb'))
                zone = self._get_last_target(disk.get('zone'))
                region = zone[:-2]
                name = disk.get('name')

                labels = self.convert_labels_format(disk.get('labels', {}))
                disk.update({
                    'project': secret_data['project_id'],
                    'id': disk_id,
                    'zone': zone,
                    'region': region,
                    'in_used_by': self._get_in_used_by(disk.get('users', [])),
                    'source_image_display': self._get_source_image_display(disk),
                    'disk_type': disk_type,
                    'snapshot_schedule': self.get_matched_snapshot(region, disk, resource_policies),
                    'snapshot_schedule_display': self._get_snapshot_schedule(disk),
                    'encryption': self._get_encryption(disk),
                    'size': float(self._get_bytes(int(disk.get('sizeGb')))),
                    'read_iops': self.get_iops_rate(disk_type, disk_size, 'read'),
                    'write_iops': self.get_iops_rate(disk_type, disk_size, 'write'),
                    'read_throughput': self.get_throughput_rate(disk_type, disk_size),
                    'write_throughput': self.get_throughput_rate(disk_type, disk_size),
                    'labels': labels
                })

                disk_data = Disk(disk, strict=False)
                disk_resource = DiskResource({
                    'name': name,
                    'account': project_id,
                    'region_code': disk['region'],
                    'tags': labels,
                    'data': disk_data,
                    'reference': ReferenceModel(disk_data.reference())
                })
                self.set_region_code(disk['region'])
                collected_cloud_services.append(DiskResponse({'resource': disk_resource}))
            except Exception as e:
                _LOGGER.error(f'[collect_cloud_service] => {e}', exc_info=True)
                error_response = self.generate_resource_error_response(e, 'ComputeEngine', 'Disk', disk_id)
                error_responses.append(error_response)

        _LOGGER.debug(f'** Disk Finished {time.time() - start_time} Seconds **')
        return collected_cloud_services, error_responses

    def get_iops_rate(self, disk_type, disk_size, flag):
        const = self._get_iops_constant(disk_type, flag)
        return disk_size * const

    def get_throughput_rate(self, disk_type, disk_size):
        const = self._get_throughput_constant(disk_type)
        return disk_size * const

    def get_matched_snapshot(self, region, disk, resource_policies):
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
                        'region': self._get_last_target(policy.get('region')),
                        'labels': self.convert_labels_format(snapshot_prop.get('labels', {})),
                        'tags': self.convert_labels_format(snapshot_prop.get('labels', {})),
                        'storage_locations': snapshot_prop.get('storageLocations', [])
                    })
                    matched_policies.append(policy)

        return matched_policies

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

    @staticmethod
    def _get_source_image_display(disk):
        source_image_display = ''
        source_image = disk.get('sourceImage')
        if source_image:
            source_image_display = source_image[source_image.rfind('/') + 1:]
        return source_image_display

    @staticmethod
    def _get_snapshot_schedule(disk):
        snapshot_schedule = []
        policies = disk.get('resourcePolicies', [])
        for policy in policies:
            snapshot_schedule.append(policy[policy.rfind('/') + 1:])
        return snapshot_schedule

    '''
    TODO: 
    '''
    @staticmethod
    def _get_in_used_by(users):
        in_used_by = []
        for user in users:
            used_single = user[user.rfind('/') + 1:]
            in_used_by.append(used_single)
        return in_used_by

    @staticmethod
    def _get_bytes(number):
        return 1024 * 1024 * 1024 * number

    @staticmethod
    def _get_encryption(disk):
        encryption = 'Google managed'
        disk_encryption = disk.get('diskEncryptionKey')
        if disk_encryption:
            if 'kmsKeyName' in disk_encryption or 'kmsKeyServiceAccount' in disk_encryption:
                encryption = 'Customer managed'
            else:
                encryption = 'Customer supplied'
        return encryption

    '''
    TODO: 
    '''
    @staticmethod
    def _get_last_target(target):
        # target can be Null
        if target is None:
            return ""
        else:
            return target[target.rfind('/') + 1:]
