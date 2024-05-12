from schematics import Model
from schematics.types import (
    ModelType,
    ListType,
    StringType,
    IntType,
    BooleanType,
    DictType,
)

__all__ = ["ServiceConfig"]


class SecretEnvVar(Model):
    key = StringType(serialize_when_none=False)
    project_id = StringType(serialize_when_none=False, deserialize_from="projectId")
    secret = StringType(serialize_when_none=False)
    version = StringType(serialize_when_none=False)


class SecretVersion(Model):
    version = StringType(serialize_when_none=False)
    path = StringType(serialize_when_none=False)


class SecretVolume(Model):
    mount_path = StringType(serialize_when_none=False, deserialize_from="mountPath")
    project_id = StringType(serialize_when_none=False, deserialize_from="projectId")
    secret = StringType(serialize_when_none=False)
    versions = ListType(ModelType(SecretVersion, serialize_when_none=False))


class ServiceConfig(Model):
    service = StringType(serialize_when_none=False)
    timeout_seconds = IntType(
        serialize_when_none=False, deserialize_from="timeoutSeconds"
    )
    available_memory = StringType(
        serialize_when_none=False, deserialize_from="availableMemory"
    )
    environment_variables = DictType(
        StringType, serialize_when_none=False, deserialize_from="environmentVariables"
    )
    max_instance_count = IntType(
        serialize_when_none=False, deserialize_from="maxInstanceCount"
    )
    min_instance_count = IntType(
        serialize_when_none=False, deserialize_from="minInstanceCount", default=0
    )
    vpc_connector = StringType(
        serialize_when_none=False, deserialize_from="vpcConnector"
    )
    vpc_connector_egress_settings = StringType(
        choices=(
            "VPC_CONNECTOR_EGRESS_SETTINGS_UNSPECIFIED",
            "PRIVATE_RANGES_ONLY",
            "ALL_TRAFFIC",
        ),
        serialize_when_none=False,
        deserialize_from="vpcConnectorEgressSettings",
    )
    ingress_settings = StringType(
        choices=(
            "INGRESS_SETTINGS_UNSPECIFIED",
            "ALLOW_ALL",
            "ALLOW_INTERNAL_ONLY",
            "ALLOW_INTERNAL_AND_GCLB",
        ),
        serialize_when_none=False,
        deserialize_from="ingressSettings",
    )
    uri = StringType(serialize_when_none=False)
    service_account_email = StringType(
        serialize_when_none=False, deserialize_from="serviceAccountEmail"
    )
    all_traffic_on_latest_revision = BooleanType(
        serialize_when_none=False, deserialize_from="allTrafficOnLatestRevision"
    )
    secret_environment_variables = ListType(
        ModelType(
            SecretEnvVar,
            serialize_when_none=False,
            deserialize_from="secretEnvironmentVariables",
        )
    )
    secret_volumes = ListType(
        ModelType(
            SecretVolume, serialize_when_none=False, deserialize_from="secretVolumes"
        )
    )
    revision = StringType(serialize_when_none=False)
