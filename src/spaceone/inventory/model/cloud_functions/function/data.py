from schematics import Model
from schematics.types import ModelType, ListType, StringType, IntType, BooleanType, DictType

from spaceone.inventory.libs.schema.cloud_service import BaseResource


class Function(BaseResource):
    pass

    def reference(self):
        return {
            "resource_id": '',  # TODO write unique key
            "external_link": f"https://console.cloud.google.com/cloudpubsub/topic/detail/{self.topic_id}?project={self.project}"
        }
