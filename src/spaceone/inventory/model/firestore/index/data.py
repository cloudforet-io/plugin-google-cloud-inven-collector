from schematics import Model
from schematics.types import StringType

__all__ = ["FirestoreIndex"]


class FirestoreIndex(Model):
    # 기본 정보
    name = StringType(required=True)
    database_id = StringType(required=True)
    project_id = StringType(required=True)

    # 인덱스 설정
    query_scope = StringType(choices=["COLLECTION", "COLLECTION_GROUP"])
    api_scope = StringType(choices=["ANY_API", "DATASTORE_MODE_API"])
    state = StringType(choices=["CREATING", "READY", "ERROR"])
    density = StringType()  # SPARSE_ALL, DENSE_ALL 등

    # 인덱스 구성 (GCP 내부 필드 제외) - 문자열로 단순화
    fields_summary = StringType()  # 필드 정보를 문자열로 요약

    # 메타데이터
    collection_group = StringType()  # 인덱스가 적용되는 컬렉션 그룹

    def reference(self):
        return {
            "resource_id": self.name,
            "external_link": f"https://console.cloud.google.com/firestore/databases/{self.database_id}/indexes?project={self.project_id}",
        }

    @staticmethod
    def filter_internal_fields(fields):
        """GCP 내부 필드(__로 시작하는 필드) 제거"""
        filtered_fields = []
        for field in fields:
            field_path = field.get("fieldPath", "")
            if not field_path.startswith("__"):
                filtered_fields.append(field)
        return filtered_fields
