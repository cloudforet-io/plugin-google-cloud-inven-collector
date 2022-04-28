import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ['RouteConnector']
_LOGGER = logging.getLogger(__name__)


class RouteConnector(GoogleCloudConnector):
    google_client_service = 'compute'
    version = 'v1'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_routes(self, **query):
        route_list = []
        query.update({'project': self.project_id})
        request = self.client.routes().list(**query)
        while request is not None:
            response = request.execute()
            for template in response.get('items', []):
                route_list.append(template)
            request = self.client.routes().list_next(previous_request=request,
                                                     previous_response=response)

        return route_list

    def list_instance(self, **query):
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
            request = self.client.instances().aggregatedList_next(previous_request=request,
                                                                  previous_response=response)

        return instance_list
