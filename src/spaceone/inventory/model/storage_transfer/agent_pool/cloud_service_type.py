import os

from spaceone.inventory.conf.cloud_service_conf import ASSET_URL
from spaceone.inventory.libs.common_parser import get_data_from_yaml
from spaceone.inventory.libs.schema.cloud_service_type import (
    CloudServiceTypeMeta,
    CloudServiceTypeResource,
    CloudServiceTypeResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    EnumDyField,
    SearchField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_widget import (
    CardWidget,
    ChartWidget,
)

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, "widget/total_count.yml")
count_by_state_conf = os.path.join(current_dir, "widget/count_by_state.yml")

cst_agent_pool = CloudServiceTypeResource()
cst_agent_pool.name = "AgentPool"
cst_agent_pool.provider = "google_cloud"
cst_agent_pool.group = "StorageTransfer"
cst_agent_pool.service_code = "Storage Transfer Service"
cst_agent_pool.is_primary = False
cst_agent_pool.is_major = False
cst_agent_pool.labels = ["Storage", "Transfer", "Agent"]
cst_agent_pool.tags = {
    "spaceone:icon": f"{ASSET_URL}/Storage-Transfer.svg",
}

cst_agent_pool._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Display Name", "data.display_name"),
        EnumDyField.data_source(
            "State",
            "data.state",
            default_state={
                "safe": ["CONNECTED"],
                "warning": ["CREATED", "INSTALLING"],
                "alert": ["DELETING"],
            },
        ),
        TextDyField.data_source("Bandwidth Limit", "data.bandwidth_limit.limit_mbps"),
        TextDyField.data_source("Project ID", "data.project_id"),
    ],
    search=[
        SearchField.set(name="Agent Pool Name", key="name"),
        SearchField.set(name="Display Name", key="data.display_name"),
        SearchField.set(name="Project ID", key="data.project_id"),
        SearchField.set(
            name="State",
            key="data.state",
            enums={
                "CREATED": {"label": "Created"},
                "INSTALLING": {"label": "Installing"},
                "CONNECTED": {"label": "Connected"},
                "DELETING": {"label": "Deleting"},
            },
        ),
        SearchField.set(name="Bandwidth Limit", key="data.bandwidth_limit.limit_mbps"),
        SearchField.set(name="Account ID", key="account"),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_state_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_agent_pool}),
]
