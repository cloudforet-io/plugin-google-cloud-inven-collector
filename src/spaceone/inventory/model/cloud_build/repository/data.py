from schematics import Model
from schematics.types import (
    DictType,
    StringType,
)


class Repository(Model):
    name = StringType()
    remote_uri = StringType(deserialize_from="remoteUri")
    create_time = StringType(deserialize_from="createTime")
    update_time = StringType(deserialize_from="updateTime")
    annotations = DictType(StringType, default={})
    etag = StringType()
    uid = StringType()
    webhook_id = StringType(deserialize_from="webhookId")
