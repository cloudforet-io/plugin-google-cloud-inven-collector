from schematics.types import ModelType, PolyModelType, StringType

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
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout
from spaceone.inventory.model.firestore.backup_schedule.data import BackupSchedule

"""
BACKUP SCHEDULE
"""

backup_schedule_meta = CloudServiceMeta.set_layouts(
    [
        ItemDynamicLayout.set_fields(
            "Backup Schedule Information",
            fields=[
                TextDyField.data_source("Name", "data.name"),
                TextDyField.data_source("Database ID", "data.database_id"),
                EnumDyField.data_source(
                    "Recurrence Type",
                    "data.recurrence_type",
                    default_badge={"indigo.500": ["DAILY"], "coral.600": ["WEEKLY"]},
                ),
                TextDyField.data_source("Retention", "data.retention"),
                DateTimeDyField.data_source("Created", "data.create_time"),
                DateTimeDyField.data_source("Updated", "data.update_time"),
                TextDyField.data_source("UID", "data.uid"),
            ],
        )
    ]
)


class BackupScheduleResource(CloudServiceResource):
    cloud_service_group = StringType(default="Firestore")
    cloud_service_type = StringType(default="BackupSchedule")
    data = ModelType(BackupSchedule)
    _metadata = ModelType(
        CloudServiceMeta, default=backup_schedule_meta, serialized_name="metadata"
    )


class BackupScheduleResponse(CloudServiceResponse):
    resource = PolyModelType(BackupScheduleResource)
