import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["CloudRunV2Connector"]

_LOGGER = logging.getLogger(__name__)


class CloudRunV2Connector(GoogleCloudConnector):
    google_client_service = "run"
    version = "v2"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_services(self, parent, **query):
        services = []
        query.update({"parent": parent})
        request = self.client.projects().locations().services().list(**query)

        while request is not None:
            try:
                response = request.execute()
                services.extend(response.get("services", []))
                request = (
                    self.client.projects()
                    .locations()
                    .services()
                    .list_next(request, response)
                )
            except Exception as e:
                _LOGGER.warning(f"Failed to list services: {e}")
                break

        return services

    def list_service_revisions(self, parent, **query):
        revisions = []
        query.update({"parent": parent})
        request = (
            self.client.projects().locations().services().revisions().list(**query)
        )

        while request is not None:
            try:
                response = request.execute()
                revisions.extend(response.get("revisions", []))
                request = (
                    self.client.projects()
                    .locations()
                    .services()
                    .revisions()
                    .list_next(request, response)
                )
            except Exception as e:
                _LOGGER.warning(f"Failed to list revisions: {e}")
                break

        return revisions

    def list_jobs(self, parent, **query):
        jobs = []
        query.update({"parent": parent})
        request = self.client.projects().locations().jobs().list(**query)

        while request is not None:
            try:
                response = request.execute()
                jobs.extend(response.get("jobs", []))
                request = (
                    self.client.projects()
                    .locations()
                    .jobs()
                    .list_next(request, response)
                )
            except Exception as e:
                _LOGGER.warning(f"Failed to list jobs: {e}")
                break

        return jobs

    def list_job_executions(self, parent, **query):
        executions = []
        query.update({"parent": parent})
        request = self.client.projects().locations().jobs().executions().list(**query)

        while request is not None:
            try:
                response = request.execute()
                executions.extend(response.get("executions", []))
                request = (
                    self.client.projects()
                    .locations()
                    .jobs()
                    .executions()
                    .list_next(request, response)
                )
            except Exception as e:
                _LOGGER.warning(f"Failed to list executions: {e}")
                break

        return executions

    def list_execution_tasks(self, parent, **query):
        tasks = []
        query.update({"parent": parent})
        request = (
            self.client.projects().locations().jobs().executions().tasks().list(**query)
        )

        while request is not None:
            try:
                response = request.execute()
                tasks.extend(response.get("tasks", []))
                request = (
                    self.client.projects()
                    .locations()
                    .jobs()
                    .executions()
                    .tasks()
                    .list_next(request, response)
                )
            except Exception as e:
                _LOGGER.warning(f"Failed to list tasks: {e}")
                break

        return tasks

    def list_worker_pools(self, parent, **query):
        worker_pools = []
        query.update({"parent": parent})
        request = self.client.projects().locations().workerPools().list(**query)

        while request is not None:
            try:
                response = request.execute()
                worker_pools.extend(response.get("workerPools", []))
                request = (
                    self.client.projects()
                    .locations()
                    .workerPools()
                    .list_next(request, response)
                )
            except Exception as e:
                _LOGGER.warning(f"Failed to list worker pools: {e}")
                break

        return worker_pools

    def list_worker_pool_revisions(self, parent, **query):
        revisions = []
        query.update({"parent": parent})
        request = (
            self.client.projects().locations().workerPools().revisions().list(**query)
        )

        while request is not None:
            try:
                response = request.execute()
                revisions.extend(response.get("revisions", []))
                request = (
                    self.client.projects()
                    .locations()
                    .workerPools()
                    .revisions()
                    .list_next(request, response)
                )
            except Exception as e:
                _LOGGER.warning(f"Failed to list worker pool revisions: {e}")
                break

        return revisions

    def list_operations(self, parent, **query):
        """V2 API에서 operations 조회"""
        operations = []
        query.update({"name": parent})
        try:
            request = self.client.projects().locations().operations().list(**query)
            while request is not None:
                response = request.execute()
                raw_operations = response.get("operations", [])
                operations.extend(raw_operations)
                request = self.client.projects().locations().operations().list_next(
                    request, response
                )
        except Exception as e:
            _LOGGER.warning(f"Failed to list operations: {e}")
            return []
        return operations
