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


class ConfigurationSpec(Model):
    template = BaseType()  # RevisionTemplate - 복잡한 중첩 구조


class ConfigurationStatus(Model):
    observed_generation = IntType(deserialize_from="observedGeneration")
    conditions = BaseType()  # 복잡한 조건 배열
    latest_created_revision_name = StringType(deserialize_from="latestCreatedRevisionName")
    latest_ready_revision_name = StringType(deserialize_from="latestReadyRevisionName")


class ConfigurationV1(Model):
    api_version = StringType(deserialize_from="apiVersion")
    kind = StringType()
    metadata = ModelType(ObjectMeta)
    spec = BaseType()  # 전체 spec을 BaseType으로 처리하여 복잡한 template 구조 문제 해결
    status = BaseType()  # 전체 status를 BaseType으로 처리하여 복잡한 조건 구조 문제 해결
    
    # Additional fields
    name = StringType()
    project = StringType()
    location = StringType()
    region = StringType()
