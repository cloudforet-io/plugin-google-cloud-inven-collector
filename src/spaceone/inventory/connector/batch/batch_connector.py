import logging
from typing import Dict, List

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["BatchConnector"]

_LOGGER = logging.getLogger(__name__)


class BatchConnector(GoogleCloudConnector):
    """최적화된 Batch Connector - 효율적인 API 호출과 에러 처리"""

    google_client_service = "batch"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_all_jobs(self, **query) -> List[Dict]:
        """
        모든 Location의 Job 목록을 글로벌로 조회합니다.
        locations/- 패턴을 사용하여 한번에 모든 location의 jobs를 가져옵니다.

        Args:
            **query: 추가 쿼리 파라미터

        Returns:
            List[Dict]: 모든 Job 목록
        """
        parent = f"projects/{self.project_id}/locations/-"
        return self._paginated_list(
            self.client.projects().locations().jobs().list,
            parent=parent,
            resource_key="jobs",
            error_context="list all jobs",
            **query,
        )

    def list_tasks(self, task_group_name: str, **query) -> List[Dict]:
        """
        TaskGroup의 Task 목록을 조회합니다.

        Args:
            task_group_name: TaskGroup의 전체 경로
            **query: 추가 쿼리 파라미터

        Returns:
            List[Dict]: Task 목록
        """
        return self._paginated_list(
            self.client.projects().locations().jobs().taskGroups().tasks().list,
            parent=task_group_name,
            resource_key="tasks",
            error_context=f"list tasks for {task_group_name}",
            **query,
        )

    def _paginated_list(
        self, api_method, resource_key: str, error_context: str, **query
    ) -> List[Dict]:
        """
        페이지네이션을 지원하는 API 호출의 공통 처리 로직

        Args:
            api_method: API 메서드 (예: client.jobs().list)
            resource_key: 응답에서 추출할 리소스 키 (예: 'jobs', 'tasks')
            error_context: 에러 로그에 사용할 컨텍스트
            **query: API 쿼리 파라미터

        Returns:
            List[Dict]: 수집된 리소스 목록
        """
        resources = []

        try:
            request = api_method(**query)
            while request is not None:
                response = request.execute()

                # 리소스 추가
                page_resources = response.get(resource_key, [])
                resources.extend(page_resources)

                # 다음 페이지 요청 생성
                request = self._get_next_request(api_method, request, response)

            _LOGGER.debug(f"Successfully collected {len(resources)} {resource_key}")

        except Exception as e:
            _LOGGER.warning(f"Failed to {error_context}: {e}")

        return resources

    def _get_next_request(self, api_method, request, response):
        """
        다음 페이지 요청을 생성합니다.

        Args:
            api_method: 원본 API 메서드
            request: 현재 요청
            response: 현재 응답

        Returns:
            다음 페이지 요청 또는 None
        """
        try:
            # client 객체에서 해당 경로의 _next 메서드 찾기
            if "jobs" in str(api_method):
                if "tasks" in str(api_method):
                    # tasks API
                    next_method = (
                        self.client.projects()
                        .locations()
                        .jobs()
                        .taskGroups()
                        .tasks()
                        .list_next
                    )
                else:
                    # jobs API
                    next_method = self.client.projects().locations().jobs().list_next
            else:
                # locations API
                next_method = self.client.projects().locations().list_next

            return next_method(previous_request=request, previous_response=response)
        except Exception:
            # 다음 페이지가 없거나 에러 발생 시
            return None

    # ===== 레거시 호환성을 위한 메서드들 =====

    def list_locations(self, **query) -> List[Dict]:
        """
        레거시 호환성을 위한 메서드. 현재는 사용되지 않습니다.
        """
        _LOGGER.warning("list_locations is deprecated and not used in optimized flow")
        return []

    def list_jobs(self, location_id: str, **query) -> List[Dict]:
        """
        레거시 호환성을 위한 메서드. list_all_jobs 사용을 권장합니다.
        """
        _LOGGER.warning("list_jobs is deprecated. Use list_all_jobs instead")
        parent = f"projects/{self.project_id}/locations/{location_id}"
        return self._paginated_list(
            self.client.projects().locations().jobs().list,
            parent=parent,
            resource_key="jobs",
            error_context=f"list jobs for location {location_id}",
            **query,
        )

    def get_job(self, name: str, **query) -> Dict:
        """
        특정 Job의 상세 정보를 조회합니다. 현재는 사용되지 않습니다.
        """
        query.update({"name": name})
        try:
            return self.client.projects().locations().jobs().get(**query).execute()
        except Exception as e:
            _LOGGER.warning(f"Failed to get job {name}: {e}")
            return {}

    def get_task(self, name: str, **query) -> Dict:
        """
        특정 Task의 상세 정보를 조회합니다. 현재는 사용되지 않습니다.
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
