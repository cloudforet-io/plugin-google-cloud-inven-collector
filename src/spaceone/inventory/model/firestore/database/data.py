from schematics import Model
from schematics.types import (
    DateTimeType,
    StringType,
)

__all__ = ["Database"]


class Database(Model):
    # 기본 정보
    id = StringType(required=True)
    name = StringType(required=True)
    project_id = StringType(required=True)
    location_id = StringType()
    uid = StringType()

    # 데이터베이스 설정
    type = StringType(choices=["FIRESTORE_NATIVE", "DATASTORE_MODE"])
    concurrency_mode = StringType(choices=["OPTIMISTIC", "PESSIMISTIC"])
    app_engine_integration_mode = StringType(
        choices=["ENABLED", "DISABLED"], default="DISABLED"
    )

    # 시간 정보
    create_time = DateTimeType()
    update_time = DateTimeType()
    earliest_version_time = DateTimeType()

    # 보안 및 백업
    version_retention_period = StringType()  # "3600s" 형태
    point_in_time_recovery_enablement = StringType(
        choices=[
            "POINT_IN_TIME_RECOVERY_ENABLED",
            "POINT_IN_TIME_RECOVERY_DISABLED",
        ]
    )
    delete_protection_state = StringType(
        choices=["DELETE_PROTECTION_ENABLED", "DELETE_PROTECTION_DISABLED"]
    )

    # 메타데이터
    etag = StringType()
    key_prefix = StringType()

    def reference(self):
        return {
            "resource_id": self.name,
            "external_link": f"https://console.cloud.google.com/firestore/databases/{self.id}?project={self.project_id}",
        }
