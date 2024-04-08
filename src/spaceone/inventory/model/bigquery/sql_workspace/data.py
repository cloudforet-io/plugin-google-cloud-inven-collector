from schematics import Model
from schematics.types import (
    ModelType,
    ListType,
    StringType,
    IntType,
    DateTimeType,
    BooleanType,
    FloatType,
    DictType,
    UnionType,
    MultiType,
)
from spaceone.inventory.libs.schema.cloud_service import BaseResource


class Labels(Model):
    key = StringType()
    value = StringType()


class View(Model):
    use_legacy_sql = BooleanType(
        deserialize_from="useLegacySql", serialize_when_none=False
    )


class Range(Model):
    start = StringType(serialize_when_none=False)
    end = StringType(serialize_when_none=False)
    interval = StringType(serialize_when_none=False)


class TimePartitioning(Model):
    type = StringType()
    expiration_ms = StringType(
        deserialize_from="expirationMs", serialize_when_none=False
    )
    field = StringType(serialize_when_none=False)
    require_partition_filter = StringType(
        deserialize_from="requirePartitionFilter", serialize_when_none=False
    )


class RangePartitioning(Model):
    field = StringType()
    range = ModelType(Range, serialize_when_none=False)


class TableReference(Model):
    project_id = StringType(deserialize_from="projectId", serialize_when_none=False)
    dataset_id = StringType(deserialize_from="datasetId", serialize_when_none=False)
    table_id = StringType(deserialize_from="tableId", serialize_when_none=False)


class TableSchema(Model):
    name = StringType()
    type = StringType()
    mode = StringType()


class ProjectReference(Model):
    project_id = StringType()


class ReservationUsage(Model):
    name = StringType(serialize_when_none=False)
    slot_ms = StringType(deserialize_from="slotMs", serialize_when_none=False)


class Table(Model):
    id = StringType(deserialize_from="id")
    name = StringType(serialize_when_none=False)
    type = StringType(serialize_when_none=False)
    creation_time = DateTimeType(
        deserialize_from="creationTime", serialize_when_none=False
    )
    expiration_time = DateTimeType(
        deserialize_from="expirationTime", serialize_when_none=False
    )
    last_modified_time = DateTimeType(
        deserialize_from="lastModifiedTime", serialize_when_none=False
    )


class DatasetReference(Model):
    dataset_id = StringType(deserialize_from="datasetId", serialize_when_none=False)
    project_id = StringType(deserialize_from="projectId", serialize_when_none=False)


class ProjectModel(Model):
    id = StringType()
    kind = StringType()
    numeric_id = StringType(deserialize_from="numericId")
    project_reference = ModelType(
        ProjectReference, deserialize_from="projectReference", serialize_when_none=False
    )
    friendly_name = StringType(
        deserialize_from="friendlyName", serialize_when_none=False
    )


class Access(Model):
    role = StringType(deserialize_from="role", serialize_when_none=False)
    special_group = StringType(
        deserialize_from="specialGroup", serialize_when_none=False
    )
    user_by_email = StringType(
        deserialize_from="userByEmail", serialize_when_none=False
    )


class BigQueryWorkSpace(BaseResource):
    matching_project = ListType(ModelType(ProjectModel), default=[])
    dataset_reference = ModelType(
        DatasetReference, deserialize_from="datasetReference", serialize_when_none=False
    )
    friendly_name = StringType(
        deserialize_from="friendlyName", serialize_when_none=False
    )
    tables = ListType(ModelType(Table), default=[])
    access = ListType(ModelType(Access), default=[])
    labels = ListType(ModelType(Labels), default=[])
    etags = StringType(serialize_when_none=False)
    location = StringType()
    default_partition_expiration_ms_display = IntType(serialize_when_none=False)
    default_table_expiration_ms_display = IntType(serialize_when_none=False)
    default_table_expiration_ms = StringType(
        deserialize_from="defaultTableExpirationMs", serialize_when_none=False
    )
    default_partition_expiration_ms = StringType(
        deserialize_from="defaultPartitionExpirationMs", serialize_when_none=False
    )

    creation_time = DateTimeType(deserialize_from="creationTime")
    last_modified_time = DateTimeType(deserialize_from="lastModifiedTime")

    def reference(self):
        return {
            "resource_id": self.self_link,
            "external_link": f"https://console.cloud.google.com/bigquery?project={self.project}&p={self.dataset_reference.project_id}&page=dataset&d={self.dataset_reference.dataset_id}",
        }
