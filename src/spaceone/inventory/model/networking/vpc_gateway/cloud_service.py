from schematics.types import ModelType, PolyModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.model.networking.vpc_gateway.data import VPCGateway

"""
VPC Gateway Cloud Service
"""


class VPCGatewayResource(CloudServiceResource):
    cloud_service_group = StringType(default="Networking")
    cloud_service_type = StringType(default="VPCGateway")
    data = ModelType(VPCGateway)
    _metadata = ModelType(CloudServiceMeta, serialize_when_none=False)


class VPCGatewayResponse(CloudServiceResponse):
    resource = PolyModelType(VPCGatewayResource)
