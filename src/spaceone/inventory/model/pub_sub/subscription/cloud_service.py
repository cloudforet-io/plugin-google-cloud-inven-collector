from schematics.types import ModelType, StringType, PolyModelType

from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta
from spaceone.inventory.libs.schema.metadata.dynamic_field import EnumDyField, TextDyField
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, ListDynamicLayout
from spaceone.inventory.model.pub_sub.subscription.data import Subscription

subscription_detail = ItemDynamicLayout.set_fields('Subscription Details', fields=[
    EnumDyField.data_source('Delivery type', 'data.display.delivery_type',
                            default_outline_badge=['Pull', 'Push', 'BigQuery']),
    TextDyField.data_source('Subscription expiration', 'data.display.subscription_expiration'),
    TextDyField.data_source('Acknowledgement deadline', 'data.display.ack_deadline_seconds'),
    TextDyField.data_source('Subscription filter', 'data.filter'),
    TextDyField.data_source('Subscription message retention duration', 'data.display.retention_duration'),
    TextDyField.data_source('Retain acknowledged messages', 'data.display.retain_acked_messages'),
    TextDyField.data_source('Exactly once delivery', 'data.display.exactly_once_delivery'),
    TextDyField.data_source('Message ordering', 'data.display.message_ordering'),
    TextDyField.data_source('Dead letter topic', 'data.dead_letter_policy.dead_letter_topic'),
    TextDyField.data_source('Maximum delivery attempts', 'data.dead_letter_policy.max_delivery_attempts'),
    TextDyField.data_source('Retry policy', 'data.display.retry_policy.description'),
    TextDyField.data_source('Minimum backoff duration', 'data.display.retry_policy.minimum_backoff'),
    TextDyField.data_source('Maximum backoff duration', 'data.display.retry_policy.maximum_backoff'),
])
subscription_detail_meta = ListDynamicLayout.set_layouts('Details', layouts=[subscription_detail])
subscription_meta = CloudServiceMeta.set_layouts([subscription_detail_meta])


class PubSubResource(CloudServiceResource):
    cloud_service_group = StringType(default='Pub/Sub')


class SubscriptionResource(PubSubResource):
    cloud_service_type = StringType(default='Subscription')
    data = ModelType(Subscription)
    _metadata = ModelType(CloudServiceMeta, default=subscription_meta, serialized_name='metadata')


class SubscriptionResponse(CloudServiceResponse):
    resource = PolyModelType(SubscriptionResource)
