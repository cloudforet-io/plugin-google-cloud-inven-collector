from schematics.types import ModelType, PolyModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.model.batch.job.data import (
    BatchJobResource,
    batch_job_meta,
)

"""
Batch Job Cloud Service Models - Job 개별 리소스 관리
"""


class BatchGroupResource(CloudServiceResource):
    """Batch 서비스 그룹 기본 리소스"""
    
    cloud_service_group = StringType(default="Batch")


class JobResource(BatchGroupResource):
    """Batch Job 리소스 - 개별 Job을 하나의 리소스로 관리"""
    
    cloud_service_type = StringType(default="Job")
    data = ModelType(BatchJobResource)
    _metadata = ModelType(
        CloudServiceMeta,
        default=batch_job_meta,
        serialized_name="metadata",
    )


class JobResponse(CloudServiceResponse):
    """Batch Job 응답 모델"""
    
    resource = PolyModelType(JobResource)
