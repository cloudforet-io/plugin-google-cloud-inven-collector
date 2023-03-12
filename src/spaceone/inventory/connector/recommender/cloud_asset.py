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
        total_assets = []
        query.update({'parent': f'projects/{self.project_id}'})
        request = self.client.assets().list(**query)

        while request is not None:
            response = request.execute()
            for asset in response.get('assets', {}):
                total_assets.append(asset)
            request = self.client.assets().list_next(previous_request=request, previous_response=response)
        return total_assets
