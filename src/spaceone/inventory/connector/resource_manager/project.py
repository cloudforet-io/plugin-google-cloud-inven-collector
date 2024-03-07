import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["ProjectConnector"]
_LOGGER = logging.getLogger(__name__)


class ProjectConnector(GoogleCloudConnector):
    google_client_service = "cloudresourcemanager"
    version = "v3"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.secret_data = kwargs.get("secret_data", {})

    def get_project_info(self):
        name = f"projects/{self.secret_data['project_id']}"
        return self.client.projects().get(name=name).execute()
