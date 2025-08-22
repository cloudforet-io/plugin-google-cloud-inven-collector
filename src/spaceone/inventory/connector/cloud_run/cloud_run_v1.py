import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["CloudRunV1Connector"]

_LOGGER = logging.getLogger(__name__)


class CloudRunV1Connector(GoogleCloudConnector):
    google_client_service = "run"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_locations(self) -> list:
        try:
            request = self.client.projects().locations().list(name=f"projects/{self.project_id}")
            response = request.execute()
            return response.get('locations', [])
        except Exception as e:
            _LOGGER.error(f"Failed to list locations from Cloud Run API: {str(e)}")
            return []

    def list_domain_mappings(self, parent: str) -> list:
        try:
            request = self.client.namespaces().domainmappings().list(parent=parent)
            response = request.execute()
            return response.get('items', [])
        except Exception as e:
            _LOGGER.error(f"Failed to list Cloud Run v1 domain mappings: {str(e)}")
            return []
