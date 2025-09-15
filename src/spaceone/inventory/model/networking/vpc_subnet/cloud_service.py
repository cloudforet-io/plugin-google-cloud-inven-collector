from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse
from spaceone.inventory.libs.schema.base import ReferenceModel

from .data import VPCSubnet

__all__ = ["VPCSubnetResource", "VPCSubnetResponse"]


class VPCSubnetResource(CloudServiceResource):
    cloud_service_group = "Networking"
    cloud_service_type = "VPCSubnet"


class VPCSubnetResponse(CloudServiceResponse):
    resource = VPCSubnetResource
