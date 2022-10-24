from schematics.types import StringType

from spaceone.inventory.libs.schema.cloud_service import BaseResource


class Schema(BaseResource):
    name = StringType(serialize_when_none=False)
    schema_type = StringType(choices=['TYPE_UNSPECIFIED', 'PROTOCOL_BUFFER', 'AVRO'], serialize_when_none=False)
    definition = StringType(serialize_when_none=False)
    revision_id = StringType(serialize_when_none=False, deserialize_from='revisionId')
    revision_create_time = StringType(serialize_when_none=False, deserialize_from='revisionCreateTime')

    def reference(self):
        return {
            "resource_id": self.id,
            "external_link": f"https://console.cloud.google.com/cloudpubsub/schema/detail/{self.id}?project={self.project}"
        }


"""
{
  "name": string,
  "type": enum (Type),
  "definition": string,
  "revisionId": string,
  "revisionCreateTime": string
}
"""
