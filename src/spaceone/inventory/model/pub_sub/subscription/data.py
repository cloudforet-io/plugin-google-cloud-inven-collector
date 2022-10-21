from schematics import Model
from schematics.types import ModelType, StringType, IntType, BooleanType, DictType


class RetryPolicy(Model):
    minimum_backoff = StringType(serialize_when_none=False, deserialize_from='minimumBackoff')
    maximum_backoff = StringType(serialize_when_none=False, deserialize_from='maximumBackoff')


class DeadLetterPolicy(Model):
    dead_letter_topic = StringType(serialize_when_none=False, deserialize_from='deadLetterTopic')
    max_delivery_attempts = IntType(serialize_when_none=False, deserialize_from='maxDeliveryAttempts')


class BigQueryConfig(Model):
    table = StringType(serialize_when_none=False)
    use_topic_schema = BooleanType(serialize_when_none=False, deserialize_from='useTopicSchema')
    write_metadata = BooleanType(serialize_when_none=False, deserialize_from='writeMetadata')
    drop_unknown_fields = BooleanType(serialize_when_none=False, deserialize_from='dropUnknownFields')
    state = StringType(choices=('STATE_UNSPECIFIED', 'ACTIVE', 'PERMISSION_DENIED', 'NOT_FOUND', 'SCHEMA_MISMATCH'),
                       serialize_when_none=False)


class OidcToken(Model):
    service_account_email = StringType(serialize_when_none=False, deserialize_from='serviceAccountEmail')
    audience = StringType(serialize_when_none=False)


class PushConfig(Model):
    push_endpoint = StringType(serialize_when_none=False, deserialize_from='pushEndpoint')
    attributes = DictType(StringType, serialize_when_none=False)
    oidc_token = ModelType(OidcToken, serialize_when_none=False, deserialize_from='oidcToken')


class Subscription(Model):
    name = StringType()
    topic = StringType(serialize_when_none=False)
    delivery_type = StringType(serialize_when_none=False)
    push_config = ModelType(PushConfig, deserialize_from='pushConfig')
    bigquery_config = ModelType(BigQueryConfig, serialize_when_none=False, deserialize_from='bigqueryConfig')
    ack_deadline_seconds = IntType(serialize_when_none=False, deserialize_from='ackDeadlineSeconds')
    retain_acked_messages = BooleanType(serialize_when_none=False, deserialize_from='retainAckedMessages')
    message_retention_duration = StringType(serialize_when_none=False, deserialize_from='messageRetentionDuration')
    labels = DictType(StringType, serialize_when_none=False)
    enable_message_ordering = BooleanType(serialize_when_none=False, deserialize_from='enableMessageOrdering')
    expiration_policy = DictType(StringType, serialize_when_none=False, deserialize_from='expirationPolicy')
    filter = StringType(serialize_when_none=False)
    dead_letter_policy = ModelType(DeadLetterPolicy, serialize_when_none=False, deserialize_from='deadLetterPolicy')
    retry_policy = ModelType(RetryPolicy, serialize_when_none=False, deserialize_from='retryPolicy')
    detached = BooleanType(serialize_when_none=False)
    enable_exactly_once_delivery = BooleanType(serialize_when_none=False, deserialize_from='enableExactlyOnceDelivery')
    topic_message_retention_duration = StringType(serialize_when_none=False,
                                                  deserialize_from='topicMassageRetentionDuration')
    state = StringType(choices=('STATE_UNSPECIFIED', 'ACTIVE', 'RESOURCE_ERROR'))
