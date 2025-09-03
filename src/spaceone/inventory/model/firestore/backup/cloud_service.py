from schematics.types import ModelType, PolyModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    DateTimeDyField,
    EnumDyField,
    SizeField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout
from spaceone.inventory.model.firestore.backup.data import Backup

"""
BACKUP
"""

backup_meta = CloudServiceMeta.set_layouts(
    [
        ItemDynamicLayout.set_fields(
            "Backup Information",
            fields=[
                TextDyField.data_source("Name", "data.name"),
                TextDyField.data_source("Location", "data.location_id"),
                TextDyField.data_source("Database", "data.database"),
                EnumDyField.data_source(
                    "State",
                    "data.state",
                    default_badge={
                        "green.500": ["READY"],
                        "yellow.500": ["CREATING"],
                        "red.500": ["NOT_AVAILABLE"],
                    },
                ),
                SizeField.data_source("Size", "data.size_bytes"),
                DateTimeDyField.data_source("Created", "data.create_time"),
                DateTimeDyField.data_source("Expires", "data.expire_time"),
                DateTimeDyField.data_source("Version Time", "data.version_time"),
                TextDyField.data_source("UID", "data.uid"),
            ],
        )
    ]
)


class BackupResource(CloudServiceResource):
    cloud_service_group = StringType(default="Firestore")
    cloud_service_type = StringType(default="Backup")
    data = ModelType(Backup)
    _metadata = ModelType(
        CloudServiceMeta, default=backup_meta, serialized_name="metadata"
    )


class BackupResponse(CloudServiceResponse):
    resource = PolyModelType(BackupResource)
