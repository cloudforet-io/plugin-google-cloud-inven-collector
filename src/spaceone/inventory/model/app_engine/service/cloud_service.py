from schematics.types import ModelType, PolyModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout
from spaceone.inventory.model.app_engine.service.data import AppEngineService

"""
AppEngine Service
"""
app_engine_service = ItemDynamicLayout.set_fields(
    "AppEngine Service",
    fields=[
        TextDyField.data_source("Service", "data.name"),
        TextDyField.data_source("Versions", "data.version_count"),
        TextDyField.data_source("Labels", "data.labels"),
        TextDyField.data_source("Ingress", "data.network.ingress_traffic_allowed"),
        TextDyField.data_source("VPC Access Name", "data.vpc_access_connector.name"),
        TextDyField.data_source(
            "VPC Egress Setting", "data.vpc_access_connector.egress_setting"
        ),
        TextDyField.data_source(
            "Last Version Deployed", "data.latest_version_deployed"
        ),
        TextDyField.data_source("Project ID", "data.project_id"),
        TextDyField.data_source("Service ID", "data.service_id"),
        TextDyField.data_source("Instance Count", "data.instance_count"),
    ],
)

traffic_split = ItemDynamicLayout.set_fields(
    "Traffic Split",
    fields=[
        TextDyField.data_source("Allocations", "data.split.allocations"),
        TextDyField.data_source("Shard By", "data.split.shardBy"),
    ],
)

network_settings = ItemDynamicLayout.set_fields(
    "Network Settings",
    fields=[
        TextDyField.data_source("Forwarded Ports", "data.network.forwarded_ports"),
        TextDyField.data_source("Instance Tag", "data.network.instance_tag"),
        TextDyField.data_source("Network Name", "data.network.name"),
        TextDyField.data_source("Subnetwork Name", "data.network.subnetwork_name"),
        TextDyField.data_source(
            "Ingress Traffic Allowed", "data.network.ingress_traffic_allowed"
        ),
    ],
)

vpc_access_connector = ItemDynamicLayout.set_fields(
    "VPC Access Connector",
    fields=[
        TextDyField.data_source("Name", "data.vpc_access_connector.name"),
        TextDyField.data_source(
            "Egress Setting", "data.vpc_access_connector.egress_setting"
        ),
    ],
)

app_engine_service_meta = CloudServiceMeta.set_layouts(
    [app_engine_service, traffic_split, network_settings, vpc_access_connector]
)


class AppEngineResource(CloudServiceResource):
    cloud_service_group = StringType(default="AppEngine")


class AppEngineServiceResource(AppEngineResource):
    cloud_service_type = StringType(default="Service")
    data = ModelType(AppEngineService)
    _metadata = ModelType(
        CloudServiceMeta, default=app_engine_service_meta, serialized_name="metadata"
    )


class AppEngineServiceResponse(CloudServiceResponse):
    resource = PolyModelType(AppEngineServiceResource)
