from spaceone.inventory.model.cloud_build.cloud_build import (
    CLOUD_SERVICE_TYPES as BUILD_CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_build.connection import (
    CLOUD_SERVICE_TYPES as CONNECTION_CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_build.repository import (
    CLOUD_SERVICE_TYPES as REPOSITORY_CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_build.trigger import (
    CLOUD_SERVICE_TYPES as TRIGGER_CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_build.worker_pool import (
    CLOUD_SERVICE_TYPES as WORKER_POOL_CLOUD_SERVICE_TYPES,
)

CLOUD_SERVICE_TYPES = (
    BUILD_CLOUD_SERVICE_TYPES
    + CONNECTION_CLOUD_SERVICE_TYPES
    + REPOSITORY_CLOUD_SERVICE_TYPES
    + TRIGGER_CLOUD_SERVICE_TYPES
    + WORKER_POOL_CLOUD_SERVICE_TYPES
)
