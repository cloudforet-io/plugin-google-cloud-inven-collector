import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ['EventarcConnector']
_LOGGER = logging.getLogger(__name__)


class EventarcConnector(GoogleCloudConnector):
    google_client_service = 'eventarc'
    version = 'v1'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_providers(self):
        providers = []
        query = {'parent': self._make_parent()}
        eventarc_provider_service = self.client.projects().locations().providers()
        request = eventarc_provider_service.list(**query)

        while request is not None:
            response = request.execute()
            providers = response.get('providers', [])
            request = eventarc_provider_service.list_next(previous_request=request, previous_response=response)
        return providers

    def _make_parent(self):
        return f'projects/{self.project_id}/locations/-'
