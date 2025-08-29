from schematics.types import IntType, ListType, StringType

from spaceone.inventory.libs.schema.cloud_service import BaseResource

"""
Datastore Namespace Data 모델 정의

Google Cloud Datastore Namespace의 상세 데이터를 표현하기 위한 schematics 모델입니다.
"""


class DatastoreNamespaceData(BaseResource):
    """Datastore Namespace 데이터 모델"""

    namespace_id = StringType()
    display_name = StringType()
    kinds = ListType(StringType())
    kind_count = IntType()
    database_id = StringType()  # 데이터베이스 ID 추가
    project_id = StringType()
    created_time = StringType()

    def reference(self):
        # 데이터베이스 name 구성 (projects/{project_id}/databases/{database_id})
        database_name = (
            f"projects/{self.project_id}/databases/{self.database_id}"
            if self.database_id != "(default)"
            else f"projects/{self.project_id}/databases/(default)"
        )

        # database_id가 "(default)"인 경우 "-default-"로 변환
        url_database_id = (
            "-default-" if self.database_id == "(default)" else self.database_id
        )

        # namespace_id가 "(default)"인 경우 "__$DEFAULT$__"로 변환
        url_namespace_id = (
            "__$DEFAULT$__" if self.namespace_id == "(default)" else self.namespace_id
        )

        return {
            "resource_id": f"{database_name}:{self.namespace_id}",
            "external_link": f"https://console.cloud.google.com/datastore/databases/{url_database_id}/entities;ns={url_namespace_id}/query/kind?project={self.project_id}",
        }
