from schematics import Model
from schematics.types import ModelType, StringType, IntType, BooleanType, DictType

from spaceone.inventory.libs.schema.cloud_service import BaseResource


class RetryPolicy(Model):
    description = StringType(serialize_when_none=False)
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


class Display(Model):
    delivery_type = StringType(serialize_when_none=False)
    retention_duration = StringType(serialize_when_none=False)
    ttl = StringType(serialize_when_none=False)
    subscription_expiration = StringType(serialize_when_none=False)
    ack_deadline_seconds = StringType(serialize_when_none=False)
    message_ordering = StringType(serialize_when_none=False)
    exactly_once_delivery = StringType(serialize_when_none=False)
    attachment = StringType(serialize_when_none=False)
    retain_acked_messages = StringType(serialize_when_none=False)
    retry_policy = ModelType(RetryPolicy, serialize_when_none=False)


class Subscription(BaseResource):
    topic = StringType(serialize_when_none=False)
    display = ModelType(Display, serialize_when_none=False)
    push_config = ModelType(PushConfig, serialize_when_none=False, deserialize_from='pushConfig')
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
    state = StringType(choices=('STATE_UNSPECIFIED', 'ACTIVE', 'RESOURCE_ERROR'))

    def reference(self):
        return {
            "resource_id": self.self_link,
            "external_link": f"https://console.cloud.google.com/cloudpubsub/subscription/detail/{self.id}?project={self.project}"
        }
