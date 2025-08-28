import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["StorageTransferConnector"]
_LOGGER = logging.getLogger(__name__)


class StorageTransferConnector(GoogleCloudConnector):
    google_client_service = "storagetransfer"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_transfer_jobs(self, **query):
        """전송 작업 목록을 조회합니다."""
        transfer_jobs = []
        query.update({"filter": f'{{"project_id": "{self.project_id}"}}'})
        request = self.client.transferJobs().list(**query)

        while request is not None:
            response = request.execute()
            for transfer_job in response.get("transferJobs", []):
                transfer_jobs.append(transfer_job)
            request = self.client.transferJobs().list_next(
                previous_request=request, previous_response=response
            )

        return transfer_jobs

    def get_transfer_job(self, job_name, project_id):
        """특정 전송 작업의 상세 정보를 조회합니다."""
        return (
            self.client.transferJobs()
            .get(jobName=job_name, projectId=project_id)
            .execute()
        )

    def list_transfer_operations(self, **query):
        """전송 작업 실행 목록을 조회합니다."""
        operations = []

        # name 파라미터는 필수 - "transferOperations" 고정값
        name = "transferOperations"

        # 필터 설정
        filter_dict = {"project_id": self.project_id}

        # 특정 transfer job의 operations만 조회하는 경우
        if "transfer_job_names" in query:
            filter_dict["transfer_job_names"] = query["transfer_job_names"]

        # API 호출 파라미터 설정
        api_params = {"name": name, "filter": str(filter_dict).replace("'", '"')}

        # 추가 쿼리 파라미터가 있으면 포함
        for key, value in query.items():
            if key not in ["transfer_job_names"]:  # 이미 처리된 파라미터 제외
                api_params[key] = value

        request = self.client.transferOperations().list(**api_params)

        while request is not None:
            response = request.execute()
            for operation in response.get("operations", []):
                operations.append(operation)
            request = self.client.transferOperations().list_next(
                previous_request=request, previous_response=response
            )

        return operations

    def get_transfer_operation(self, operation_name):
        """특정 전송 작업 실행의 상세 정보를 조회합니다."""
        return self.client.transferOperations().get(name=operation_name).execute()

    def list_agent_pools(self, **query):
        """에이전트 풀 목록을 조회합니다."""
        agent_pools = []
        query.update({"projectId": self.project_id})
        request = self.client.projects().agentPools().list(**query)

        while request is not None:
            response = request.execute()
            for agent_pool in response.get("agentPools", []):
                agent_pools.append(agent_pool)
            request = (
                self.client.projects()
                .agentPools()
                .list_next(previous_request=request, previous_response=response)
            )

        return agent_pools
