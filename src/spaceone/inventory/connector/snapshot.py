import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ['SnapshotConnector']
_LOGGER = logging.getLogger(__name__)


class SnapshotConnector(GoogleCloudConnector):
    google_client_service = 'compute'
    version = 'v1'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_snapshot(self, **query):
        snapshot_list = []
        query = self.generate_query(**query)
        request = self.client.snapshots().list(**query)
        while request is not None:
            response = request.execute()
            for snapshot in response.get('items', []):
                snapshot_list.append(snapshot)
            request = self.client.snapshots().list_next(previous_request=request, previous_response=response)

        return snapshot_list

    def list_resource_policies(self, **query):
        resource_policies = {}
        query = self.generate_query(**query)
        result = self.client.resourcePolicies().aggregatedList(**query).execute()
        all_results = result.get('items', {})
        for region in all_results.keys():
            if 'resourcePolicies' in all_results.get(region):
                for single_policy in all_results.get(region).get('resourcePolicies', []):
                    resource_policies[single_policy.get('selfLink')] = single_policy
        return resource_policies

    def list_all_disks_for_snapshots(self, **query):
        disks = []
        disk_with_schedule = {}
        query = self.generate_query(**query)
        request = self.client.disks().aggregatedList(**query)
        while request is not None:
            response = request.execute()
            for name, disks_scoped_list in response['items'].items():
                if 'disks' in disks_scoped_list:
                    disks.extend(disks_scoped_list.get('disks'))
            request = self.client.disks().aggregatedList_next(previous_request=request,
                                                              previous_response=response)

        for disk in disks:
            if 'resourcePolicies' in disk:
                zone_name_only = self._get_zone(disk.get('zone'))
                disk_name = disk.get('name')
                disk_with_schedule.update({f'{disk_name}-{zone_name_only}': disk.get('resourcePolicies')})

        return disk_with_schedule

    @staticmethod
    def _get_zone(zone: str):
        a = zone
        return a[a.rfind('zones/')+6:]