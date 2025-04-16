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
        try:
            _LOGGER.info(self.secret_data['project_id'])
            name = f"projects/{self.secret_data['project_id']}"
            return self.client.projects().get(name=name).execute()
        except Exception as e:
            _LOGGER.error(f"TTT to get project info: {e}", exc_info=True)
            raise
