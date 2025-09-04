from schematics import Model
from schematics.types import (
    BaseType,
    DateTimeType,
    DictType,
    IntType,
    ModelType,
    StringType,
)


class ObjectMeta(Model):
    name = StringType()
    namespace = StringType()
    uid = StringType()
    resource_version = StringType(deserialize_from="resourceVersion")
    generation = IntType()
    creation_timestamp = DateTimeType(deserialize_from="creationTimestamp")
    labels = DictType(StringType)
    annotations = DictType(StringType)


class JobSpec(Model):
    template = BaseType()  # ExecutionTemplate - 모든 중첩 구조를 BaseType으로 처리


class JobStatus(Model):
    observed_generation = IntType(deserialize_from="observedGeneration")
    conditions = BaseType()  # 복잡한 조건 배열
    execution_count = IntType(deserialize_from="executionCount")
    latest_created_execution = BaseType(deserialize_from="latestCreatedExecution")


class JobV1(Model):
    api_version = StringType(deserialize_from="apiVersion")
    kind = StringType()
    metadata = ModelType(ObjectMeta)
    spec = BaseType()  # 전체 spec을 BaseType으로 처리하여 복잡한 중첩 구조 문제 해결
    status = BaseType()  # 전체 status를 BaseType으로 처리하여 복잡한 중첩 구조 문제 해결
    
    # Additional fields
    name = StringType()
    project = StringType()
    location = StringType()
    region = StringType()
    
    # Execution info (populated by manager)
    executions = BaseType(default=[])
    execution_count = IntType(default=0)
