from schematics.types import (
    StringType,
)

from spaceone.inventory.libs.schema.cloud_service import BaseResource

__all__ = ["Backup"]


class Backup(BaseResource):
    full_name = StringType()
    database_id = StringType()
    database_uid = StringType(deserialize_from="databaseUid")

    state = StringType()

    snapshot_time = StringType(deserialize_from="snapshotTime")
    expire_time = StringType(deserialize_from="expireTime")

    def reference(self):
        return {
            "resource_id": f"https://firestore.googleapis.com/v1/{self.full_name}",
            "external_link": f"https://console.cloud.google.com/firestore/databases/{self.database_id}/disaster-recovery?project={self.project}",
        }
