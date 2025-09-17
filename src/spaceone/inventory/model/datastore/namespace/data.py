from schematics.types import IntType, ListType, StringType

from spaceone.inventory.libs.schema.cloud_service import BaseResource

"""
Datastore Namespace Data 모델 정의

Google Cloud Datastore Namespace의 상세 데이터를 표현하기 위한 schematics 모델입니다.
"""


class DatastoreNamespaceData(BaseResource):
    """Datastore Namespace data model"""

    namespace_id = StringType()
    display_name = StringType()
    kinds = ListType(StringType())
    kind_count = IntType()
    database_id = StringType()

    def reference(self):
        # database_id is "(default)" then convert to "-default-"
        url_database_id = (
            "-default-" if self.database_id == "(default)" else self.database_id
        )

        # namespace_id is "(default)" then convert to "__$DEFAULT$__"
        url_namespace_id = (
            "__$DEFAULT$__" if self.namespace_id == "(default)" else self.namespace_id
        )

        return {
            "resource_id": f"https://datastore.googleapis.com/v1/projects/{self.project}:runQuery (POST)",
            "external_link": f"https://console.cloud.google.com/datastore/databases/{url_database_id}/entities;ns={url_namespace_id}/query/kind?project={self.project}",
        }
