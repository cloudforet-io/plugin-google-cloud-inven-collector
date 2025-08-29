import logging
import time
from typing import List, Tuple

from spaceone.inventory.connector.storage_transfer.transfer_job import (
    StorageTransferConnector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.storage_transfer.agent_pool.cloud_service import (
    AgentPoolResource,
    AgentPoolResponse,
)
from spaceone.inventory.model.storage_transfer.agent_pool.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.storage_transfer.agent_pool.data import AgentPool

_LOGGER = logging.getLogger(__name__)


class StorageTransferAgentPoolManager(GoogleCloudManager):
    connector_name = "StorageTransferConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params) -> Tuple[List[AgentPoolResponse], List]:
        _LOGGER.debug("** Storage Transfer Agent Pool START **")
        start_time = time.time()
        """
        Args:
            params:
                - options
                - schema
                - secret_data
                - filter
                - zones
        Response:
            CloudServiceResponse/ErrorResourceResponse
        """
        collected_cloud_services = []
        error_responses = []
        agent_pool_name = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        ##################################
        # 0. Gather All Related Resources
        ##################################
        storage_transfer_conn: StorageTransferConnector = self.locator.get_connector(
            self.connector_name, **params
        )

        # Get agent pools
        agent_pools = storage_transfer_conn.list_agent_pools()

        for agent_pool in agent_pools:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                agent_pool_name = agent_pool.get("name", "")

                ##################################
                # 2. Make Base Data
                ##################################
                # 라벨 변환
                labels = self.convert_labels_format(agent_pool.get("labels", {}))

                # 데이터 업데이트
                agent_pool.update(
                    {
                        "project_id": project_id,
                        "region": "global",  # Agent Pool은 글로벌 리소스
                        "labels": labels,
                    }
                )

                agent_pool_data = AgentPool(agent_pool, strict=False)

                ##################################
                # 3. Make Return Resource
                ##################################
                agent_pool_resource = AgentPoolResource(
                    {
                        "name": agent_pool_name,
                        "account": project_id,
                        "tags": labels,
                        "region_code": "global",
                        "instance_type": agent_pool.get("state", ""),
                        "instance_size": 0,
                        "data": agent_pool_data,
                        "reference": ReferenceModel(agent_pool_data.reference()),
                    }
                )

                ##################################
                # 4. Make Collected Region Code
                ##################################
                self.set_region_code("global")

                ##################################
                # 5. Make Resource Response Object
                ##################################
                collected_cloud_services.append(
                    AgentPoolResponse({"resource": agent_pool_resource})
                )

            except Exception as e:
                _LOGGER.error(
                    f"[collect_cloud_service] agent_pool => {agent_pool_name}, error => {e}",
                    exc_info=True,
                )
                error_response = self.generate_resource_error_response(
                    e, "StorageTransfer", "AgentPool", agent_pool_name
                )
                error_responses.append(error_response)

        _LOGGER.debug(
            f"** Storage Transfer Agent Pool Finished {time.time() - start_time} Seconds **"
        )
        return collected_cloud_services, error_responses
