from schematics import Model
from schematics.types import (
    ModelType,
    StringType,
)

from spaceone.inventory.libs.schema.cloud_service import BaseResource


class BandwidthLimit(Model):
    """Bandwidth limit information"""

    limit_mbps = StringType(deserialize_from="limitMbps", serialize_when_none=False)


class AgentPool(BaseResource):
    """Storage Transfer Agent Pool model"""

    full_name = StringType()
    display_name = StringType(deserialize_from="displayName", serialize_when_none=False)
    state = StringType()
    bandwidth_limit = ModelType(
        BandwidthLimit, deserialize_from="bandwidthLimit", serialize_when_none=False
    )

    def reference(self):
        return {
            "resource_id": f"https://storagetransfer.googleapis.com/v1/{self.full_name}",
            "external_link": f"https://console.cloud.google.com/transfer/agent-pools/pool/{self.name}/agents?project={self.project}",
        }
