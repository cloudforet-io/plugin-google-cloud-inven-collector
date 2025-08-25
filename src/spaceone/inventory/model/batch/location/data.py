from schematics import Model
from schematics.types import DictType, IntType, ListType, ModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
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

"""
Batch Location Data Model
"""


class BatchTask(Model):
    """Batch Task 정보 모델"""

    name = StringType()
    task_index = IntType(deserialize_from="taskIndex")
    state = StringType()
    create_time = StringType(deserialize_from="createTime")
    start_time = StringType(deserialize_from="startTime")
    end_time = StringType(deserialize_from="endTime")
    exit_code = IntType(deserialize_from="exitCode")


class BatchTaskGroup(Model):
    """Batch TaskGroup 정보 모델"""

    name = StringType()
    task_count = StringType(deserialize_from="taskCount")
    parallelism = StringType()
    machine_type = StringType(deserialize_from="machineType")
    image_uri = StringType(deserialize_from="imageUri")
    cpu_milli = StringType(deserialize_from="cpuMilli")
    memory_mib = StringType(deserialize_from="memoryMib")
    tasks = ListType(ModelType(BatchTask), serialize_when_none=False)


class BatchJobSummary(Model):
    """간단한 Batch Job 정보 모델"""

    name = StringType()
    uid = StringType()
    display_name = StringType(deserialize_from="displayName")
    state = StringType()
    create_time = StringType(deserialize_from="createTime")
    update_time = StringType(deserialize_from="updateTime")
    task_groups = ListType(
        ModelType(BatchTaskGroup),
        deserialize_from="taskGroups",
        serialize_when_none=False,
    )


class Location(Model):
    """Batch Location 정보 모델"""

    name = StringType()
    location_id = StringType(deserialize_from="locationId")
    display_name = StringType(deserialize_from="displayName")
    metadata = DictType(StringType)
    labels = DictType(StringType)
    project_id = StringType()
    jobs = ListType(ModelType(BatchJobSummary), serialize_when_none=False)  # Jobs 정보
    job_count = IntType(serialize_when_none=False)  # Job 개수 추가

    def reference(self):
        return {
            "resource_id": self.location_id,
            "external_link": f"https://console.cloud.google.com/batch/locations/{self.location_id}?project={self.project_id}",
        }


# TAB - Project Info
project_info_meta = ItemDynamicLayout.set_fields(
    "Project Info",
    fields=[
        TextDyField.data_source("Project ID", "data.project_id"),
    ],
)

# TAB - Location Info
location_info_meta = ItemDynamicLayout.set_fields(
    "Location Info",
    fields=[
        TextDyField.data_source("Location ID", "data.location_id"),
        TextDyField.data_source("Display Name", "data.display_name"),
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("Job Count", "data.job_count"),
    ],
)

# TAB - Jobs (Job, TaskGroup, Task 정보를 모두 포함)
batch_jobs_meta = TableDynamicLayout.set_fields(
    "Jobs",
    root_path="data.jobs",
    fields=[
        TextDyField.data_source("Job Name", "name"),
        TextDyField.data_source("Job ID", "uid"),
        TextDyField.data_source("Display Name", "display_name"),
        EnumDyField.data_source(
            "Job State",
            "state",
            default_state={
                "safe": ["SUCCEEDED"],
                "warning": ["SCHEDULED", "QUEUED", "RUNNING"],
                "alert": ["FAILED"],
                "disable": ["DELETION_IN_PROGRESS"],
            },
        ),
        TextDyField.data_source("Task Groups", "task_groups"),
        DateTimeDyField.data_source("Create Time", "create_time"),
        DateTimeDyField.data_source("Update Time", "update_time"),
    ],
)


# TAB - Metadata
location_metadata_meta = ItemDynamicLayout.set_fields(
    "Metadata",
    fields=[
        TextDyField.data_source("Metadata", "data.metadata"),
        TextDyField.data_source("Labels", "data.labels"),
    ],
)

batch_location_meta = CloudServiceMeta.set_layouts(
    [
        project_info_meta,
        location_info_meta,
        batch_jobs_meta,
        location_metadata_meta,
    ]
)
