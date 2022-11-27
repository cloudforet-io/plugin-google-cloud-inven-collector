import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ['FunctionGen2Connector']
_LOGGER = logging.getLogger(__name__)


class FunctionGen2Connector(GoogleCloudConnector):
    google_client_service = 'cloudfunctions'
    version = 'v2'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_functions(self):
        functions = []
        query = {'parent': self._make_parent()}
        functions_service = self.client.projects().locations().functions()
        request = functions_service.list(**query)

        while request is not None:
            response = request.execute()
            functions = response.get('functions', [])
            request = functions_service.list_next(previous_request=request, previous_response=response)
        return functions

    def _make_parent(self):
        return f'projects/{self.project_id}/locations/-'


