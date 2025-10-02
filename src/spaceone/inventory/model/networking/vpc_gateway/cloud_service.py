from schematics.types import ModelType, PolyModelType

from spaceone.inventory.libs.schema.base import BaseResponse
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
    cloud_service_group = "Networking"
    cloud_service_type = "VPCGateway"
    data = ModelType(VPCGateway)
    _metadata = ModelType(CloudServiceMeta, serialize_when_none=False)


class VPCGatewayResponse(CloudServiceResponse):
    resource = PolyModelType(VPCGatewayResource)

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
        v2.0 로깅 시스템을 사용하여 VPCGatewayResponse를 생성합니다.
        """
        # BaseResponse의 create_with_logging 메서드 활용
        base_response = BaseResponse.create_with_logging(
            state=state,
            resource_type=resource_type,
            message=message,
            resource=resource,
            match_rules=match_rules,
        )

        return base_response
