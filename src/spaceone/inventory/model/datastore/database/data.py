from schematics.types import StringType

from spaceone.inventory.libs.schema.cloud_service import BaseResource


class DatastoreDatabaseData(BaseResource):
    """Datastore Database 데이터 모델"""

    # 기본 정보
    name = StringType()  # 전체 리소스 이름 (projects/{project}/databases/{database_id})
    database_id = StringType()  # 데이터베이스 ID
    uid = StringType()  # 시스템 할당 고유 식별자
    location_id = StringType()  # 위치 ID (예: nam5, eur3)
    type = StringType()  # 데이터베이스 유형 (DATASTORE_MODE, FIRESTORE_NATIVE)
    concurrency_mode = StringType()  # 동시성 제어 모드

    # 시간 정보
    create_time = StringType()  # 생성 시간
    update_time = StringType()  # 업데이트 시간

    # 메타데이터
    etag = StringType()  # ETag
    project_id = StringType()  # 프로젝트 ID
    display_name = StringType()  # 표시 이름

    def reference(self):
        return {
            "resource_id": self.name,
            "external_link": f"https://console.cloud.google.com/datastore/databases?project={self.project_id}",
        }
