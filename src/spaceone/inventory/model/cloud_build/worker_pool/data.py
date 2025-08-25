from schematics import Model
from schematics.types import (
    DateTimeType,
    DictType,
    StringType,
)


class WorkerPool(Model):
    name = StringType()
    display_name = StringType(deserialize_from="displayName")
    uid = StringType()
    annotations = DictType(StringType, default={})
    create_time = DateTimeType(deserialize_from="createTime")
    update_time = DateTimeType(deserialize_from="updateTime")
    delete_time = DateTimeType(deserialize_from="deleteTime")
    state = StringType()
    private_pool_v1_config = DictType(StringType, deserialize_from="privatePoolV1Config", default={})
    etag = StringType()
