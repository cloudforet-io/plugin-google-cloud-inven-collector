from schematics import Model
from schematics.types import IntType, ListType, ModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import BaseResource

"""
Datastore Index Data 모델 정의

Google Cloud Datastore Index의 상세 데이터를 표현하기 위한 schematics 모델입니다.
"""


class IndexProperty(Model):
    """Index Property information model"""

    name = StringType()
    direction = StringType()


class DatastoreIndexData(BaseResource):
    """Datastore Index data model"""

    index_id = StringType(deserialize_from="indexId")
    kind = StringType()
    ancestor = StringType()
    state = StringType()
    properties = ListType(ModelType(IndexProperty))

    property_count = IntType()
    sorted_properties = ListType(StringType())
    unsorted_properties = ListType(StringType())

    def reference(self):
        return {
            "resource_id": f"https://datastore.googleapis.com/v1/projects/{self.project}",
            "external_link": f"https://console.cloud.google.com/datastore/indexes?project={self.project}",
        }
