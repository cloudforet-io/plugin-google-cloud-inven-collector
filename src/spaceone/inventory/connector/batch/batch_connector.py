import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["BatchConnector"]

_LOGGER = logging.getLogger(__name__)


class BatchConnector(GoogleCloudConnector):
    """통합 Batch Connector - Locations, Jobs, Tasks API를 모두 처리"""

    google_client_service = "batch"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # ===== Locations API =====
    def list_locations(self, **query):
        """
        Batch 서비스가 지원되는 Location 목록을 조회합니다.

        Args:
            **query: 추가 쿼리 파라미터

        Returns:
            list: Location 목록
        """
        locations = []
        parent = f"projects/{self.project_id}"
        query.update({"name": parent})

        try:
            request = self.client.projects().locations().list(**query)
            while request is not None:
                response = request.execute()
                for location in response.get("locations", []):
                    locations.append(location)
                request = (
                    self.client.projects()
                    .locations()
                    .list_next(previous_request=request, previous_response=response)
                )
        except Exception as e:
            _LOGGER.warning(f"Failed to list locations: {e}")

        return locations

    def get_location(self, name, **query):
        """
        특정 Location의 상세 정보를 조회합니다.

        Args:
            name (str): Location의 전체 경로
            **query: 추가 쿼리 파라미터

        Returns:
            dict: Location 정보
        """
        query.update({"name": name})

        try:
            return self.client.projects().locations().get(**query).execute()
        except Exception as e:
            _LOGGER.warning(f"Failed to get location {name}: {e}")
            return {}

    # ===== Jobs API =====
    def list_all_jobs(self, **query):
        """
        모든 Location의 Job 목록을 글로벌로 조회합니다.
        locations/- 패턴을 사용하여 한번에 모든 location의 jobs를 가져옵니다.

        Args:
            **query: 추가 쿼리 파라미터

        Returns:
            list: 모든 Job 목록
        """
        jobs = []
        parent = f"projects/{self.project_id}/locations/-"
        query.update({"parent": parent})

        try:
            request = self.client.projects().locations().jobs().list(**query)
            while request is not None:
                response = request.execute()
                for job in response.get("jobs", []):
                    jobs.append(job)
                request = (
                    self.client.projects()
                    .locations()
                    .jobs()
                    .list_next(previous_request=request, previous_response=response)
                )
        except Exception as e:
            _LOGGER.warning(f"Failed to list all jobs: {e}")

        return jobs

    def list_jobs(self, location_id, **query):
        """
        특정 Location의 Job 목록을 조회합니다.

        Args:
            location_id (str): Location ID
            **query: 추가 쿼리 파라미터

        Returns:
            list: Job 목록
        """
        jobs = []
        parent = f"projects/{self.project_id}/locations/{location_id}"
        query.update({"parent": parent})

        try:
            request = self.client.projects().locations().jobs().list(**query)
            while request is not None:
                response = request.execute()
                for job in response.get("jobs", []):
                    jobs.append(job)
                request = (
                    self.client.projects()
                    .locations()
                    .jobs()
                    .list_next(previous_request=request, previous_response=response)
                )
        except Exception as e:
            _LOGGER.warning(f"Failed to list jobs for location {location_id}: {e}")

        return jobs

    def get_job(self, name, **query):
        """
        특정 Job의 상세 정보를 조회합니다.

        Args:
            name (str): Job의 전체 경로
            **query: 추가 쿼리 파라미터

        Returns:
            dict: Job 정보
        """
        query.update({"name": name})

        try:
            return self.client.projects().locations().jobs().get(**query).execute()
        except Exception as e:
            _LOGGER.warning(f"Failed to get job {name}: {e}")
            return {}

    # ===== Tasks API =====
    def list_tasks(self, task_group_name, **query):
        """
        TaskGroup의 Task 목록을 조회합니다.

        Args:
            task_group_name (str): TaskGroup의 전체 경로
                                  Format: projects/{project}/locations/{location}/jobs/{job}/taskGroups/{task_group}
            **query: 추가 쿼리 파라미터 (filter, pageSize, pageToken)

        Returns:
            list: Task 목록
        """
        tasks = []
        query.update({"parent": task_group_name})

        try:
            request = (
                self.client.projects()
                .locations()
                .jobs()
                .taskGroups()
                .tasks()
                .list(**query)
            )
            while request is not None:
                response = request.execute()
                for task in response.get("tasks", []):
                    tasks.append(task)
                request = (
                    self.client.projects()
                    .locations()
                    .jobs()
                    .taskGroups()
                    .tasks()
                    .list_next(previous_request=request, previous_response=response)
                )
        except Exception as e:
            _LOGGER.warning(f"Failed to list tasks for {task_group_name}: {e}")

        return tasks

    def get_task(self, name, **query):
        """
        특정 Task의 상세 정보를 조회합니다.

        Args:
            name (str): Task의 전체 경로
            **query: 추가 쿼리 파라미터

        Returns:
            dict: Task 정보
        """
        query.update({"name": name})

        try:
            return (
                self.client.projects()
                .locations()
                .jobs()
                .taskGroups()
                .tasks()
                .get(**query)
                .execute()
            )
        except Exception as e:
            _LOGGER.warning(f"Failed to get task {name}: {e}")
            return {}
