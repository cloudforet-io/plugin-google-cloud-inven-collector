from schematics.types import DictType, ListType, StringType

from spaceone.inventory.libs.schema.cloud_service import BaseResource


class FilestoreSnapshotData(BaseResource):
    """Filestore Snapshot data model"""

    snapshot_id = StringType()
    full_name = StringType()
    state = StringType()
    description = StringType(serialize_when_none=False)
    location = StringType()

    instance_id = StringType()

    labels = ListType(DictType(StringType), default=[])

    create_time = StringType(deserialize_from="createTime")

    def reference(self):
        return {
            "resource_id": f"https://file.googleapis.com/v1/{self.full_name}",
            "external_link": f"https://console.cloud.google.com/filestore/instances/locations/{self.location}/id/{self.instance_id}/snapshots/snapshotId/{self.snapshot_id}?project={self.project}",
        }
