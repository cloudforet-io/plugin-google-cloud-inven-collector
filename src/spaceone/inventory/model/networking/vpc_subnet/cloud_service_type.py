import os

from spaceone.inventory.libs.common_parser import get_data_from_yaml
from spaceone.inventory.libs.schema.cloud_service_type import (
    CloudServiceTypeResource,
    CloudServiceTypeResponse,
    CloudServiceTypeMeta,
)
from spaceone.inventory.libs.schema.metadata.dynamic_widget import (
    CardWidget,
    ChartWidget,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    TextDyField,
    SearchField,
    DateTimeDyField,
    EnumDyField,
)
from spaceone.inventory.conf.cloud_service_conf import ASSET_URL

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, "widget/total_count.yml")
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yml")
count_by_project_conf = os.path.join(current_dir, "widget/count_by_project.yml")

cst_vpc_subnet = CloudServiceTypeResource()
cst_vpc_subnet.name = "VPCSubnet"
cst_vpc_subnet.provider = "google_cloud"
cst_vpc_subnet.group = "Networking"
cst_vpc_subnet.service_code = "Networking"
cst_vpc_subnet.is_primary = True
cst_vpc_subnet.is_major = True
cst_vpc_subnet.labels = ["Networking"]
cst_vpc_subnet.tags = {
    "spaceone:icon": f"{ASSET_URL}/VPC.svg",
    "spaceone:display_name": "VPCSubnet",
}

cst_vpc_subnet._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("Region", "data.region"),
        TextDyField.data_source("VPC Network", "data.network_display"),
        TextDyField.data_source("IP Address Range", "data.ip_cidr_range"),
        TextDyField.data_source("Gateway", "data.gateway_address"),
        EnumDyField.data_source(
            "Private Google Access",
            "data.google_access",
            default_state={
                "safe": ["On"],
                "warning": ["Off"],
            },
        ),
        EnumDyField.data_source(
            "Flow Logs",
            "data.flow_log",
            default_state={
                "safe": ["On"],
                "warning": ["Off"],
            },
        ),
        TextDyField.data_source("Purpose", "data.purpose"),
        TextDyField.data_source("State", "data.state"),
        DateTimeDyField.data_source("Creation Time", "data.creation_timestamp"),
    ],
    search=[
        SearchField.set(name="Subnet ID", key="data.id"),
        SearchField.set(name="Name", key="data.name"),
        SearchField.set(name="Region", key="data.region"),
        SearchField.set(name="VPC Network", key="data.network_display"),
        SearchField.set(name="IP Address Range", key="data.ip_cidr_range"),
        SearchField.set(name="Gateway", key="data.gateway_address"),
        SearchField.set(name="Purpose", key="data.purpose"),
        SearchField.set(name="State", key="data.state"),
        SearchField.set(
            name="Creation Time", key="data.creation_timestamp", data_type="datetime"
        ),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_vpc_subnet}),
]
