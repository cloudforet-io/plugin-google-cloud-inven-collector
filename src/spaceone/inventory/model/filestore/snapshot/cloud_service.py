from schematics.types import ModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    DateTimeDyField,
    EnumDyField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    TableDynamicLayout,
)
from spaceone.inventory.model.filestore.snapshot.data import FilestoreSnapshotData

# TAB - Snapshot Details
filestore_snapshot_details = ItemDynamicLayout.set_fields(
    "Snapshot Details",
    fields=[
        TextDyField.data_source("Snapshot ID", "data.snapshot_id"),
        TextDyField.data_source("Full Name", "data.full_name"),
        EnumDyField.data_source(
            "State",
            "data.state",
            default_state={
                "safe": ["READY"],
                "warning": ["CREATING", "DELETING"],
                "alert": ["STATE_UNSPECIFIED"],
            },
        ),
        TextDyField.data_source("Description", "data.description"),
        TextDyField.data_source("Instance ID", "data.instance_id"),
        DateTimeDyField.data_source("Created", "data.create_time"),
    ],
)

# TAB - Labels
filestore_snapshot_labels = TableDynamicLayout.set_fields(
    "Labels",
    root_path="data.labels",
    fields=[
        TextDyField.data_source("Key", "key"),
        TextDyField.data_source("Value", "value"),
    ],
)

filestore_snapshot_meta = CloudServiceMeta.set_layouts(
    [filestore_snapshot_details, filestore_snapshot_labels]
)


class FilestoreSnapshotResource(CloudServiceResource):
    cloud_service_type = StringType(default="Snapshot")
    cloud_service_group = StringType(default="Filestore")
    data = ModelType(FilestoreSnapshotData)
    _metadata = ModelType(
        CloudServiceMeta, default=filestore_snapshot_meta, serialized_name="metadata"
    )


class FilestoreSnapshotResponse(CloudServiceResponse):
    resource = ModelType(FilestoreSnapshotResource)
