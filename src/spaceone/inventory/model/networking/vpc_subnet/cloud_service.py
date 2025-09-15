from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse
from spaceone.inventory.libs.schema.base import ReferenceModel

from .data import VPCSubnet

__all__ = ["VPCSubnetResource", "VPCSubnetResponse"]


class VPCSubnetResource(CloudServiceResource):
    cloud_service_group = "Networking"
    cloud_service_type = "VPCSubnet"


class VPCSubnetResponse(CloudServiceResponse):
    resource = VPCSubnetResource
    
    @classmethod
    def create_with_logging(
        cls,
        state: str = "SUCCESS",
        resource_type: str = "inventory.CloudService",
        message: str = "",
        resource=None,
        match_rules: dict = None,
    ):
        """
        v2.0 로깅 시스템을 사용하여 VPCSubnetResponse를 생성합니다.
        """
        # BaseResponse의 create_with_logging 메서드 활용
        base_response = super().create_with_logging(
            state=state,
            resource_type=resource_type,
            message=message,
            resource=resource,
            match_rules=match_rules,
        )
        return base_response