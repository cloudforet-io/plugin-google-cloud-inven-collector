# V1 Managers
from spaceone.inventory.manager.cloud_run.configuration_v1_manager import (
    CloudRunConfigurationV1Manager,
)
from spaceone.inventory.manager.cloud_run.domain_mapping_v1_manager import (
    CloudRunDomainMappingV1Manager,
)
from spaceone.inventory.manager.cloud_run.job_v1_manager import (
    CloudRunJobV1Manager,
)

# V2 Managers
from spaceone.inventory.manager.cloud_run.job_v2_manager import (
    CloudRunJobV2Manager,
)
from spaceone.inventory.manager.cloud_run.operation_v2_manager import (
    CloudRunOperationV2Manager,
)
from spaceone.inventory.manager.cloud_run.route_v1_manager import (
    CloudRunRouteV1Manager,
)
from spaceone.inventory.manager.cloud_run.service_v1_manager import (
    CloudRunServiceV1Manager,
)
from spaceone.inventory.manager.cloud_run.service_v2_manager import (
    CloudRunServiceV2Manager,
)
from spaceone.inventory.manager.cloud_run.worker_pool_v1_manager import (
    CloudRunWorkerPoolV1Manager,
)
from spaceone.inventory.manager.cloud_run.worker_pool_v2_manager import (
    CloudRunWorkerPoolV2Manager,
)

__all__ = [
    # V1 Managers
    "CloudRunConfigurationV1Manager",
    "CloudRunDomainMappingV1Manager",
    "CloudRunJobV1Manager",
    "CloudRunRouteV1Manager",
    "CloudRunServiceV1Manager",
    "CloudRunWorkerPoolV1Manager",
    # V2 Managers
    "CloudRunJobV2Manager",
    "CloudRunOperationV2Manager",
    "CloudRunServiceV2Manager",
    "CloudRunWorkerPoolV2Manager",
]