from schematics import Model
from schematics.types import (
    DateTimeType,
    IntType,
    StringType,
)

__all__ = ["Backup"]


class Backup(Model):
    # 기본 정보
    name = StringType(required=True)
    database = StringType(required=True)  # 원본 데이터베이스 경로
    project_id = StringType(required=True)
    location_id = StringType(required=True)

    # 백업 상태
    state = StringType(choices=["CREATING", "READY", "NOT_AVAILABLE"])

    # 시간 정보
    create_time = DateTimeType()
    expire_time = DateTimeType()
    version_time = DateTimeType()  # 백업된 데이터의 시점

    # 백업 크기 및 통계
    size_bytes = IntType()

    # 메타데이터
    uid = StringType()

    def reference(self):
        backup_id = self.name.split("/")[-1] if "/" in self.name else self.name
        return {
            "resource_id": self.name,
            "external_link": f"https://console.cloud.google.com/firestore/locations/{self.location_id}/backups/{backup_id}?project={self.project_id}",
        }
