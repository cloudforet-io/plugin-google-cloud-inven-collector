from schematics.types import ModelType, StringType, PolyModelType
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta
from spaceone.inventory.model.pub_sub.subscription.data import Subscription

subscription = ItemDynamicLayout.set_fields('Subscription', fields=[])
subscription_meta = CloudServiceMeta.set_layouts([])


class PubSubResource(CloudServiceResource):
    cloud_service_group = StringType(default='PubSub')


class SubscriptionResource(PubSubResource):
    cloud_service_type = StringType(default='Subscription')
    data = ModelType(Subscription)
    _metadata = ModelType(CloudServiceMeta, default=subscription_meta, serialized_name='metadata')


class SubscriptionResponse(CloudServiceResponse):
    resource = PolyModelType(SubscriptionResource)
