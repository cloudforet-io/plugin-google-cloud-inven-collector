import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ['FirewallConnector']
_LOGGER = logging.getLogger(__name__)


class FirewallConnector(GoogleCloudConnector):
    google_client_service = 'compute'
    version = 'v1'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_firewall(self, **query):
        firewalls_list = []
        query.update({'project': self.project_id})
        request = self.client.firewalls().list(**query)

        while request is not None:
            response = request.execute()
            for backend_bucket in response.get('items', []):
                firewalls_list.append(backend_bucket)
            request = self.client.firewalls().list_next(previous_request=request, previous_response=response)

        return firewalls_list

    def list_instance_for_networks(self, **query):
        instance_list = []
        query.update({'project': self.project_id,
                      'includeAllScopes': False,
                      'maxResults': 500})

        request = self.client.instances().aggregatedList(**query)
        while request is not None:
            response = request.execute()
            for name, instances_scoped_list in response['items'].items():
                if 'instances' in instances_scoped_list:
                    instance_list.extend(instances_scoped_list.get('instances'))
            request = self.client.instances().aggregatedList_next(previous_request=request, previous_response=response)

        return instance_list