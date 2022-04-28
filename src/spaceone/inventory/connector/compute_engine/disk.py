import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ['DiskConnector']
_LOGGER = logging.getLogger(__name__)


class DiskConnector(GoogleCloudConnector):
    google_client_service = 'compute'
    version = 'v1'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_disks(self, **query):
        disk_list = []
        query.update({'project': self.project_id})
        request = self.client.disks().aggregatedList(**query)

        while request is not None:
            response = request.execute()
            for key, _disk in response['items'].items():
                if 'disks' in _disk:
                    disk_list.extend(_disk.get('disks'))
            request = self.client.disks().aggregatedList_next(previous_request=request,
                                                                  previous_response=response)
        return disk_list

    def list_resource_policies(self, **query):
        resource_policy_vo = {}
        query.update({'project': self.project_id})
        request = self.client.resourcePolicies().aggregatedList(**query)
        while request is not None:
            response = request.execute()
            for key, _disk in response['items'].items():
                if 'resourcePolicies' in _disk:
                    _key = key[key.rfind('/')+1:]
                    resource_policy_vo.update({
                        _key: _disk.get('resourcePolicies')
                    })
            request = self.client.resourcePolicies().aggregatedList_next(previous_request=request,
                                                                         previous_response=response)

        return resource_policy_vo
