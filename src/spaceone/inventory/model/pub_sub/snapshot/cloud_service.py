from schematics.types import ModelType, StringType, PolyModelType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceResource,
    CloudServiceResponse,
    CloudServiceMeta,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    TextDyField,
    DateTimeDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout
from spaceone.inventory.model.pub_sub.snapshot.data import Snapshot

snapshot = ItemDynamicLayout.set_fields(
    "Snapshot",
    fields=[
        TextDyField.data_source("Snapshot ID", "data.id"),
        TextDyField.data_source("Topic name", "data.topic"),
        DateTimeDyField.data_source("Expiration", "data.expire_time"),
        TextDyField.data_source(
            "Project", "data.project", options={"is_optional": True}
        ),
    ],
)
snapshot_meta = CloudServiceMeta.set_layouts([snapshot])


class PubSubResource(CloudServiceResource):
    cloud_service_group = StringType(default="PubSub")


class SnapshotResource(PubSubResource):
    cloud_service_type = StringType(default="Snapshot")
    data = ModelType(Snapshot)
    _metadata = ModelType(
        CloudServiceMeta, default=snapshot_meta, serialized_name="metadata"
    )


class SnapshotResponse(CloudServiceResponse):
    resource = PolyModelType(SnapshotResource)
