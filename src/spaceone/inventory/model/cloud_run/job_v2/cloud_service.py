from schematics.types import ModelType, PolyModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    DateTimeDyField,
    ListDyField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    TableDynamicLayout,
)
from spaceone.inventory.model.cloud_run.job_v2.data import Job

"""
Cloud Run Job
"""
# TAB - Job Overview
job_overview = ItemDynamicLayout.set_fields(
    "Job Overview",
    fields=[
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("UID", "data.uid"),
        TextDyField.data_source("Generation", "data.generation"),
        TextDyField.data_source("Creator", "data.creator"),
        TextDyField.data_source("Last Modifier", "data.last_modifier"),
        TextDyField.data_source("Client", "data.client"),
        TextDyField.data_source("Launch Stage", "data.launch_stage"),
        TextDyField.data_source("Observed Generation", "data.observed_generation"),
        TextDyField.data_source("ETag", "data.etag"),
        DateTimeDyField.data_source("Create Time", "data.create_time"),
        DateTimeDyField.data_source("Update Time", "data.update_time"),
        DateTimeDyField.data_source("Delete Time", "data.delete_time"),
        DateTimeDyField.data_source("Expire Time", "data.expire_time"),
    ],
)

# TAB - Status & Conditions
job_status = ItemDynamicLayout.set_fields(
    "Status & Conditions",
    fields=[
        TextDyField.data_source("Execution Count", "data.execution_count"),
        TextDyField.data_source(
            "Latest Created Execution", "data.latest_created_execution.name"
        ),
        DateTimeDyField.data_source(
            "Latest Execution Create Time", "data.latest_created_execution.create_time"
        ),
        DateTimeDyField.data_source(
            "Latest Execution Completion Time",
            "data.latest_created_execution.completion_time",
        ),
        TextDyField.data_source(
            "Latest Execution Status", "data.latest_created_execution.completion_status"
        ),
        ListDyField.data_source(
            "Conditions",
            "data.conditions",
            default_badge={
                "type": "outline",
                "sub_key": "type",
                "delimiter": "<br>",
            },
        ),
    ],
)

# TAB - Executions
job_executions = TableDynamicLayout.set_fields(
    "Executions",
    fields=[
        TextDyField.data_source("Name", "data.executions.name"),
        TextDyField.data_source("UID", "data.executions.uid"),
        TextDyField.data_source("Creator", "data.executions.creator"),
        TextDyField.data_source("Job", "data.executions.job"),
        TextDyField.data_source("Task Count", "data.executions.task_count"),
    ],
    root_path="data.executions",
)

cloud_run_job_meta = CloudServiceMeta.set_layouts(
    [
        job_overview,
        job_status,
        job_executions,
    ]
)


class CloudRunResource(CloudServiceResource):
    cloud_service_group = StringType(default="CloudRun")


class JobResource(CloudRunResource):
    cloud_service_type = StringType(default="Job")
    data = ModelType(Job)
    _metadata = ModelType(
        CloudServiceMeta, default=cloud_run_job_meta, serialized_name="metadata"
    )


class JobResponse(CloudServiceResponse):
    resource = PolyModelType(JobResource)
