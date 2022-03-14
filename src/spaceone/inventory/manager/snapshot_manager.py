import time
import logging
import re
from datetime import datetime

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.snapshot.cloud_service import SnapShotSchedule, Snapshot, SnapshotResource, SnapshotResponse
from spaceone.inventory.connector.snapshot import SnapshotConnector
from spaceone.inventory.model.snapshot.cloud_service_type import CLOUD_SERVICE_TYPES

_LOGGER = logging.getLogger(__name__)


class SnapshotManager(GoogleCloudManager):
    connector_name = 'SnapshotConnector'
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug(f'** Snapshot START **')
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
        snapshot_id = ""

        secret_data = params['secret_data']
        project_id = secret_data['project_id']
        snapshot_conn: SnapshotConnector = self.locator.get_connector(self.connector_name, **params)

        # Get lists that relate with snapshots through Google Cloud API
        snapshots = snapshot_conn.list_snapshot()
        all_region_resource_policies = snapshot_conn.list_resource_policies()
        disk_list_info = snapshot_conn.list_all_disks_for_snapshots()

        for snapshot in snapshots:
            try:
                snapshot_id = snapshot.get('id')
                region = self.get_matching_region(snapshot.get('storageLocations'))
                snapshot_schedule = []
                snapshot_schedule_display = []
                disk_name_key = self._get_disk_name_key(snapshot.get('name'))

                for resource_policy in disk_list_info.get(disk_name_key, []):
                    snapshot_schedule_display.append(self._get_last_target(resource_policy))
                    matched_po = self.get_matched_snapshot_schedule(all_region_resource_policies.get(resource_policy))
                    snapshot_schedule.append(SnapShotSchedule(matched_po, strict=False))
                labels = self.convert_labels_format(snapshot.get('labels', {}))
                snapshot.update({
                    'project': secret_data['project_id'],
                    'disk': self.get_disk_info(snapshot),
                    'snapshot_schedule': snapshot_schedule,
                    'snapshot_schedule_display': snapshot_schedule_display,
                    'creation_type': 'Scheduled' if snapshot.get('autoCreated') else 'Manual',
                    'encryption': self._get_encryption_info(snapshot),
                    'labels': labels
                })
                snapshot_data = Snapshot(snapshot, strict=False)
                _name = snapshot_data.get('name', '')
                # labels -> tags
                snapshots_resource = SnapshotResource({
                    'name': _name,
                    'account': project_id,
                    'region_code': region.get('region_code'),
                    'data': snapshot_data,
                    'tags': labels,
                    'reference': ReferenceModel(snapshot_data.reference())
                })

                self.set_region_code(region.get('region_code'))
                collected_cloud_services.append(SnapshotResponse({'resource': snapshots_resource}))
            except Exception as e:
                _LOGGER.error(f'[collect_cloud_service] => {e}', exc_info=True)
                error_response = self.generate_resource_error_response(e, 'ComputeEngine', 'Snapshot', snapshot_id)
                error_responses.append(error_response)

        _LOGGER.debug(f'** SnapShot Finished {time.time() - start_time} Seconds **')
        return collected_cloud_services, error_responses

    def get_matching_region(self, svc_location):
        region_code = svc_location[0] if len(svc_location) > 0 else 'global'
        matched_info = self.match_region_info(region_code)
        return {'region_code': region_code, 'location': 'regional'} if matched_info \
            else {'region_code': 'global', 'location': 'multi'}

    def get_disk_info(self, snapshot):
        '''
            source_disk = StringType()
            source_disk_display = StringType()
            source_disk_id = StringType()
            diskSizeGb = IntType()
            disk_size_display = StringType()
            storage_bytes = IntType()
            storage_bytes_display = StringType()
        '''
        disk_gb = snapshot.get('diskSizeGb', 0.0)
        st_byte = snapshot.get('storageBytes', 0)
        size = self._get_bytes(int(disk_gb))
        return {
            'source_disk': snapshot.get('sourceDisk', ''),
            'source_disk_display': self._get_display_name(snapshot.get('sourceDisk', ''), 'disks/', 6),
            'source_disk_id': snapshot.get('sourceDiskId', ''),
            'disk_size': float(size),
            'storage_bytes': int(st_byte)
        }

    def get_matched_snapshot_schedule(self, policy):
        schedule_policy = policy.get('snapshotSchedulePolicy', {})
        snapshot_prop = schedule_policy.get('snapshotProperties', {})
        retention = schedule_policy.get('retentionPolicy', {})
        retention.update({'max_retention_days_display': str(retention.get('maxRetentionDays')) + ' days'})
        policy_schedule = schedule_policy.get('schedule', {})

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

        return policy

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
    def _get_display_name(source: str, search_word_str: str, index_num: int):
        a = source
        return a[a.find(search_word_str) + index_num:]

    @staticmethod
    def _get_encryption_info(snapshot):
        encryption = 'Google managed'
        encryption_key = snapshot.get('snapshotEncryptionKey')

        if encryption_key:
            if 'kmsKeyName' in encryption_key or 'kmsKeyServiceAccount' in encryption_key:
                encryption = 'Customer managed'
            elif 'rawKey' in encryption_key or 'sha256' in encryption_key:
                encryption = 'Customer supplied'

        return encryption

    @staticmethod
    def _get_last_target(target_str):
        return target_str[target_str.rfind('/') + 1:]

    @staticmethod
    def _get_bytes(number):
        return 1024 * 1024 * 1024 * number

    @staticmethod
    def _get_disk_name_key(snapshot_name):
        disk_key = None
        pattern = r'-[0-9]{14}-'
        matched_str = re.findall(pattern, snapshot_name)
        key = matched_str[0] if len(matched_str) > 0 else None
        if key:
            disk_key = snapshot_name[:snapshot_name.find(key)]
        return disk_key