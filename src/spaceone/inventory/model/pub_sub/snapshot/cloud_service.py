from schematics.types import ModelType, StringType, PolyModelType
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta
from spaceone.inventory.model.pub_sub.snapshot.data import PubSubSnapshot

pub_sub_snapshot = ItemDynamicLayout.set_fields('Snapshot', fields=[])
pub_sub_snapshot_meta = CloudServiceMeta.set_layouts([])


class PubSubResource(CloudServiceResource):
    cloud_service_group = StringType(default='PubSub')


class PubSubSnapshotResource(PubSubResource):
    cloud_service_type = StringType(default='Snapshot')
    data = ModelType(PubSubSnapshot)
    _metadata = ModelType(CloudServiceMeta, default=pub_sub_snapshot_meta, serialized_name='metadata')


class PubSubSnapshotResponse(CloudServiceResponse):
    resource = PolyModelType(PubSubSnapshotResource)
