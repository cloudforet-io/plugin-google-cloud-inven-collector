from schematics import Model
from schematics.types import (
    ListType,
    ModelType,
    StringType,
)

from spaceone.inventory.libs.schema.cloud_service import BaseResource


class Labels(Model):
    key = StringType()
    value = StringType()


class BandwidthLimit(Model):
    """대역폭 제한 정보"""

    limit_mbps = StringType(deserialize_from="limitMbps", serialize_when_none=False)


class AgentPool(BaseResource):
    """Storage Transfer Agent Pool 모델"""

    display_name = StringType(deserialize_from="displayName", serialize_when_none=False)
    state = StringType(choices=("CREATED", "INSTALLING", "CONNECTED", "DELETING"))
    bandwidth_limit = ModelType(
        BandwidthLimit, deserialize_from="bandwidthLimit", serialize_when_none=False
    )

    # 표시용 정보
    project_id = StringType(serialize_when_none=False)
    region = StringType(serialize_when_none=False)

    labels = ListType(ModelType(Labels), default=[])

    def reference(self):
        return {
            "resource_id": self.name,
            "external_link": f"https://console.cloud.google.com/transfer/agent-pools?project={self.project_id}",
        }
