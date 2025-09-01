from schematics import Model
from schematics.types import (
    DateTimeType,
    DictType,
    FloatType,
    ListType,
    ModelType,
    PolyModelType,
    StringType,
)

from spaceone.inventory.libs.schema.google_cloud_logging import GoogleCloudLoggingModel
from spaceone.inventory.libs.schema.google_cloud_monitoring import (
    GoogleCloudMonitoringModel,
)
from spaceone.inventory.libs.schema.region import RegionResource
from spaceone.inventory.model.compute_engine.instance.data import NIC, Disk, VMInstance

from .base import (
    BaseMetaData,
    BaseResponse,
    MetaDataView,
    MetaDataViewSubData,
    ReferenceModel,
)


class Labels(Model):
    key = StringType()
    value = StringType()


class CloudServiceMeta(BaseMetaData):
    @classmethod
    def set(cls):
        sub_data = MetaDataViewSubData()
        return cls({"view": MetaDataView({"sub_data": sub_data})})

    @classmethod
    def set_layouts(cls, layouts=[]):
        sub_data = MetaDataViewSubData({"layouts": layouts})
        return cls({"view": MetaDataView({"sub_data": sub_data})})


class ServerMetadata(Model):
    view = ModelType(MetaDataView)

    @classmethod
    def set_layouts(cls, layouts=[]):
        sub_data = MetaDataViewSubData({"layouts": layouts})
        return cls({"view": MetaDataView({"sub_data": sub_data})})


class BaseResource(Model):
    id = StringType(serialize_when_none=False)
    name = StringType(serialize_when_none=False)
    project = StringType(serialize_when_none=False)
    region = StringType(serialize_when_none=False)
    self_link = StringType(deserialize_from="selfLink", serialize_when_none=False)
    google_cloud_monitoring = ModelType(
        GoogleCloudMonitoringModel, serialize_when_none=False
    )
    google_cloud_logging = ModelType(GoogleCloudLoggingModel, serialize_when_none=False)


class CloudServiceResource(Model):
    provider = StringType(default="google_cloud")
    account = StringType()
    ip_addresses = ListType(StringType())
    instance_type = StringType(serialize_when_none=False)
    instance_size = FloatType(serialize_when_none=False)
    launched_at = DateTimeType(serialize_when_none=False)
    cloud_service_type = StringType()
    cloud_service_group = StringType()
    name = StringType(default="")
    region_code = StringType()
    data = PolyModelType(Model, default=lambda: {})
    tags = ListType(ModelType(Labels), serialize_when_none=False)
    reference = ModelType(ReferenceModel)
    _metadata = PolyModelType(
        CloudServiceMeta, serialize_when_none=False, serialized_name="metadata"
    )


class CloudServiceResponse(BaseResponse):
    match_rules = DictType(
        ListType(StringType),
        default={
            "1": [
                "reference.resource_id",
                "provider",
                "cloud_service_type",
                "cloud_service_group",
            ]
        },
    )
    resource_type = StringType(default="inventory.CloudService")
    resource = PolyModelType(CloudServiceResource)


class ErrorResource(Model):
    resource_type = StringType(default="inventory.CloudService")
    provider = StringType(default="google_cloud")
    cloud_service_group = StringType(default="ComputeEngine", serialize_when_none=False)
    cloud_service_type = StringType(default="Instance", serialize_when_none=False)
    resource_id = StringType(serialize_when_none=False)


class ErrorResourceResponse(CloudServiceResponse):
    state = StringType(default="FAILURE")
    resource_type = StringType(default="inventory.ErrorResource")
    resource = ModelType(ErrorResource, default={})

    @classmethod
    def create_with_logging(
        cls,
        error_message: str = "",
        error_code: str = "UNKNOWN_ERROR",
        resource_type: str = "inventory.ErrorResource",
        additional_data: dict = None,
    ) -> "ErrorResourceResponse":
        """
        로깅과 함께 ErrorResourceResponse 인스턴스를 생성합니다.

        Args:
            error_message: 에러 메시지
            error_code: 에러 코드
            resource_type: 리소스 타입
            additional_data: 추가 데이터

        Returns:
            ErrorResourceResponse 인스턴스
        """
        import logging

        _error_logger = logging.getLogger(__name__)

        # 에러 로깅
        _error_logger.error(
            f"Response state: FAILURE, resource_type: {resource_type}, "
            f"error_code: {error_code}, message: {error_message}"
        )

        # 에러 리소스 데이터 생성
        error_resource_data = {
            "provider": "google_cloud",
            "account": "",
            "error_message": error_message,
        }

        if additional_data:
            error_resource_data.update(additional_data)

        error_resource = ErrorResource(error_resource_data)

        return cls(
            {
                "state": "FAILURE",
                "resource_type": resource_type,
                "resource": error_resource,
            }
        )


class VMInstanceResource(Model):
    server_type = StringType(default="VM")
    os_type = StringType(choices=("LINUX", "WINDOWS"))
    primary_ip_address = StringType()
    ip_addresses = ListType(StringType())
    nics = ListType(ModelType(NIC))
    disks = ListType(ModelType(Disk))
    provider = StringType(default="google_cloud")
    cloud_service_type = StringType(default="Instance")
    cloud_service_group = StringType(default="ComputeEngine")
    name = StringType()
    account = StringType()
    instance_type = StringType(serialize_when_none=False)
    instance_size = StringType(serialize_when_none=False)
    launched_at = StringType(serialize_when_none=False)
    region_code = StringType()
    data = ModelType(VMInstance)
    tags = ListType(ModelType(Labels))
    reference = ModelType(ReferenceModel)
    _metadata = ModelType(ServerMetadata, serialized_name="metadata")


class RegionResourceResponse(BaseResponse):
    state = StringType(default="SUCCESS")
    resource_type = StringType(default="inventory.Region")
    match_rules = DictType(
        ListType(StringType), default={"1": ["region_code", "provider"]}
    )
    resource = PolyModelType(RegionResource)
