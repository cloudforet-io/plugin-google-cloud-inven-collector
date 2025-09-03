from schematics import Model
from schematics.types import IntType, ListType, ModelType, StringType

__all__ = ["FirestoreCollection", "DocumentInfo"]


class DocumentInfo(Model):
    """컬렉션 내 문서 정보"""

    id = StringType(required=True)
    name = StringType()  # 전체 문서 경로
    fields_summary = StringType()  # 문서 필드 정보를 문자열로 요약
    create_time = StringType()
    update_time = StringType()


class FirestoreCollection(Model):
    # 기본 정보
    collection_id = StringType(required=True)
    database_id = StringType(required=True)
    project_id = StringType(required=True)
    collection_path = StringType(required=True)  # 컬렉션 전체 경로

    # 포함된 문서들 - ModelType 패턴으로 복원하되 serialize_when_none=False 추가
    documents = ListType(ModelType(DocumentInfo), default=[], serialize_when_none=False)
    document_count = IntType(default=0)

    # 메타데이터
    depth_level = IntType(default=0)  # 0: 최상위, 1: 하위 컬렉션
    parent_document_path = StringType()  # 하위 컬렉션인 경우 부모 문서 경로

    def reference(self):
        return {
            "resource_id": f"projects/{self.project_id}/databases/{self.database_id}/documents/{self.collection_path}",
            "external_link": f"https://console.cloud.google.com/firestore/databases/{self.database_id}/data/~2F{self.collection_path}?project={self.project_id}",
        }
