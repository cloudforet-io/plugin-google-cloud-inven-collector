from schematics import Model
from schematics.types import (
    BaseType,
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


class TrafficTarget(Model):
    type = StringType()  # TrafficTargetAllocationType enum
    revision = StringType()
    percent = IntType()
    tag = StringType()


class Revision(Model):
    name = StringType()
    uid = StringType()
    service = StringType()
    generation = StringType()
    create_time = DateTimeType(deserialize_from="createTime")
    update_time = DateTimeType(deserialize_from="updateTime")
    conditions = ListType(ModelType(Condition), default=[])


class Service(Model):
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
    traffic = ListType(ModelType(TrafficTarget), default=[])
    urls = ListType(StringType, default=[])
    observed_generation = IntType(deserialize_from="observedGeneration")
    terminal_condition = ModelType(Condition, deserialize_from="terminalCondition")
    conditions = ListType(ModelType(Condition), default=[])
    latest_ready_revision_name = StringType(deserialize_from="latestReadyRevisionName")
    latest_created_revision_name = StringType(
        deserialize_from="latestCreatedRevisionName"
    )
    traffic_statuses = ListType(
        DictType(BaseType), deserialize_from="trafficStatuses", default=[]
    )
    uri = StringType()
    etag = StringType()
    template = DictType(BaseType, default={})
    ingress = StringType()
    revisions = ListType(ModelType(Revision), default=[])
    revision_count = IntType(default=0)
