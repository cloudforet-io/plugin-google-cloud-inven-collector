from schematics import Model
from schematics.types import ModelType, ListType, StringType, IntType, BooleanType, DictType

__all__ = ['EventTrigger']


class EventFilter(Model):
    attribute = StringType(serialize_when_none=False)
    value = StringType(serialize_when_none=False)
    operator = StringType(serialize_when_none=False)


class EventTrigger(Model):
    trigger = StringType(serialize_when_none=False)
    trigger_region = StringType(serialize_when_none=False, deserialize_from='triggerRegion')
    event_type = StringType(serialize_when_none=False, deserialize_from='eventType')
    event_filters = ListType(ModelType(EventFilter, serialize_when_none=False, deserialize_from='eventFilters'))
    pubsub_topic = StringType(serialize_when_none=False, deserialize_from='pubsubTopic')
    service_account_email = StringType(serialize_when_none=False, deserialize_from='serviceAccountEmail')
    retry_policy = StringType(choices=('RETRY_POLICY_UNSPECIFIED', 'RETRY_POLICY_DO_NOT_RETRY', 'RETRY_POLICY_RETRY'),
                              serialize_when_none=False, deserialize_from='retryPolicy')
    channel = StringType(serialize_when_none=False)
