from schematics import Model
from schematics.types import DictType, IntType, ListType, ModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import CloudServiceMeta
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
최적화된 Batch Data Models - 성능과 가독성 개선
"""


class BatchTask(Model):
    """최적화된 Batch Task 모델 - 필수 필드만 포함"""

    name = StringType(serialize_when_none=False)
    task_index = IntType(deserialize_from="taskIndex", serialize_when_none=False)
    state = StringType(serialize_when_none=False)
    create_time = StringType(deserialize_from="createTime", serialize_when_none=False)
    start_time = StringType(deserialize_from="startTime", serialize_when_none=False)
    end_time = StringType(deserialize_from="endTime", serialize_when_none=False)
    exit_code = IntType(deserialize_from="exitCode", serialize_when_none=False)


class BatchTaskGroup(Model):
    """최적화된 Batch TaskGroup 모델 - 성능과 가독성 개선"""

    name = StringType(serialize_when_none=False)
    task_count = StringType(deserialize_from="taskCount", serialize_when_none=False)
    parallelism = StringType(serialize_when_none=False)
    machine_type = StringType(deserialize_from="machineType", serialize_when_none=False)
    image_uri = StringType(deserialize_from="imageUri", serialize_when_none=False)
    cpu_milli = StringType(deserialize_from="cpuMilli", serialize_when_none=False)
    memory_mib = StringType(deserialize_from="memoryMib", serialize_when_none=False)
    tasks = ListType(ModelType(BatchTask), serialize_when_none=False)


class BatchJobSummary(Model):
    """최적화된 Batch Job 모델 - 핵심 정보 중심"""

    name = StringType(serialize_when_none=False)
    uid = StringType(serialize_when_none=False)
    display_name = StringType(deserialize_from="displayName", serialize_when_none=False)
    state = StringType(serialize_when_none=False)
    create_time = StringType(deserialize_from="createTime", serialize_when_none=False)
    update_time = StringType(deserialize_from="updateTime", serialize_when_none=False)
    task_groups = ListType(
        ModelType(BatchTaskGroup),
        deserialize_from="taskGroups",
        serialize_when_none=False,
    )


class Location(Model):
    """Batch 정보 모델"""

    name = StringType(serialize_when_none=False)
    location_id = StringType(deserialize_from="locationId", serialize_when_none=False)
    display_name = StringType(deserialize_from="displayName", serialize_when_none=False)
    metadata = DictType(StringType, serialize_when_none=False)
    labels = DictType(StringType, serialize_when_none=False)
    project_id = StringType()
    jobs = ListType(ModelType(BatchJobSummary), serialize_when_none=False)  # Jobs 정보
    job_count = IntType(serialize_when_none=False)  # Job 개수 추가

    def reference(self):
        if self.location_id:
            return {
                "resource_id": self.location_id,
                "external_link": f"https://console.cloud.google.com/batch/locations/{self.location_id}?project={self.project_id}",
            }
        else:
            return {
                "resource_id": "batch",
                "external_link": f"https://console.cloud.google.com/batch?project={self.project_id}",
            }


# ===== 최적화된 UI 레이아웃 =====

# TAB - Project Overview (프로젝트 개요)
project_info_meta = ItemDynamicLayout.set_fields(
    "Project Overview",
    fields=[
        TextDyField.data_source("Project ID", "data.project_id"),
        TextDyField.data_source("Total Jobs", "data.job_count"),
    ],
)

# TAB - Jobs (핵심 Job 정보만 표시)
batch_jobs_meta = TableDynamicLayout.set_fields(
    "Jobs",
    root_path="data.jobs",
    fields=[
        TextDyField.data_source("Job Name", "name"),
        TextDyField.data_source("Job ID", "uid"),
        TextDyField.data_source("Display Name", "display_name"),
        EnumDyField.data_source(
            "Status",
            "state",
            default_state={
                "safe": ["SUCCEEDED"],
                "warning": ["SCHEDULED", "QUEUED", "RUNNING", "PENDING"],
                "alert": ["FAILED"],
                "disable": ["DELETION_IN_PROGRESS"],
            },
        ),
        DateTimeDyField.data_source("Created", "create_time"),
        DateTimeDyField.data_source("Updated", "update_time"),
    ],
)

# 최적화된 메타데이터 - 필수 탭만 포함
batch_location_meta = CloudServiceMeta.set_layouts(
    [
        project_info_meta,
        batch_jobs_meta,
    ]
)
