from schematics.types import DictType, ListType, StringType

from spaceone.inventory.libs.schema.cloud_service import BaseResource

"""
Filestore Snapshot Data 모델 정의

Google Cloud Filestore 스냅샷의 상세 데이터를 표현하기 위한 schematics 모델입니다.
"""


class FilestoreSnapshotData(BaseResource):
    """Filestore 스냅샷 데이터 모델"""

    # 기본 정보
    full_name = StringType()  # reference 메서드용 전체 경로
    snapshot_id = StringType()
    state = StringType()
    description = StringType(serialize_when_none=False)
    location = StringType()

    # 인스턴스 관련 정보
    instance_name = StringType()  # 부모 인스턴스의 전체 이름
    instance_id = StringType()  # 부모 인스턴스의 ID

    # 라벨 정보
    labels = ListType(DictType(StringType), default=[])

    # 시간 정보
    create_time = StringType(deserialize_from="createTime")

    def reference(self):
        return {
            "resource_id": f"https://file.googleapis.com/v1/{self.full_name}",
            "external_link": f"https://console.cloud.google.com/filestore/snapshots/locations/{self.location}/id/{self.snapshot_id}?project={self.project}",
        }
