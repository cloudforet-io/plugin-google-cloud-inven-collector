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
    project_id = StringType()
    created_time = StringType()

    def reference(self):
        return {
            "resource_id": f"{self.project_id}:{self.namespace_id}",
            "external_link": f"https://console.cloud.google.com/datastore/entities;kind=__namespace__;ns={self.namespace_id}/query/kind?project={self.project_id}",
        }
