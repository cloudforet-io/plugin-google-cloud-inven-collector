from schematics import Model
from schematics.types import (
    BaseType,
    BooleanType,
    DictType,
    ListType,
    StringType,
)


class Trigger(Model):
    id = StringType()
    name = StringType()
    description = StringType()
    tags = ListType(StringType, default=[])
    disabled = BooleanType(default=False)
    substitutions = DictType(BaseType, default={})
    filename = StringType()
    ignored_files = ListType(StringType, deserialize_from="ignoredFiles", default=[])
    included_files = ListType(StringType, deserialize_from="includedFiles", default=[])
    filter = StringType()
    trigger_template = DictType(
        BaseType, deserialize_from="triggerTemplate", default={}
    )
    github = DictType(BaseType, default={})
    pubsub_config = DictType(BaseType, deserialize_from="pubsubConfig", default={})
    webhook_config = DictType(BaseType, deserialize_from="webhookConfig", default={})
    repository_event_config = DictType(
        BaseType, deserialize_from="repositoryEventConfig", default={}
    )
    build = DictType(BaseType, default={})
    autodetect = BooleanType(default=False)
    create_time = StringType(
        deserialize_from="createTime"
    )  # DateTimeType 대신 StringType 사용
    service_account = StringType(deserialize_from="serviceAccount")
    source_to_build = DictType(BaseType, deserialize_from="sourceToBuild", default={})
    git_file_source = DictType(BaseType, deserialize_from="gitFileSource", default={})
    approval_config = DictType(BaseType, deserialize_from="approvalConfig", default={})
