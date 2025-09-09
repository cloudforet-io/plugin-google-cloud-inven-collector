from schematics.types import StringType

from spaceone.inventory.libs.schema.cloud_service import BaseResource


class DatastoreDatabaseData(BaseResource):
    """Datastore Database 데이터 모델"""

    # 기본 정보 - API 응답 필드들
    database_id = StringType()  # 데이터베이스 ID (projects/{project}/databases/{database_id}에서 추출)
    uid = StringType()  # 시스템 할당 고유 식별자
    location_id = StringType(deserialize_from="locationId")  # 위치 ID (예: nam5, eur3)
    type = StringType()  # 데이터베이스 유형 (DATASTORE_MODE, FIRESTORE_NATIVE)
    concurrency_mode = StringType(deserialize_from="concurrencyMode")  # 동시성 제어 모드

    # 시간 정보
    create_time = StringType(deserialize_from="createTime")  # 생성 시간
    update_time = StringType(deserialize_from="updateTime")  # 업데이트 시간

    # 메타데이터
    etag = StringType()  # ETag
    
    # 추가 처리된 필드들
    project_id = StringType()  # 프로젝트 ID (매니저에서 추가)
    display_name = StringType()  # 표시 이름 (매니저에서 생성)

    def reference(self):
        return {
            "resource_id": self.name,
            "external_link": f"https://console.cloud.google.com/datastore/databases?project={self.project_id}",
        }
