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
        TextDyField.data_source("Database ID", "data.database_id"),
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("UID", "data.uid"),
        EnumDyField.data_source(
            "Type",
            "data.type",
            default_badge={
                "indigo.500": ["DATASTORE_MODE"],
                "coral.600": ["FIRESTORE_NATIVE"],
            },
        ),
        TextDyField.data_source("Location", "data.location_id"),
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
        TextDyField.data_source("Project ID", "data.project_id"),
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
