from schematics.types import (
    StringType,
)

from spaceone.inventory.libs.schema.cloud_service import BaseResource

__all__ = ["BackupSchedule"]


class BackupSchedule(BaseResource):
    full_name = StringType()
    database_id = StringType()

    retention = StringType()

    recurrence_type = StringType()
    weekly_day = StringType()

    create_time = StringType(deserialize_from="createTime")
    update_time = StringType(deserialize_from="updateTime")

    def reference(self):
        return {
            "resource_id": f"https://firestore.googleapis.com/v1/{self.full_name}",
            "external_link": f"https://console.cloud.google.com/firestore/databases/{self.database_id}/disaster-recovery?project={self.project}",
        }
