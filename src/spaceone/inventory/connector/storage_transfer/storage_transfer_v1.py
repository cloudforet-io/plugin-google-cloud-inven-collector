import logging
from typing import Dict, List

from googleapiclient.errors import HttpError
from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["StorageTransferConnector"]
_LOGGER = logging.getLogger(__name__)


class StorageTransferConnector(GoogleCloudConnector):
    google_client_service = "storagetransfer"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_transfer_jobs(self, **query) -> List[Dict]:
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

        except HttpError as e:
            if e.resp.status == 404:
                _LOGGER.warning(
                    f"Storage Transfer service not available for project {self.project_id} "
                )
                return []
            elif e.resp.status == 403:
                _LOGGER.warning(
                    f"Storage Transfer API not enabled or insufficient permissions for project {self.project_id}, "
                )
                return []
            else:
                _LOGGER.error(f"HTTP error listing transfer jobs for project {self.project_id}: {e}")
                raise e
        except Exception as e:
            _LOGGER.error(
                f"Failed to list transfer jobs for project {self.project_id}: {e}"
            )
            raise

    def list_transfer_operations(self, **query) -> List[Dict]:
        operations = []

        filter_dict = {"project_id": self.project_id}

        if "transfer_job_names" in query:
            filter_dict["transfer_job_names"] = query["transfer_job_names"]

        query.update(
            {
                "name": "transferOperations",
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

        except HttpError as e:
            if e.resp.status == 404:
                _LOGGER.warning(
                    f"Storage Transfer service not available for project {self.project_id} "
                )
                return []
            elif e.resp.status == 403:
                _LOGGER.warning(
                    f"Storage Transfer API not enabled or insufficient permissions for project {self.project_id}, "
                )
                return []
            else:
                _LOGGER.error(f"HTTP error listing transfer operations for project {self.project_id}: {e}")
                raise e
        except Exception as e:
            _LOGGER.error(
                f"Failed to list transfer operations for project {self.project_id}: {e}"
            )
            raise

    def list_agent_pools(self, **query) -> List[Dict]:
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

        except HttpError as e:
            if e.resp.status == 404:
                _LOGGER.warning(
                    f"Storage Transfer service not available for project {self.project_id} "
                )
                return []
            elif e.resp.status == 403:
                _LOGGER.warning(
                    f"Storage Transfer API not enabled or insufficient permissions for project {self.project_id}, "
                )
                return []
            else:
                _LOGGER.error(f"HTTP error listing agent pools for project {self.project_id}: {e}")
                raise e
        except Exception as e:
            _LOGGER.error(
                f"Failed to list agent pools for project {self.project_id}: {e}"
            )
            raise
