from schematics.types import ModelType, StringType, PolyModelType

from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, ListDynamicLayout
from spaceone.inventory.model.pub_sub.subscription.data import Subscription

subscription_detail = ItemDynamicLayout.set_fields('Subscription Details', fields=[])
subscription_detail_meta = ListDynamicLayout.set_layouts('Details', layouts=[subscription_detail])
subscription_meta = CloudServiceMeta.set_layouts([subscription_detail_meta])


class PubSubResource(CloudServiceResource):
    cloud_service_group = StringType(default='PubSub')


class SubscriptionResource(PubSubResource):
    cloud_service_type = StringType(default='Subscription')
    data = ModelType(Subscription)
    _metadata = ModelType(CloudServiceMeta, default=subscription_meta, serialized_name='metadata')


class SubscriptionResponse(CloudServiceResponse):
    resource = PolyModelType(SubscriptionResource)
