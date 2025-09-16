from schematics.types import ModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.model.filestore.backup.data import FilestoreBackupData

"""
Filestore Backup Cloud Service 모델 정의

SpaceONE의 Cloud Service 형태로 Filestore 백업 리소스를 표현하기 위한 모델입니다.
"""


class FilestoreBackupResource(CloudServiceResource):
    """Filestore 백업 리소스 모델"""

    cloud_service_type = StringType(default="Backup")
    cloud_service_group = StringType(default="Filestore")
    data = ModelType(FilestoreBackupData)


class FilestoreBackupResponse(CloudServiceResponse):
    """Filestore 백업 응답 모델"""

    resource = ModelType(FilestoreBackupResource)
