from schematics import Model
from schematics.types import ModelType, ListType, StringType

__all__ = [
    "SecretEnvVar",
    "SecretVolume",
    "SourceRepository",
    "HttpsTrigger",
    "EventTrigger",
]


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
    versions = ListType(ModelType(SecretVersion), serialize_when_none=False)


class SourceRepository(Model):
    url = StringType(serialize_when_none=False)
    deployed_url = StringType(serialize_when_none=False, deserialize_from="deployedUrl")


class HttpsTrigger(Model):
    url = StringType(serialize_when_none=False)
    security_level = StringType(
        choices=("SECURITY_LEVEL_UNSPECIFIED", "SECURE_ALWAYS", "SECURE_OPTIONAL"),
        serialize_when_none=False,
        deserialize_from="securityLevel",
    )


# TODO: have to verify actual results
class Retry(Model):
    pass


class FailurePolicy(Model):
    retry = ModelType(Retry, serialize_when_none=False)


class EventTrigger(Model):
    event_type = StringType(serialize_when_none=False, deserialize_from="eventType")
    resource = StringType(serialize_when_none=False)
    service = StringType(serialize_when_none=False)
    failure_policy = ModelType(
        FailurePolicy, serialize_when_none=False, deserialize_from="failurePolicy"
    )
