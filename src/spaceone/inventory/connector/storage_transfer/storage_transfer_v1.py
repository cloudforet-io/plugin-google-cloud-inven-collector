import logging
from typing import Dict, List

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["StorageTransferConnector"]
_LOGGER = logging.getLogger(__name__)


class StorageTransferConnector(GoogleCloudConnector):
    """Google Cloud Storage Transfer Service API 커넥터"""

    google_client_service = "storagetransfer"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_transfer_jobs(self, **query) -> List[Dict]:
        """전송 작업 목록을 조회합니다.

        Args:
            **query: API 쿼리 파라미터

        Returns:
            전송 작업 목록

        Raises:
            Exception: API 호출 실패 시
        """
        transfer_jobs = []
        query.update(
            {"filter": f'{{"project_id": "{self.project_id}"}}', "pageSize": 100}
        )

        try:
            request = self.client.transferJobs().list(**query)

            while request is not None:
                response = request.execute()
                jobs_in_response = response.get("transferJobs", [])
                transfer_jobs.extend(jobs_in_response)

                request = self.client.transferJobs().list_next(
                    previous_request=request, previous_response=response
                )

            return transfer_jobs

        except Exception as e:
            _LOGGER.error(
                f"Failed to list transfer jobs for project {self.project_id}: {e}"
            )
            raise

    def list_transfer_operations(self, **query) -> List[Dict]:
        """전송 작업 실행 목록을 조회합니다.

        Args:
            **query: API 쿼리 파라미터

        Returns:
            전송 작업 실행 목록

        Raises:
            Exception: API 호출 실패 시
        """
        operations = []

        # 필터 설정
        filter_dict = {"project_id": self.project_id}

        # 특정 transfer job의 operations만 조회하는 경우
        if "transfer_job_names" in query:
            filter_dict["transfer_job_names"] = query["transfer_job_names"]

        query.update(
            {
                "name": "transferOperations",  # name 파라미터는 필수 - "TransferOperaions" 고정갑사
                "filter": str(filter_dict).replace("'", '"'),
                "pageSize": 100,
            }
        )

        try:
            request = self.client.transferOperations().list(**query)

            while request is not None:
                response = request.execute()
                ops_in_response = response.get("operations", [])
                operations.extend(ops_in_response)

                request = self.client.transferOperations().list_next(
                    previous_request=request, previous_response=response
                )

            return operations

        except Exception as e:
            _LOGGER.error(
                f"Failed to list transfer operations for project {self.project_id}: {e}"
            )
            raise

    def list_agent_pools(self, **query) -> List[Dict]:
        """에이전트 풀 목록을 조회합니다.

        Args:
            **query: API 쿼리 파라미터

        Returns:
            에이전트 풀 목록

        Raises:
            Exception: API 호출 실패 시
        """
        agent_pools = []
        query.update({"projectId": self.project_id, "pageSize": 100})

        try:
            request = self.client.projects().agentPools().list(**query)

            while request is not None:
                response = request.execute()
                pools_in_response = response.get("agentPools", [])
                agent_pools.extend(pools_in_response)

                request = (
                    self.client.projects()
                    .agentPools()
                    .list_next(previous_request=request, previous_response=response)
                )
            return agent_pools

        except Exception as e:
            _LOGGER.error(
                f"Failed to list agent pools for project {self.project_id}: {e}"
            )
            raise
