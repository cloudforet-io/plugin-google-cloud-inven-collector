from schematics import Model
from schematics.types import ModelType, ListType, StringType, DictType

from spaceone.inventory.libs.schema.cloud_service import BaseResource
from spaceone.inventory.model.cloud_functions.function_gen2.inner_data import *

__all__ = ['FunctionGen2']


class Variable(Model):
    key = StringType(serialize_when_none=False)
    value = StringType(serialize_when_none=False)


class Source(Model):
    file_name = StringType(serialize_when_none=False)
    content = StringType(serialize_when_none=False)
    output_display = StringType(serialize_when_none=False, default='show')


class FunctionDisplay(Model):
    state = StringType(serialize_when_none=False)
    region = StringType(serialize_when_none=False)
    environment_lowercase = StringType(serialize_when_none=False)
    environment = StringType(serialize_when_none=False)
    function_id = StringType(serialize_when_none=False)
    last_deployed = StringType(serialize_when_none=False)
    trigger = StringType(serialize_when_none=False)
    runtime = StringType(serialize_when_none=False)
    timeout = StringType(serialize_when_none=False)
    executed_function = StringType(serialize_when_none=False)
    memory_allocated = StringType(serialize_when_none=False)
    vpc_connector_egress_settings = StringType(serialize_when_none=False)
    ingress_settings = StringType(serialize_when_none=False)
    source_location = StringType(serialize_when_none=False)
    source_code = ListType(ModelType(Source), serialize_when_none=False)
    trigger_name = StringType(serialize_when_none=False)
    event_provider = StringType(serialize_when_none=False)
    retry_policy = StringType(serialize_when_none=False)
    runtime_environment_variables = ListType(ModelType(Variable), serialize_when_none=False)
    build_environment_variables = ListType(ModelType(Variable), serialize_when_none=False)


class FunctionGen2(BaseResource):
    name = StringType()
    environment = StringType(choices=('ENVIRONMENT_UNSPECIFIED', 'GEN_1', 'GEN_2'), serialize_when_none=False)
    description = StringType(serialize_when_none=False)
    build_config = ModelType(BuildConfig, serialize_when_none=False, deserialize_from='buildConfig')
    service_config = ModelType(ServiceConfig, serialize_when_none=False, deserialize_from='serviceConfig')
    event_trigger = ModelType(EventTrigger, serialize_when_none=False, deserialize_from='eventTrigger')
    state = StringType(choices=('STATE_UNSPECIFIED', 'ACTIVE', 'FAILED', 'DEPLOYING', 'DELETING', 'UNKNOWN'),
                       serialize_when_none=False)
    update_time = StringType(serialize_when_none=False, deserialize_from='updateTime')
    labels = DictType(StringType, serialize_when_none=False)
    state_messages = ListType(ModelType(StateMessage), serialize_when_none=False, deserialize_from='stateMessages')

    display = ModelType(FunctionDisplay, serialize_when_none=False)

    def reference(self):
        return {
            "resource_id": self.name,
            "external_link": f"https://console.cloud.google.com/functions/details/{self.display.region}/{self.display.function_id}?env={self.display.environment_lowercase}&project={self.project}"
        }
