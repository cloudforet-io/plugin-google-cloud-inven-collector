from schematics.types import ModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.model.filestore.snapshot.data import FilestoreSnapshotData

"""
Filestore Snapshot Cloud Service 모델 정의

SpaceONE의 Cloud Service 형태로 Filestore 스냅샷 리소스를 표현하기 위한 모델입니다.
"""


class FilestoreSnapshotResource(CloudServiceResource):
    """Filestore 스냅샷 리소스 모델"""

    cloud_service_type = StringType(default="Snapshot")
    cloud_service_group = StringType(default="Filestore")
    data = ModelType(FilestoreSnapshotData)


class FilestoreSnapshotResponse(CloudServiceResponse):
    """Filestore 스냅샷 응답 모델"""

    resource = ModelType(FilestoreSnapshotResource)
