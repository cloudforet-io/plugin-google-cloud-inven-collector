from schematics.types import StringType
from spaceone.inventory.libs.schema.cloud_service import BaseResource

__all__ = ["Database"]


class Database(BaseResource):
    # BaseResource에서 상속되는 필드들:
    # id, name, project, region, self_link, google_cloud_monitoring, google_cloud_logging
    
    # Firestore 전용 필드들
    database_id = StringType(required=True)  # 원래 id 필드
    full_name = StringType(required=True)    # 원래 name 필드 (full resource name)
    project_id = StringType(required=True)   # 원래 project_id 필드
    location_id = StringType()               # 원래 location_id 필드
    uid = StringType()

    # 데이터베이스 설정
    type = StringType(choices=["FIRESTORE_NATIVE", "DATASTORE_MODE"])
    concurrency_mode = StringType(choices=["OPTIMISTIC", "PESSIMISTIC"])
    app_engine_integration_mode = StringType(
        choices=["ENABLED", "DISABLED"], default="DISABLED"
    )

    # 시간 정보
    create_time = StringType()
    update_time = StringType()
    earliest_version_time = StringType()

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
            "resource_id": self.full_name,
            "external_link": f"https://console.cloud.google.com/firestore/databases/{self.database_id}?project={self.project_id}",
        }
