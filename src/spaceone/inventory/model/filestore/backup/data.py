from schematics.types import DictType, ListType, StringType

from spaceone.inventory.libs.schema.cloud_service import BaseResource

"""
Filestore Backup Data 모델 정의

Google Cloud Filestore 백업의 상세 데이터를 표현하기 위한 schematics 모델입니다.
"""


class FilestoreBackupData(BaseResource):
    """Filestore 백업 데이터 모델"""

    full_name = StringType()
    backup_id = StringType()
    description = StringType(serialize_when_none=False)
    state = StringType()
    create_time = StringType(deserialize_from="createTime")

    labels = ListType(DictType(StringType), default=[])
    capacity_gb = StringType(deserialize_from="capacityGb", serialize_when_none=False)
    storage_bytes = StringType(
        deserialize_from="storageBytes", serialize_when_none=False
    )
    source_instance = StringType(serialize_when_none=False)
    source_instance_id = StringType(serialize_when_none=False)
    source_file_share = StringType(
        deserialize_from="sourceFileShare", serialize_when_none=False
    )
    source_instance_tier = StringType(
        deserialize_from="sourceInstanceTier", serialize_when_none=False
    )
    download_bytes = StringType(
        deserialize_from="downloadBytes", serialize_when_none=False
    )
    kms_key = StringType(deserialize_from="kmsKey", serialize_when_none=False)
    file_system_protocol = StringType(
        deserialize_from="fileSystemProtocol", serialize_when_none=False
    )

    location = StringType()

    def reference(self):
        return {
            "resource_id": f"https://file.googleapis.com/v1/{self.full_name}",
            "external_link": f"https://console.cloud.google.com/filestore/backups/locations/{self.location}/id/{self.backup_id}?project={self.project}",
        }
