from schematics import Model
from schematics.types import (
    DictType,
    ModelType,
    StringType,
)

from spaceone.inventory.libs.schema.google_cloud_logging import (
    GoogleCloudLoggingModel,
)


class Repository(Model):
    name = StringType()
    full_name = StringType()
    repository_name = StringType()
    remote_uri = StringType(deserialize_from="remoteUri")
    create_time = StringType(deserialize_from="createTime")
    update_time = StringType(deserialize_from="updateTime")
    annotations = DictType(StringType, default={})
    etag = StringType()
    connection = StringType()
    # Logging data
    google_cloud_logging = ModelType(GoogleCloudLoggingModel, serialize_when_none=False)
