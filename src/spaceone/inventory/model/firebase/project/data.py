from schematics import Model
from schematics.types import DictType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
)

"""
Firebase Project Data Model
"""


class Project(Model):
    project_id = StringType(deserialize_from="projectId")
    display_name = StringType(deserialize_from="displayName")
    project_number = StringType(deserialize_from="projectNumber")
    resources = DictType(StringType)
    state = StringType()
    etag = StringType()
    name = StringType()

    def reference(self):
        return {
            "resource_id": self.project_id,
            "external_link": f"https://console.firebase.google.com/project/{self.project_id}",
        }


# Firebase Project 메타데이터 레이아웃
firebase_project_meta = CloudServiceMeta.set_layouts(
    layouts=[
        ItemDynamicLayout.set_fields(
            "Project Info",
            fields=[
                TextDyField.data_source("Project ID", "data.project_id"),
                TextDyField.data_source("Display Name", "data.display_name"),
                TextDyField.data_source("Project Number", "data.project_number"),
                TextDyField.data_source("State", "data.state"),
                TextDyField.data_source("Name", "data.name"),
                TextDyField.data_source("ETag", "data.etag"),
            ],
        ),
        ItemDynamicLayout.set_fields(
            "Resources",
            fields=[
                TextDyField.data_source("Hosting Site", "data.resources.hostingSite"),
                TextDyField.data_source(
                    "Realtime Database Instance",
                    "data.resources.realtimeDatabaseInstance",
                ),
                TextDyField.data_source(
                    "Storage Bucket", "data.resources.storageBucket"
                ),
                TextDyField.data_source("Location ID", "data.resources.locationId"),
            ],
        ),
    ]
)
