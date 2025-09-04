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


class WorkerPoolSpec(Model):
    network_config = BaseType(deserialize_from="networkConfig")
    worker_config = BaseType(deserialize_from="workerConfig")


class WorkerPoolStatus(Model):
    observed_generation = IntType(deserialize_from="observedGeneration")
    conditions = BaseType()  # 복잡한 조건 배열


class WorkerPoolV1(Model):
    api_version = StringType(deserialize_from="apiVersion")
    kind = StringType()
    metadata = ModelType(ObjectMeta)
    spec = ModelType(WorkerPoolSpec)
    status = ModelType(WorkerPoolStatus)
    
    # Additional fields
    name = StringType()
    project = StringType()
    location = StringType()
    region = StringType()
    
    # Revision info (populated by manager)
    revisions = BaseType(default=[])
    revision_count = IntType(default=0)
