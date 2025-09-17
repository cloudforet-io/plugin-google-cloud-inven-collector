from schematics import Model
from schematics.types import (
    BooleanType,
    DictType,
    IntType,
    ModelType,
    StringType,
)

from spaceone.inventory.libs.schema.cloud_service import BaseResource


class Labels(Model):
    key = StringType()
    value = StringType()


class TransferCounters(Model):
    """Transfer counter information"""

    objects_found_from_source = IntType(
        deserialize_from="objectsFoundFromSource", serialize_when_none=False
    )
    bytes_found_from_source = IntType(
        deserialize_from="bytesFoundFromSource", serialize_when_none=False
    )
    objects_copied_to_sink = IntType(
        deserialize_from="objectsCopiedToSink", serialize_when_none=False
    )
    bytes_copied_to_sink = IntType(
        deserialize_from="bytesCopiedToSink", serialize_when_none=False
    )
    objects_from_source_failed = IntType(
        deserialize_from="objectsFromSourceFailed", serialize_when_none=False
    )
    bytes_from_source_failed = IntType(
        deserialize_from="bytesFromSourceFailed", serialize_when_none=False
    )


class OperationError(Model):
    code = IntType(serialize_when_none=False)  # google.rpc.Code enum 값
    message = StringType(serialize_when_none=False)


class OperationMetadata(Model):
    """Operation metadata information"""

    type = StringType(deserialize_from="@type", serialize_when_none=False)
    name = StringType()
    project_id = StringType(deserialize_from="projectId")
    start_time = StringType(deserialize_from="startTime", serialize_when_none=False)
    end_time = StringType(deserialize_from="endTime", serialize_when_none=False)
    status = StringType(
        choices=(
            "IN_PROGRESS",
            "PAUSED",
            "SUCCESS",
            "FAILED",
            "ABORTED",
            "QUEUED",
            "SUSPENDING",
        )
    )
    counters = ModelType(TransferCounters, serialize_when_none=False)
    transfer_job_name = StringType(deserialize_from="transferJobName")


class TransferOperation(BaseResource):
    """Storage Transfer Operation model"""

    metadata = ModelType(OperationMetadata, serialize_when_none=False)
    done = BooleanType(serialize_when_none=False)
    response = DictType(StringType, serialize_when_none=False)
    error = ModelType(OperationError, serialize_when_none=False)

    full_name = StringType()
    transfer_job_name = StringType(serialize_when_none=False)
    transfer_job_id = StringType(serialize_when_none=False)
    duration = StringType(serialize_when_none=False)

    def reference(self):
        return {
            "resource_id": f"https://storagetransfer.googleapis.com/v1/{self.full_name}",
            "external_link": f"https://console.cloud.google.com/transfer/jobs/transferJobs%2F{self.transfer_job_id}?project={self.project}",
        }
