from schematics import Model
from schematics.types import DictType, IntType, ListType, ModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import BaseResource

"""
Datastore Index Data 모델 정의

Google Cloud Datastore Index의 상세 데이터를 표현하기 위한 schematics 모델입니다.
"""


class IndexProperty(Model):
    """Index Property 정보 모델"""

    name = StringType()
    direction = StringType()


class DatastoreIndexData(BaseResource):
    """Datastore Index 데이터 모델"""

    index_id = StringType()
    kind = StringType()
    ancestor = StringType()
    state = StringType()
    properties = ListType(ModelType(IndexProperty))
    property_count = IntType()
    sorted_properties = ListType(StringType())
    unsorted_properties = ListType(StringType())
    project_id = StringType()
    display_name = StringType()
    raw_data = DictType(StringType)

    def reference(self):
        return {
            "resource_id": f"{self.project_id}:{self.index_id}",
            "external_link": f"https://console.cloud.google.com/datastore/indexes?project={self.project_id}",
        }
