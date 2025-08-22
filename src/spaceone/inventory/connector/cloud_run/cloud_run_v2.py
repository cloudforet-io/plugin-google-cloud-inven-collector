import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["CloudRunV2Connector"]

_LOGGER = logging.getLogger(__name__)


class CloudRunV2Connector(GoogleCloudConnector):
    google_client_service = "run"
    version = "v2"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_services(self, parent: str) -> list:
        try:
            request = self.client.projects().locations().services().list(parent=parent)
            response = request.execute()
            return response.get('services', [])
        except Exception as e:
            _LOGGER.error(f"Failed to list Cloud Run services: {str(e)}")
            return []

    def list_revisions(self, parent: str) -> list:
        try:
            request = self.client.projects().locations().services().revisions().list(parent=parent)
            response = request.execute()
            return response.get('revisions', [])
        except Exception as e:
            _LOGGER.error(f"Failed to list Cloud Run revisions: {str(e)}")
            return []

    def list_jobs(self, parent: str) -> list:
        try:
            request = self.client.projects().locations().jobs().list(parent=parent)
            response = request.execute()
            return response.get('jobs', [])
        except Exception as e:
            _LOGGER.error(f"Failed to list Cloud Run jobs: {str(e)}")
            return []

    def list_executions(self, parent: str) -> list:
        try:
            request = self.client.projects().locations().jobs().executions().list(parent=parent)
            response = request.execute()
            return response.get('executions', [])
        except Exception as e:
            _LOGGER.error(f"Failed to list Cloud Run executions: {str(e)}")
            return []

    def list_tasks(self, parent: str) -> list:
        try:
            request = self.client.projects().locations().jobs().executions().tasks().list(parent=parent)
            response = request.execute()
            return response.get('tasks', [])
        except Exception as e:
            _LOGGER.error(f"Failed to list Cloud Run tasks: {str(e)}")
            return []

    def list_worker_pools(self, parent: str) -> list:
        try:
            request = self.client.projects().locations().workerPools().list(parent=parent)
            response = request.execute()
            return response.get('workerPools', [])
        except Exception as e:
            _LOGGER.error(f"Failed to list Cloud Run worker pools: {str(e)}")
            return []

    def list_worker_pool_revisions(self, parent: str) -> list:
        try:
            request = self.client.projects().locations().workerPools().revisions().list(parent=parent)
            response = request.execute()
            return response.get('revisions', [])
        except Exception as e:
            _LOGGER.error(f"Failed to list Cloud Run worker pool revisions: {str(e)}")
            return []
