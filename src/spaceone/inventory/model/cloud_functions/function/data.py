from schematics import Model
from schematics.types import ModelType, ListType, StringType, IntType, BooleanType, DictType

from spaceone.inventory.libs.schema.cloud_service import BaseResource
from spaceone.inventory.model.cloud_functions.function.data import *

__all__ = ['Function']


class FunctionDisplay(Model):
    environment_lowercase = StringType(serialize_when_none=False)  # TODO: make lowercase of environment in manager (it will be used external_link)


class Function(BaseResource):
    name = StringType(serialize_when_none=False)
    environment = StringType(choices=('ENVIRONMENT_UNSPECIFIED', 'GEN_1', 'GEN_2'), serialize_when_none=False)
    description = StringType(serialize_when_none=False)
    build_config = ModelType(BuildConfig, serialize_when_none=False, deserialize_from='buildConfig')
    service_config = ModelType(ServiceConfig, serialize_when_none=False, deserialize_from='serviceConfig')
    event_trigger = ModelType(EventTrigger, serialize_when_none=False, deserialize_from='eventTrigger')
    state = StringType(choices=('STATE_UNSPECIFIED', 'ACTIVE', 'FAILED', 'DEPLOYING', 'DELETING', 'UNKNOWN'),
                       serialize_when_none=False)
    update_time = StringType(serialize_when_none=False, deserialize_from='updateTime')
    labels = DictType(StringType, serialize_when_none=False)
    state_messages = ListType(StateMessage, serialize_when_none=False, deserialize_from='stateMessages')

    display = ModelType(FunctionDisplay, serialize_when_none=False)

    def reference(self):
        return {
            "resource_id": self.name,
            "external_link": f"https://console.cloud.google.com/functions/details/{self.region}/{self.id}?env={self.display.environment_lowercase}&project={self.project}"
        }
