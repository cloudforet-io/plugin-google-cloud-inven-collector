from schematics.types import DictType, ListType, StringType

from spaceone.inventory.libs.schema.cloud_service import BaseResource

"""
Filestore Snapshot Data 모델 정의

Google Cloud Filestore 스냅샷의 상세 데이터를 표현하기 위한 schematics 모델입니다.
"""


class FilestoreSnapshotData(BaseResource):
    """Filestore 스냅샷 데이터 모델"""

    snapshot_id = StringType()
    full_name = StringType()  # full path name
    state = StringType()
    description = StringType(serialize_when_none=False)
    location = StringType()

    instance_id = StringType()  # parent instance id

    labels = ListType(DictType(StringType), default=[])

    create_time = StringType(deserialize_from="createTime")

    def reference(self):
        return {
            "resource_id": f"https://file.googleapis.com/v1/{self.full_name}",
            "external_link": f"https://console.cloud.google.com/filestore/instances/locations/{self.location}/id/{self.instance_id}/snapshots/snapshotId/{self.snapshot_id}?project={self.project}",
        }
