# V1 리소스 타입들
from spaceone.inventory.model.cloud_run.configuration_v1 import (
    CLOUD_SERVICE_TYPES as CONFIGURATION_V1_CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_run.domain_mapping_v1 import (
    CLOUD_SERVICE_TYPES as DOMAIN_MAPPING_V1_CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_run.job_v1 import (
    CLOUD_SERVICE_TYPES as JOB_V1_CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_run.job_v2 import (
    CLOUD_SERVICE_TYPES as JOB_V2_CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_run.operation_v2 import (
    CLOUD_SERVICE_TYPES as OPERATION_V2_CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_run.route_v1 import (
    CLOUD_SERVICE_TYPES as ROUTE_V1_CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_run.service_v1 import (
    CLOUD_SERVICE_TYPES as SERVICE_V1_CLOUD_SERVICE_TYPES,
)

# V2 리소스 타입들
from spaceone.inventory.model.cloud_run.service_v2 import (
    CLOUD_SERVICE_TYPES as SERVICE_V2_CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_run.worker_pool_v1 import (
    CLOUD_SERVICE_TYPES as WORKER_POOL_V1_CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_run.worker_pool_v2 import (
    CLOUD_SERVICE_TYPES as WORKER_POOL_V2_CLOUD_SERVICE_TYPES,
)

CLOUD_SERVICE_TYPES = (
    DOMAIN_MAPPING_V1_CLOUD_SERVICE_TYPES
    + SERVICE_V1_CLOUD_SERVICE_TYPES
    + JOB_V1_CLOUD_SERVICE_TYPES
    + WORKER_POOL_V1_CLOUD_SERVICE_TYPES
    + CONFIGURATION_V1_CLOUD_SERVICE_TYPES
    + ROUTE_V1_CLOUD_SERVICE_TYPES
    + SERVICE_V2_CLOUD_SERVICE_TYPES
    + JOB_V2_CLOUD_SERVICE_TYPES
    + WORKER_POOL_V2_CLOUD_SERVICE_TYPES
    + OPERATION_V2_CLOUD_SERVICE_TYPES
)
