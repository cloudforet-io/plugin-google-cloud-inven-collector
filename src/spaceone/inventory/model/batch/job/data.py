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
Batch Job 기준 Data Models - Job 개별 리소스로 관리
"""


class StatusEvent(Model):
    """Task Status Event 모델"""
    
    event_time = StringType(deserialize_from="eventTime", serialize_when_none=False)
    type = StringType(serialize_when_none=False)
    task_state = StringType(deserialize_from="taskState", serialize_when_none=False)
    description = StringType(serialize_when_none=False)


class BatchTask(Model):
    """Batch Task 모델 - Job 내 개별 Task 정보"""

    name = StringType(serialize_when_none=False)
    state = StringType(serialize_when_none=False)
    status_events = ListType(
        ModelType(StatusEvent),
        deserialize_from="statusEvents",
        serialize_when_none=False,
    )
    # 최신 이벤트 정보 (UI 표시용)
    last_event_type = StringType(serialize_when_none=False)
    last_event_time = StringType(serialize_when_none=False)


class BatchTaskGroup(Model):
    """Batch TaskGroup 모델 - Job 내 TaskGroup 정보"""

    name = StringType(serialize_when_none=False)
    task_count = StringType(deserialize_from="taskCount", serialize_when_none=False)
    parallelism = StringType(serialize_when_none=False)
    machine_type = StringType(deserialize_from="machineType", serialize_when_none=False)
    image_uri = StringType(deserialize_from="imageUri", serialize_when_none=False)
    cpu_milli = StringType(deserialize_from="cpuMilli", serialize_when_none=False)
    memory_mib = StringType(deserialize_from="memoryMib", serialize_when_none=False)
    tasks = ListType(ModelType(BatchTask), serialize_when_none=False)


class BatchJobResource(Model):
    """Batch Job 리소스 모델 - 개별 Job을 하나의 리소스로 관리"""

    name = StringType(serialize_when_none=False)
    uid = StringType(serialize_when_none=False)
    display_name = StringType(deserialize_from="displayName", serialize_when_none=False)
    state = StringType(serialize_when_none=False)
    create_time = StringType(deserialize_from="createTime", serialize_when_none=False)
    update_time = StringType(deserialize_from="updateTime", serialize_when_none=False)
    
    # Location 정보 추가
    location_id = StringType(serialize_when_none=False)
    project_id = StringType(serialize_when_none=False)
    
    # Job 세부 정보
    task_groups = ListType(
        ModelType(BatchTaskGroup),
        deserialize_from="taskGroups",
        serialize_when_none=False,
    )
    task_count = IntType(serialize_when_none=False)  # 총 Task 개수
    all_tasks = ListType(
        ModelType(BatchTask),
        serialize_when_none=False,
    )  # UI 표시용 모든 Task 목록 (평면화)
    
    # 메타데이터
    labels = DictType(StringType, serialize_when_none=False)
    annotations = DictType(StringType, serialize_when_none=False)

    def reference(self):
        """Job 개별 참조 링크 생성"""
        if self.name and self.project_id and self.location_id:
            # Job name에서 Job ID 추출 (projects/.../locations/.../jobs/{job_id})
            job_id = self.name.split('/')[-1] if '/' in self.name else self.name
            return {
                "resource_id": self.uid or self.name,
                "external_link": f"https://console.cloud.google.com/batch/jobsDetail/regions/{self.location_id}/jobs/{job_id}/details?project={self.project_id}",
            }
        else:
            return {
                "resource_id": self.uid or self.name or "unknown",
                "external_link": f"https://console.cloud.google.com/batch/jobs?project={self.project_id}",
            }


# ===== Job 기준 UI 레이아웃 =====

# TAB - Job Overview (Job 개요)
job_overview_meta = ItemDynamicLayout.set_fields(
    "Job Overview",
    fields=[
        TextDyField.data_source("Job Name", "data.display_name"),
        TextDyField.data_source("Job ID", "data.uid"),
        TextDyField.data_source("Full Name", "data.name"),
        EnumDyField.data_source(
            "Status",
            "data.state",
            default_state={
                "safe": ["SUCCEEDED"],
                "warning": ["SCHEDULED", "QUEUED", "RUNNING", "PENDING"],
                "alert": ["FAILED"],
                "disable": ["DELETION_IN_PROGRESS"],
            },
        ),
        TextDyField.data_source("Location", "data.location_id"),
        TextDyField.data_source("Project ID", "data.project_id"),
        DateTimeDyField.data_source("Created", "data.create_time"),
        DateTimeDyField.data_source("Updated", "data.update_time"),
        TextDyField.data_source("Total Tasks", "data.task_count"),
    ],
)

# TAB - Task Groups (TaskGroup 정보)
task_groups_meta = TableDynamicLayout.set_fields(
    "Task Groups",
    root_path="data.task_groups",
    fields=[
        TextDyField.data_source("Name", "name"),
        TextDyField.data_source("Task Count", "task_count"),
        TextDyField.data_source("Parallelism", "parallelism"),
        TextDyField.data_source("Machine Type", "machine_type"),
        TextDyField.data_source("Image URI", "image_uri"),
        TextDyField.data_source("CPU (milli)", "cpu_milli"),
        TextDyField.data_source("Memory (MiB)", "memory_mib"),
    ],
)

# TAB - Tasks (Task 세부 정보)
tasks_meta = TableDynamicLayout.set_fields(
    "Tasks",
    root_path="data.all_tasks",
    fields=[
        TextDyField.data_source("Task Name", "name"),
        EnumDyField.data_source(
            "Status",
            "state",
            default_state={
                "safe": ["SUCCEEDED"],
                "warning": ["ASSIGNED", "RUNNING", "PENDING"],
                "alert": ["FAILED"],
                "disable": ["STATE_UNSPECIFIED"],
            },
        ),
        TextDyField.data_source("Last Event Type", "last_event_type"),
        DateTimeDyField.data_source("Last Event Time", "last_event_time"),
    ],
)

# Job 기준 메타데이터
batch_job_meta = CloudServiceMeta.set_layouts(
    [
        job_overview_meta,
        task_groups_meta,
        tasks_meta,
    ]
)
