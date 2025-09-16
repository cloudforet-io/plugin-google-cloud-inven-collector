import os

from spaceone.inventory.libs.common_parser import get_data_from_yaml
from spaceone.inventory.libs.schema.metadata.dynamic_widget import (
    CardWidget,
    ChartWidget,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    TextDyField,
    EnumDyField,
    ListDyField,
    DateTimeDyField,
    SearchField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    TableDynamicLayout,
    ListDynamicLayout,
)
from spaceone.inventory.libs.schema.cloud_service_type import (
    CloudServiceTypeResource,
    CloudServiceTypeResponse,
    CloudServiceTypeMeta,
)
from spaceone.inventory.conf.cloud_service_conf import ASSET_URL

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, "widget/total_count.yml")
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yml")
count_by_project_conf = os.path.join(current_dir, "widget/count_by_project.yml")

"""
VPC Gateway
"""
vpc_gateway_meta = ItemDynamicLayout.set_fields(
    "Gateway Information",
    fields=[
        TextDyField.data_source("Gateway Name", "data.name"),
        EnumDyField.data_source(
            "Gateway Type",
            "data.gateway_type",
            default_badge={
                "indigo.500": ["NAT_GATEWAY"],
                "blue.500": ["VPN_GATEWAY"],
                "green.500": ["TARGET_VPN_GATEWAY"],
            },
        ),
        TextDyField.data_source("Region", "data.region"),
        TextDyField.data_source("Network", "data.network"),
        TextDyField.data_source("Status", "data.status"),
        TextDyField.data_source("Router Name", "data.router_name"),
        TextDyField.data_source("Description", "data.description"),
        DateTimeDyField.data_source("Created", "data.creation_timestamp"),
    ],
)

vpc_gateway_nat_info = ItemDynamicLayout.set_fields(
    "NAT Configuration",
    fields=[
        TextDyField.data_source("NAT IP Allocation", "data.nat_ip_allocate_option"),
        TextDyField.data_source("Source Subnet IP Ranges", "data.source_subnetwork_ip_ranges_to_nat"),
        ListDyField.data_source("NAT IPs", "data.nat_ips"),
        TextDyField.data_source("Min Ports per VM", "data.min_ports_per_vm"),
        TextDyField.data_source("Enable Endpoint Independent Mapping", "data.enable_endpoint_independent_mapping"),
    ],
)

vpc_gateway_vpn_info = ItemDynamicLayout.set_fields(
    "VPN Configuration",
    fields=[
        ListDyField.data_source("VPN Interfaces", "data.vpn_interfaces"),
        ListDyField.data_source("Forwarding Rules", "data.forwarding_rules"),
        ListDyField.data_source("Tunnels", "data.tunnels"),
    ],
)

vpc_gateway_timeout_settings = ItemDynamicLayout.set_fields(
    "Timeout Settings",
    fields=[
        TextDyField.data_source("ICMP Idle Timeout (sec)", "data.icmp_idle_timeout_sec"),
        TextDyField.data_source("TCP Established Idle Timeout (sec)", "data.tcp_established_idle_timeout_sec"),
        TextDyField.data_source("TCP Transitory Idle Timeout (sec)", "data.tcp_transitory_idle_timeout_sec"),
        TextDyField.data_source("TCP Time Wait Timeout (sec)", "data.tcp_time_wait_timeout_sec"),
        TextDyField.data_source("UDP Idle Timeout (sec)", "data.udp_idle_timeout_sec"),
    ],
)

vpc_gateway_subnetworks = TableDynamicLayout.set_fields(
    "NAT Subnetworks",
    root_path="data.nat_subnetworks",
    fields=[
        TextDyField.data_source("Name", "name"),
        ListDyField.data_source("Source IP Ranges", "source_ip_ranges_to_nat"),
        ListDyField.data_source("Secondary IP Range Names", "secondary_ip_range_names"),
    ],
)

vpc_gateway_vpn_interfaces = TableDynamicLayout.set_fields(
    "VPN Interfaces",
    root_path="data.vpn_interfaces",
    fields=[
        TextDyField.data_source("Interface ID", "id"),
        TextDyField.data_source("IP Address", "ip_address"),
        TextDyField.data_source("Interconnect Attachment", "interconnect_attachment"),
    ],
)

vpc_gateway_meta_layouts = ListDynamicLayout.set_layouts(
    "Gateway Details", 
    layouts=[
        vpc_gateway_meta,
        vpc_gateway_nat_info,
        vpc_gateway_vpn_info,
        vpc_gateway_timeout_settings,
        vpc_gateway_subnetworks,
        vpc_gateway_vpn_interfaces,
    ]
)

cst_vpc_gateway = CloudServiceTypeResource()
cst_vpc_gateway.name = "VPCGateway"
cst_vpc_gateway.provider = "google_cloud"
cst_vpc_gateway.group = "Networking"
cst_vpc_gateway.service_code = "Networking"
cst_vpc_gateway.is_primary = True
cst_vpc_gateway.is_major = True
cst_vpc_gateway.labels = ["Networking"]
cst_vpc_gateway.tags = {
    "spaceone:icon": f"{ASSET_URL}/VPC.svg",
    "spaceone:display_name": "VPCGateway",
}

cst_vpc_gateway._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Gateway Name", "data.name"),
        EnumDyField.data_source(
            "Gateway Type",
            "data.gateway_type",
            default_badge={
                "indigo.500": ["NAT_GATEWAY"],
                "blue.500": ["VPN_GATEWAY"],
                "green.500": ["TARGET_VPN_GATEWAY"],
            },
        ),
        TextDyField.data_source("Region", "data.region"),
        TextDyField.data_source("Network", "data.network"),
        TextDyField.data_source("Status", "data.status"),
        DateTimeDyField.data_source("Created", "data.creation_timestamp"),
    ],
    search=[
        SearchField.set(name="Gateway Name", key="data.name"),
        SearchField.set(name="Gateway Type", key="data.gateway_type"),
        SearchField.set(name="Region", key="data.region"),
        SearchField.set(name="Network", key="data.network"),
        SearchField.set(name="Status", key="data.status"),
        SearchField.set(name="Router Name", key="data.router_name"),
        SearchField.set(name="Project", key="data.project"),
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
    CloudServiceTypeResponse({"resource": cst_vpc_gateway}),
]
