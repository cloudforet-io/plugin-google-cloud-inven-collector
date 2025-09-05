# Storage Transfer 모델 패키지

# Transfer Job 리소스
# Agent Pool 리소스
from spaceone.inventory.model.storage_transfer.agent_pool.cloud_service import (
    AgentPoolResource,
    AgentPoolResponse,
)
from spaceone.inventory.model.storage_transfer.agent_pool.cloud_service_type import (
    CLOUD_SERVICE_TYPES as AGENT_POOL_CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.storage_transfer.agent_pool.data import AgentPool
from spaceone.inventory.model.storage_transfer.transfer_job.cloud_service import (
    TransferJobResource,
    TransferJobResponse,
)
from spaceone.inventory.model.storage_transfer.transfer_job.cloud_service_type import (
    CLOUD_SERVICE_TYPES as TRANSFER_JOB_CLOUD_SERVICE_TYPES,
)

# 데이터 모델들
from spaceone.inventory.model.storage_transfer.transfer_job.data import TransferJob

# Transfer Operation 리소스
from spaceone.inventory.model.storage_transfer.transfer_operation.cloud_service import (
    TransferOperationResource,
    TransferOperationResponse,
)
from spaceone.inventory.model.storage_transfer.transfer_operation.cloud_service_type import (
    CLOUD_SERVICE_TYPES as TRANSFER_OPERATION_CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.storage_transfer.transfer_operation.data import (
    TransferOperation,
)

# 모든 Cloud Service Types 집계
CLOUD_SERVICE_TYPES = (
    TRANSFER_JOB_CLOUD_SERVICE_TYPES
    + AGENT_POOL_CLOUD_SERVICE_TYPES
    + TRANSFER_OPERATION_CLOUD_SERVICE_TYPES
)

__all__ = [
    # Transfer Job
    "TransferJobResource",
    "TransferJobResponse",
    "TRANSFER_JOB_CLOUD_SERVICE_TYPES",
    # Agent Pool
    "AgentPoolResource",
    "AgentPoolResponse",
    "AGENT_POOL_CLOUD_SERVICE_TYPES",
    # Transfer Operation
    "TransferOperationResource",
    "TransferOperationResponse",
    "TRANSFER_OPERATION_CLOUD_SERVICE_TYPES",
    # Data Models
    "TransferJob",
    "AgentPool",
    "TransferOperation",
    # Aggregated Types
    "CLOUD_SERVICE_TYPES",
]
