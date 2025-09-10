import logging
from typing import Dict, List

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["BatchV1Connector"]

_LOGGER = logging.getLogger(__name__)


class BatchV1Connector(GoogleCloudConnector):
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
        다음 페이지 요청을 생성합니다 (최적화된 페이지네이션 처리).

        Args:
            api_method: 원본 API 메서드
            request: 현재 요청
            response: 현재 응답

        Returns:
            다음 페이지 요청 또는 None
        """
        try:
            # 메서드 경로를 기반으로 적절한 list_next 메서드 매핑
            method_path = str(api_method)
            
            # API 경로별 next 메서드 매핑 테이블 (성능 최적화)
            next_method_mapping = {
                "tasks().list": lambda: self.client.projects().locations().jobs().taskGroups().tasks().list_next,
                "jobs().list": lambda: self.client.projects().locations().jobs().list_next,
            }
            
            # 매핑 테이블에서 적절한 next 메서드 찾기
            for pattern, next_method_getter in next_method_mapping.items():
                if pattern in method_path:
                    next_method = next_method_getter()
                    return next_method(previous_request=request, previous_response=response)
            
            # 기본값: locations list_next
            return self.client.projects().locations().list_next(
                previous_request=request, previous_response=response
            )
            
        except (AttributeError, Exception) as e:
            # 다음 페이지가 없거나 에러 발생 시
            _LOGGER.debug(f"No more pages available or error in pagination: {e}")
            return None

    # ===== 선택적 사용 메서드들 =====

    def get_job_details(self, name: str, **query) -> Dict:
        """
        특정 Job의 상세 정보를 조회합니다 (필요시에만 사용).
        
        Args:
            name: Job의 전체 경로명
            **query: 추가 쿼리 파라미터
            
        Returns:
            Dict: Job 상세 정보
        """
        query.update({"name": name})
        try:
            return self.client.projects().locations().jobs().get(**query).execute()
        except Exception as e:
            _LOGGER.warning(f"Failed to get job details {name}: {e}")
            return {}

    def get_task_details(self, name: str, **query) -> Dict:
        """
        특정 Task의 상세 정보를 조회합니다 (필요시에만 사용).
        
        Args:
            name: Task의 전체 경로명
            **query: 추가 쿼리 파라미터
            
        Returns:
            Dict: Task 상세 정보
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
            _LOGGER.warning(f"Failed to get task details {name}: {e}")
            return {}
