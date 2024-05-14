from schematics import Model
from schematics.types import (
    ModelType,
    ListType,
    StringType,
    DictType,
    IntType,
    FloatType,
)

from spaceone.inventory.libs.schema.cloud_service import BaseResource
from spaceone.inventory.model.cloud_functions.function_gen1.inner_data.sub_data import *

__all__ = ["FunctionGen1"]


class Variable(Model):
    key = StringType(serialize_when_none=False)
    value = StringType(serialize_when_none=False)


class FunctionDisplay(Model):
    state = StringType(serialize_when_none=False)
    region = StringType(serialize_when_none=False)
    environment_lowercase = StringType(serialize_when_none=False)
    environment = StringType(serialize_when_none=False)
    function_id = StringType(serialize_when_none=False)
    last_deployed = StringType(serialize_when_none=False)
    runtime = StringType(serialize_when_none=False)
    timeout = StringType(serialize_when_none=False)
    executed_function = StringType(serialize_when_none=False)
    memory_allocated = StringType(serialize_when_none=False)
    ingress_settings = StringType(serialize_when_none=False)
    vpc_connector_egress_settings = StringType(serialize_when_none=False)
    trigger = StringType(serialize_when_none=False)
    event_provider = StringType(serialize_when_none=False)
    http_url = StringType(serialize_when_none=False)
    runtime_environment_variables = ListType(
        ModelType(Variable), serialize_when_none=False
    )
    build_environment_variables = ListType(
        ModelType(Variable), serialize_when_none=False
    )


class FunctionGen1(BaseResource):
    name = StringType()
    description = StringType(serialize_when_none=False)
    status = StringType(
        choices=(
            "CLOUD_FUNCTION_STATUS_UNSPECIFIED",
            "ACTIVE",
            "OFFLINE",
            "DEPLOY_IN_PROGRESS",
            "DELETE_IN_PROGRESS",
            "UNKNOWN",
        ),
        serialize_when_none=False,
    )
    entry_point = StringType(serialize_when_none=False, deserialize_from="entryPoint")
    runtime = StringType(serialize_when_none=False)
    timeout = StringType(serialize_when_none=False)
    available_memory_mb = IntType(
        serialize_when_none=False, deserialize_from="availableMemoryMb"
    )
    service_account_email = StringType(
        serialize_when_none=False, deserialize_from="serviceAccountEmail"
    )
    update_time = StringType(serialize_when_none=False, deserialize_from="updateTime")
    version_id = StringType(serialize_when_none=False, deserialize_from="versionId")
    labels = DictType(StringType, serialize_when_none=False)
    environment_variables = DictType(
        StringType, serialize_when_none=False, deserialize_from="environmentVariables"
    )
    build_environment_variables = DictType(
        StringType,
        serialize_when_none=False,
        deserialize_from="buildEnvironmentVariables",
    )
    network = StringType(serialize_when_none=False)
    max_instances = IntType(
        serialize_when_none=False, deserialize_from="maxInstances", default=0
    )
    min_instances = IntType(
        serialize_when_none=False, deserialize_from="minInstances", default=0
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
    kms_key_name = StringType(serialize_when_none=False, deserialize_from="kmsKeyName")
    build_worker_pool = StringType(
        serialize_when_none=False, deserialize_from="buildWorkerPool"
    )
    build_id = StringType(serialize_when_none=False, deserialize_from="buildId")
    build_name = StringType(serialize_when_none=False, deserialize_from="buildName")
    secret_environment_variables = ListType(
        ModelType(SecretEnvVar),
        serialize_when_none=False,
        deserialize_from="secretEnvironmentVariables",
    )
    secret_volumes = ListType(
        ModelType(SecretVolume),
        serialize_when_none=False,
        deserialize_from="secretVolumes",
    )
    source_token = StringType(serialize_when_none=False, deserialize_from="sourceToken")
    docker_repository = StringType(
        serialize_when_none=False, deserialize_from="dockerRepository"
    )
    docker_registry = StringType(
        choices=(
            "DOCKER_REGISTRY_UNSPECIFIED",
            "CONTAINER_REGISTRY",
            "ARTIFACT_REGISTRY",
        ),
        serialize_when_none=False,
        deserialize_from="dockerRegistry",
    )
    source_archive_url = StringType(
        serialize_when_none=False, deserialize_from="sourceArchiveUrl"
    )
    source_repository = ModelType(
        SourceRepository, serialize_when_none=False, deserialize_from="sourceRepository"
    )
    source_upload_url = StringType(
        serialize_when_none=False, deserialize_from="sourceUploadUrl"
    )
    https_trigger = ModelType(
        HttpsTrigger, serialize_when_none=False, deserialize_from="httpsTrigger"
    )
    event_trigger = ModelType(
        EventTrigger, serialize_when_none=False, deserialize_from="eventTrigger"
    )
    display = ModelType(FunctionDisplay, serialize_when_none=False)

    def reference(self):
        return {
            "resource_id": self.name,
            "external_link": f"https://console.cloud.google.com/functions/details/{self.display.region}/{self.display.function_id}?env={self.display.environment_lowercase}&project={self.project}",
        }
