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
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
)
from spaceone.inventory.model.datastore.database.data import DatastoreDatabaseData

"""
DATABASE
"""
database_info_meta = ItemDynamicLayout.set_fields(
    "Database Details",
    fields=[
        TextDyField.data_source("Database ID", "data.name"),
        TextDyField.data_source("Name", "data.full_name"),
        TextDyField.data_source("UID", "data.uid"),
        EnumDyField.data_source(
            "Type",
            "data.type",
            default_badge={
                "indigo.500": ["DATASTORE_MODE"],
                "coral.600": ["FIRESTORE_NATIVE"],
            },
        ),
        EnumDyField.data_source(
            "Concurrency Mode",
            "data.concurrency_mode",
            default_badge={
                "indigo.500": ["OPTIMISTIC"],
                "coral.600": ["PESSIMISTIC"],
                "peacock.500": ["OPTIMISTIC_WITH_ENTITY_GROUPS"],
            },
        ),
        DateTimeDyField.data_source("Created", "data.create_time"),
        DateTimeDyField.data_source("Updated", "data.update_time"),
        TextDyField.data_source("Location", "data.location_id"),
        EnumDyField.data_source(
            "Database Edition",
            "data.database_edition",
            default_badge={
                "indigo.500": ["STANDARD"],
                "violet.500": ["ENTERPRISE"],
                "coral.600": ["ENTERPRISE_PLUS"],
            },
        ),
        EnumDyField.data_source(
            "Free Tier",
            "data.free_tier",
            default_badge={"indigo.500": ["true"], "coral.600": ["false"]},
        ),
        EnumDyField.data_source(
            "App Engine Integration",
            "data.app_engine_integration_mode",
            default_badge={
                "indigo.500": ["ENABLED"],
                "gray.500": ["DISABLED"],
            },
        ),
        EnumDyField.data_source(
            "Point-in-Time Recovery",
            "data.point_in_time_recovery_enablement",
            default_badge={
                "green.500": ["ENABLED"],
                "red.500": ["DISABLED"],
            },
        ),
        EnumDyField.data_source(
            "Delete Protection",
            "data.delete_protection_state",
            default_badge={
                "green.500": ["DELETE_PROTECTION_ENABLED"],
                "red.500": ["DELETE_PROTECTION_DISABLED"],
                "gray.500": ["DELETE_PROTECTION_STATE_UNSPECIFIED"],
            },
        ),
        TextDyField.data_source(
            "Version Retention Period", "data.version_retention_period"
        ),
        DateTimeDyField.data_source(
            "Earliest Version Time", "data.earliest_version_time"
        ),
    ],
)

database_meta = CloudServiceMeta.set_layouts([database_info_meta])


class DatastoreDatabaseResource(CloudServiceResource):
    cloud_service_type = StringType(default="Database")
    cloud_service_group = StringType(default="Datastore")
    provider = StringType(default="google_cloud")
    data = ModelType(DatastoreDatabaseData)
    _metadata = ModelType(
        CloudServiceMeta, default=database_meta, serialized_name="metadata"
    )


class DatastoreDatabaseResponse(CloudServiceResponse):
    resource = PolyModelType(DatastoreDatabaseResource)
