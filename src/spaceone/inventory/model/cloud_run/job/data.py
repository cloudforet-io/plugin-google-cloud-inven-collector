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


class Task(Model):
    name = StringType()
    uid = StringType()
    job = StringType()
    execution = StringType()


class Execution(Model):
    name = StringType()
    uid = StringType()
    creator = StringType()
    job = StringType()
    tasks = ListType(ModelType(Task), default=[])
    task_count = IntType(default=0)


class LatestCreatedExecution(Model):
    name = StringType()
    create_time = DateTimeType(deserialize_from="createTime")
    completion_time = DateTimeType(deserialize_from="completionTime")
    completion_status = StringType(deserialize_from="completionStatus")


class Job(Model):
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
    executions = ListType(ModelType(Execution), default=[])
    execution_count = IntType(default=0)
    latest_created_execution = ModelType(
        LatestCreatedExecution, deserialize_from="latestCreatedExecution"
    )
