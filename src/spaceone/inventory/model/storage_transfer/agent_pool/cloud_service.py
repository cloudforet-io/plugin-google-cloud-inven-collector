from schematics.types import ModelType, PolyModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    EnumDyField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    TableDynamicLayout,
)
from spaceone.inventory.model.storage_transfer.agent_pool.data import (
    AgentPool,
)

"""
Agent Pool
"""

# TAB - Agent Pool Configuration
agent_pool_configuration_meta = ItemDynamicLayout.set_fields(
    "Configuration",
    fields=[
        TextDyField.data_source("Pool Name", "name"),
        TextDyField.data_source("Display Name", "data.display_name"),
        TextDyField.data_source("Project ID", "data.project_id"),
        EnumDyField.data_source(
            "State",
            "data.state",
            default_state={
                "safe": ["CONNECTED"],
                "warning": ["CREATED", "INSTALLING"],
                "alert": ["DELETING"],
            },
        ),
        TextDyField.data_source(
            "Bandwidth Limit (Mbps)", "data.bandwidth_limit.limit_mbps"
        ),
    ],
)

# TAB - Labels
agent_pool_labels_meta = TableDynamicLayout.set_fields(
    "Labels",
    root_path="data.labels",
    fields=[
        TextDyField.data_source("Key", "key"),
        TextDyField.data_source("Value", "value"),
    ],
)

agent_pool_meta = CloudServiceMeta.set_layouts(
    [
        agent_pool_configuration_meta,
        agent_pool_labels_meta,
    ]
)


class StorageTransferResource(CloudServiceResource):
    cloud_service_group = StringType(default="StorageTransfer")


class AgentPoolResource(StorageTransferResource):
    cloud_service_type = StringType(default="AgentPool")
    data = ModelType(AgentPool)
    _metadata = ModelType(
        CloudServiceMeta, default=agent_pool_meta, serialized_name="metadata"
    )


class AgentPoolResponse(CloudServiceResponse):
    resource = PolyModelType(AgentPoolResource)
