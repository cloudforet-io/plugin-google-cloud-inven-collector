from schematics.types import DictType, ListType, StringType

from spaceone.inventory.libs.schema.cloud_service import BaseResource

"""
Filestore Backup Data 모델 정의

Google Cloud Filestore 백업의 상세 데이터를 표현하기 위한 schematics 모델입니다.
"""


class FilestoreBackupData(BaseResource):
    """Filestore 백업 데이터 모델"""

    # 기본 정보
    full_name = StringType()  # reference 메서드용 전체 경로
    backup_id = StringType()
    state = StringType()
    description = StringType(serialize_when_none=False)
    location = StringType()

    # 백업 소스 정보
    source_instance = StringType(serialize_when_none=False)  # 소스 인스턴스 전체 경로
    source_file_share = StringType(serialize_when_none=False)  # 소스 파일 공유 이름

    # 용량 정보
    capacity_gb = StringType(serialize_when_none=False)  # 백업 용량 (GB)
    storage_bytes = StringType(serialize_when_none=False)  # 실제 저장 용량 (bytes)

    # 라벨 정보
    labels = ListType(DictType(StringType), default=[])

    # 시간 정보
    create_time = StringType(deserialize_from="createTime")

    def reference(self):
        return {
            "resource_id": f"https://file.googleapis.com/v1/{self.full_name}",
            "external_link": f"https://console.cloud.google.com/filestore/backups/locations/{self.location}/id/{self.backup_id}?project={self.project}",
        }
