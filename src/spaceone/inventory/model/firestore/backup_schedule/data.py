from schematics import Model
from schematics.types import (
    DateTimeType,
    StringType,
)

__all__ = ["BackupSchedule"]


class BackupSchedule(Model):
    # 기본 정보
    name = StringType(required=True)
    database_id = StringType(required=True)
    project_id = StringType(required=True)

    # 백업 설정
    retention = StringType()  # "604800s" 형태의 보존 기간

    # 스케줄 설정 (DailyRecurrence 또는 WeeklyRecurrence)
    recurrence_type = StringType(choices=["DAILY", "WEEKLY"])

    # 시간 정보
    create_time = DateTimeType()
    update_time = DateTimeType()

    # 메타데이터
    uid = StringType()

    def reference(self):
        return {
            "resource_id": self.name,
            "external_link": f"https://console.cloud.google.com/firestore/databases/{self.database_id}/backup-schedules?project={self.project_id}",
        }
