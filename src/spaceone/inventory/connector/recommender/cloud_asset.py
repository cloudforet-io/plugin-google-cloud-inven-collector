import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ['CloudAssetConnector']
_LOGGER = logging.getLogger(__name__)


class CloudAssetConnector(GoogleCloudConnector):
    google_client_service = 'cloudasset'
    version = 'v1'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_assets_in_project(self, **query):
        assets = []
        query.update({'parent': f'projects/{self.project_id}'})
        request = self.client.assets().list(**query)
        print(dir(request))
        while request is not None:
            response = request.execute()
            assets = [asset for asset in response.get('assets', [])]
            request = self.client.projects().assets().list_next(
                previous_request=request, previous_response=response)
        return assets
