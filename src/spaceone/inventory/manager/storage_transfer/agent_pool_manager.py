import logging
import time
from typing import List, Tuple

from spaceone.inventory.connector.storage_transfer.storage_transfer_v1 import (
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
    """Storage Transfer Agent Pool 리소스 관리자"""

    connector_name = "StorageTransferConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params) -> Tuple[List[AgentPoolResponse], List]:
        """Storage Transfer Agent Pool 리소스를 수집합니다.

        Args:
            params: 수집 파라미터
                - options: 수집 옵션
                - schema: 스키마 정보
                - secret_data: 인증 정보
                - filter: 필터 조건
                - zones: 대상 영역

        Returns:
            수집된 CloudService 응답과 에러 응답의 튜플
        """
        _LOGGER.debug("** Storage Transfer Agent Pool START **")
        start_time = time.time()

        collected_cloud_services = []
        error_responses = []
        agent_pool_name = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        try:
            ##################################
            # 0. Gather All Related Resources
            ##################################
            storage_transfer_conn: StorageTransferConnector = (
                self.locator.get_connector(self.connector_name, **params)
            )

            # Get agent pools
            agent_pools = storage_transfer_conn.list_agent_pools()
            _LOGGER.info(f"Found {len(agent_pools)} agent pools to process")

            for agent_pool in agent_pools:
                try:
                    ##################################
                    # 1. Set Basic Information
                    ##################################
                    agent_pool_name = agent_pool.get("name", "")
                    agent_pool_simple_name = (
                        agent_pool_name.split("/")[-1]
                        if "/" in agent_pool_name
                        else agent_pool_name
                    )

                    ##################################
                    # 2. Make Base Data
                    ##################################

                    agent_pool.update(
                        {
                            "name": agent_pool_simple_name,
                            "project": project_id,
                        }
                    )
                    self_link = (
                        f"https://storagetransfer.googleapis.com/v1/{agent_pool_name}"
                    )

                    # No labels!!
                    agent_pool_data = AgentPool(agent_pool, strict=False)

                    ##################################
                    # 3. Make Return Resource
                    ##################################
                    agent_pool_resource = AgentPoolResource(
                        {
                            "name": agent_pool_simple_name,
                            "account": project_id,
                            "region_code": "global",
                            "instance_type": agent_pool.get("state", ""),
                            "data": agent_pool_data,
                            "reference": ReferenceModel(
                                agent_pool_data.reference(self_link=self_link)
                            ),
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
                        f"Failed to process agent pool {agent_pool_name}: {e}",
                        exc_info=True,
                    )
                    error_response = self.generate_resource_error_response(
                        e, "StorageTransfer", "AgentPool", agent_pool_name
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(
                f"Failed to collect Storage Transfer Agent Pools: {e}", exc_info=True
            )
            error_response = self.generate_resource_error_response(
                e, "StorageTransfer", "AgentPool", "collection"
            )
            error_responses.append(error_response)

        # 수집 완료 로깅
        _LOGGER.debug(
            f"** Storage Transfer Agent Pool Finished {time.time() - start_time} Seconds **"
        )

        return collected_cloud_services, error_responses
