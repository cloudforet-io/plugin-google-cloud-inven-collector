from schematics import Model
from schematics.types import ModelType, ListType, StringType, IntType, DateTimeType, BooleanType, FloatType, DictType
from spaceone.inventory.libs.schema.cloud_service import BaseResource


class Subscription(Model):
    subscription_id = StringType()
    subscription_name = StringType()
    project = StringType()


class Snapshot(Model):
    snapshot_id = StringType()
    snapshot_name = StringType()
    project = StringType()


class Topic(BaseResource):
    encryption_key = StringType(choices=('Google-managed', 'Customer-managed'))
    schema_name = StringType(default='')
    message_encoding = StringType(default='')
    labels = DictType(StringType, default={})
    retention_duration = StringType(default='')
    subscriptions = ListType(ModelType(Subscription))
    snapshots = ListType(ModelType(Snapshot))

