from schematics import Model
from schematics.types import (
    DateTimeType,
    DictType,
    IntType,
    ListType,
    ModelType,
    StringType,
)


class Condition(Model):
    type = StringType()
    state = StringType()
    message = StringType()
    last_transition_time = DateTimeType(deserialize_from="lastTransitionTime")
    severity = StringType()
    revision_reason = StringType(deserialize_from="revisionReason")


class Revision(Model):
    name = StringType()
    uid = StringType()
    service = StringType()
    generation = StringType()
    create_time = DateTimeType(deserialize_from="createTime")
    update_time = DateTimeType(deserialize_from="updateTime")
    conditions = ListType(ModelType(Condition), default=[])


class WorkerPool(Model):
    name = StringType()
    uid = StringType()
    generation = IntType()
    labels = DictType(StringType, default={})
    annotations = DictType(StringType, default={})
    create_time = DateTimeType(deserialize_from="createTime")
    update_time = DateTimeType(deserialize_from="updateTime")
    delete_time = DateTimeType(deserialize_from="deleteTime")
    expire_time = DateTimeType(deserialize_from="expireTime")
    creator = StringType()
    last_modifier = StringType(deserialize_from="lastModifier")
    client = StringType()
    launch_stage = StringType(deserialize_from="launchStage")
    observed_generation = IntType(deserialize_from="observedGeneration")
    terminal_condition = ModelType(Condition, deserialize_from="terminalCondition")
    conditions = ListType(ModelType(Condition), default=[])
    etag = StringType()
    revisions = ListType(ModelType(Revision), default=[])
    revision_count = IntType(default=0)
