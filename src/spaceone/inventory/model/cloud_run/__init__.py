from spaceone.inventory.model.cloud_run.domain_mapping import (
    CLOUD_SERVICE_TYPES as DOMAIN_MAPPING_CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_run.job import (
    CLOUD_SERVICE_TYPES as JOB_CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_run.service import (
    CLOUD_SERVICE_TYPES as SERVICE_CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_run.worker_pool import (
    CLOUD_SERVICE_TYPES as WORKER_POOL_CLOUD_SERVICE_TYPES,
)

CLOUD_SERVICE_TYPES = (
    DOMAIN_MAPPING_CLOUD_SERVICE_TYPES
    + JOB_CLOUD_SERVICE_TYPES
    + SERVICE_CLOUD_SERVICE_TYPES
    + WORKER_POOL_CLOUD_SERVICE_TYPES
)
