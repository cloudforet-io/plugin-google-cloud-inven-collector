from schematics import Model
from schematics.types import (
    BaseType,
    DictType,
    StringType,
)


class WorkerPool(Model):
    name = StringType()
    display_name = StringType(deserialize_from="displayName")
    uid = StringType()
    annotations = DictType(StringType, default={})
    create_time = StringType(deserialize_from="createTime")
    update_time = StringType(deserialize_from="updateTime")
    delete_time = StringType(deserialize_from="deleteTime")
    state = StringType()
    private_pool_v1_config = DictType(
        BaseType, deserialize_from="privatePoolV1Config", default={}
    )
    etag = StringType()
