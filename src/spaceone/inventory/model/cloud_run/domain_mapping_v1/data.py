from schematics import Model
from schematics.types import (
    DateTimeType,
    IntType,
    ModelType,
    StringType,
)


class Condition(Model):
    type = StringType()
    status = StringType()
    reason = StringType()
    message = StringType()
    last_transition_time = DateTimeType(deserialize_from="lastTransitionTime")


class DomainMappingMetadata(Model):
    name = StringType()
    namespace = StringType()
    uid = StringType()
    creation_timestamp = DateTimeType(deserialize_from="creationTimestamp")
    cluster_name = StringType(deserialize_from="clusterName")


class DomainMappingSpec(Model):
    route_name = StringType(deserialize_from="routeName")
    certificate_mode = StringType(deserialize_from="certificateMode")


class DomainMappingStatus(Model):
    conditions = ModelType(Condition)
    observed_generation = IntType(deserialize_from="observedGeneration")
    url = StringType()


class DomainMapping(Model):
    api_version = StringType(deserialize_from="apiVersion")
    kind = StringType()
    metadata = ModelType(DomainMappingMetadata)
    spec = ModelType(DomainMappingSpec)
    status = ModelType(DomainMappingStatus)
