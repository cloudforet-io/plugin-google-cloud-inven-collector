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
from spaceone.inventory.model.firestore.database.data import Database

"""
DATABASE
"""
database_meta = CloudServiceMeta.set_layouts(
    [
        ItemDynamicLayout.set_fields(
            "Database",
            fields=[
                TextDyField.data_source("Database ID", "data.id"),
                TextDyField.data_source("Name", "data.name"),
                TextDyField.data_source("Project", "data.project_id"),
                TextDyField.data_source("Location", "data.location_id"),
                EnumDyField.data_source(
                    "Type",
                    "data.type",
                    default_badge={
                        "indigo.500": ["FIRESTORE_NATIVE"],
                        "coral.600": ["DATASTORE_MODE"],
                    },
                ),
                EnumDyField.data_source(
                    "Concurrency Mode",
                    "data.concurrency_mode",
                    default_badge={
                        "indigo.500": ["OPTIMISTIC"],
                        "coral.600": ["PESSIMISTIC"],
                    },
                ),
                EnumDyField.data_source(
                    "App Engine Integration",
                    "data.app_engine_integration_mode",
                    default_badge={
                        "indigo.500": ["ENABLED"],
                        "gray.400": ["DISABLED"],
                    },
                ),
                TextDyField.data_source("UID", "data.uid"),
                TextDyField.data_source("ETag", "data.etag"),
                TextDyField.data_source("Key Prefix", "data.key_prefix"),
            ],
        ),
        ItemDynamicLayout.set_fields(
            "Timestamps",
            fields=[
                DateTimeDyField.data_source("Created", "data.create_time"),
                DateTimeDyField.data_source("Updated", "data.update_time"),
            ],
        ),
        ItemDynamicLayout.set_fields(
            "Security & Backup",
            fields=[
                EnumDyField.data_source(
                    "Delete Protection",
                    "data.delete_protection_state",
                    default_badge={
                        "indigo.500": ["DELETE_PROTECTION_ENABLED"],
                        "coral.600": ["DELETE_PROTECTION_DISABLED"],
                        "gray.400": ["DELETE_PROTECTION_STATE_UNSPECIFIED"],
                    },
                ),
                EnumDyField.data_source(
                    "Point-in-time Recovery",
                    "data.point_in_time_recovery_enablement",
                    default_badge={
                        "indigo.500": ["POINT_IN_TIME_RECOVERY_ENABLED"],
                        "coral.600": ["POINT_IN_TIME_RECOVERY_DISABLED"],
                        "gray.400": ["POINT_IN_TIME_RECOVERY_ENABLEMENT_UNSPECIFIED"],
                    },
                ),
                TextDyField.data_source(
                    "Version Retention Period", "data.version_retention_period"
                ),
                DateTimeDyField.data_source(
                    "Earliest Version Time", "data.earliest_version_time"
                ),
            ],
        ),
    ]
)


class DatabaseResource(CloudServiceResource):
    cloud_service_group = StringType(default="Firestore")
    cloud_service_type = StringType(default="Database")
    data = ModelType(Database)
    _metadata = ModelType(
        CloudServiceMeta, default=database_meta, serialized_name="metadata"
    )


class DatabaseResponse(CloudServiceResponse):
    resource = PolyModelType(DatabaseResource)
