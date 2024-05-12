from schematics.types import PolyModelType

from spaceone.inventory.model.networking.firewall.data import *
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    TextDyField,
    EnumDyField,
    ListDyField,
    DateTimeDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    TableDynamicLayout,
)
from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceResource,
    CloudServiceResponse,
    CloudServiceMeta,
)

"""
Firewall
"""

# TAB - Firewall
firewall_detail_meta = ItemDynamicLayout.set_fields(
    "Firewall Details",
    fields=[
        TextDyField.data_source("ID", "data.id"),
        TextDyField.data_source("Name", "data.name"),
        EnumDyField.data_source(
            "Logs",
            "data.display.logs",
            default_badge={"indigo.500": ["On"], "coral.600": ["Off"]},
        ),
        TextDyField.data_source("Priority", "data.priority"),
        TextDyField.data_source("Direction", "data.display.direction_display"),
        EnumDyField.data_source(
            "Action On Match",
            "data.display.action",
            default_badge={"indigo.500": ["Allow"], "coral.600": ["Deny"]},
        ),
        ListDyField.data_source("Source Filter", "data.source_ranges"),
        ListDyField.data_source("Protocols and ports", "data.display.protocols_port"),
        # TextDyField.data_source('Insights', 'data.network_tier_display'),
        DateTimeDyField.data_source("Creation Time", "data.creation_timestamp"),
    ],
)

# instance_template_meta_disk
firewall_applicable_inst_meta = TableDynamicLayout.set_fields(
    "Applicable to Instances",
    root_path="data.applicable_instance",
    fields=[
        TextDyField.data_source("Name", "name"),
        TextDyField.data_source("Subnetwork", "subnetwork"),
        TextDyField.data_source("Internal IP", "address"),
        ListDyField.data_source(
            "Tags", "tags", default_badge={"type": "outline", "delimiter": "<br>"}
        ),
        ListDyField.data_source("Service Accounts", "service_accounts"),
        TextDyField.data_source("Project", "project"),
        ListDyField.data_source(
            "Label",
            "labels_display",
            default_badge={"type": "outline", "delimiter": "<br>"},
        ),
        DateTimeDyField.data_source("Creation Time", "creation_timestamp"),
    ],
)

instance_template_meta = CloudServiceMeta.set_layouts(
    [firewall_detail_meta, firewall_applicable_inst_meta]
)


class VPCResource(CloudServiceResource):
    cloud_service_group = StringType(default="Networking")


class FirewallResource(VPCResource):
    cloud_service_type = StringType(default="Firewall")
    data = ModelType(Firewall)
    _metadata = ModelType(
        CloudServiceMeta, default=instance_template_meta, serialized_name="metadata"
    )


class FirewallResponse(CloudServiceResponse):
    resource = PolyModelType(FirewallResource)
