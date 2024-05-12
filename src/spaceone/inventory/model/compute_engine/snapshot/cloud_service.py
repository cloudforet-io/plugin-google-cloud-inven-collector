from schematics.types import PolyModelType

from spaceone.inventory.model.compute_engine.snapshot.data import *
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    TextDyField,
    DateTimeDyField,
    EnumDyField,
    ListDyField,
    SizeField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    TableDynamicLayout,
)
from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceResource,
    CloudServiceResponse,
    CloudServiceMeta,
)

"""
Snapshot
"""

# TAB - Snapshot
# snapshot details
snapshot_instance_meta = ItemDynamicLayout.set_fields(
    "Snapshot Details",
    fields=[
        TextDyField.data_source("Source Disk", "data.disk.source_disk_display"),
        SizeField.data_source("Disk Size", "data.disk.disk_size"),
        SizeField.data_source("SnapShot Size", "data.disk.storage_bytes"),
        ListDyField.data_source(
            "Locations",
            "data.storage_locations",
            default_badge={"type": "outline", "delimiter": "<br>"},
        ),
        DateTimeDyField.data_source("Creation Time", "data.creation_timestamp"),
        EnumDyField.data_source(
            "Encryption Type",
            "data.encryption",
            default_badge={
                "primary": ["Google managed"],
                "indigo.500": ["Customer managed"],
                "coral.600": ["Customer supplied"],
            },
        ),
    ],
)


snapshot_labels_meta = TableDynamicLayout.set_fields(
    "Labels",
    root_path="data.labels",
    fields=[
        TextDyField.data_source("Key", "key"),
        TextDyField.data_source("Value", "value"),
    ],
)


instance_template_meta = CloudServiceMeta.set_layouts(
    [snapshot_instance_meta, snapshot_labels_meta]
)


class ComputeEngineResource(CloudServiceResource):
    cloud_service_group = StringType(default="ComputeEngine")


class SnapshotResource(ComputeEngineResource):
    cloud_service_type = StringType(default="Snapshot")
    data = ModelType(Snapshot)
    _metadata = ModelType(
        CloudServiceMeta, default=instance_template_meta, serialized_name="metadata"
    )


class SnapshotResponse(CloudServiceResponse):
    resource = PolyModelType(SnapshotResource)
