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


class ServiceSpec(Model):
    template = BaseType()  # RevisionTemplate - 복잡한 중첩 구조
    traffic = BaseType()   # Traffic 배열


class ServiceStatus(Model):
    observed_generation = IntType(deserialize_from="observedGeneration")
    conditions = BaseType()  # 복잡한 조건 배열
    latest_created_revision_name = StringType(deserialize_from="latestCreatedRevisionName")
    latest_ready_revision_name = StringType(deserialize_from="latestReadyRevisionName")
    url = StringType()
    address = BaseType()   # 주소 객체
    traffic = BaseType()   # Traffic 배열


class ServiceV1(Model):
    api_version = StringType(deserialize_from="apiVersion")
    kind = StringType()
    metadata = ModelType(ObjectMeta)
    spec = ModelType(ServiceSpec)
    status = ModelType(ServiceStatus)
    
    # Additional fields
    name = StringType()
    project = StringType()
    location = StringType()
    region = StringType()
    
    # Revision info (populated by manager)
    revisions = BaseType(default=[])
    revision_count = IntType(default=0)
