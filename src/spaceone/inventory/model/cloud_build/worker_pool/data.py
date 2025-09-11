from schematics import Model
from schematics.types import (
    BaseType,
    DictType,
    StringType,
)


class WorkerPool(Model):
    name = StringType()
    full_name = StringType()
    uid = StringType()
    annotations = DictType(StringType, default={})
    create_time = StringType(deserialize_from="createTime")
    update_time = StringType(deserialize_from="updateTime")
    delete_time = StringType(deserialize_from="deleteTime")
    state = StringType()
    private_pool_v1_config = DictType(
        BaseType, deserialize_from="privatePoolV1Config", default={}
    )
    disk_size_display = StringType()  # GB 단위로 표시
    etag = StringType()
