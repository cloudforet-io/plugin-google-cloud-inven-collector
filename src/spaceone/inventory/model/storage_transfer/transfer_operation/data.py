from schematics import Model
from schematics.types import (
    BooleanType,
    DateTimeType,
    DictType,
    IntType,
    ListType,
    ModelType,
    StringType,
)

from spaceone.inventory.libs.schema.cloud_service import BaseResource


class Labels(Model):
    key = StringType()
    value = StringType()


class TransferCounters(Model):
    """전송 카운터 정보"""

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


class ErrorSummary(Model):
    """에러 요약 정보"""

    error_code = StringType(deserialize_from="errorCode")
    error_count = IntType(deserialize_from="errorCount")


class OperationMetadata(Model):
    """Operation의 metadata 정보"""

    type = StringType(deserialize_from="@type", serialize_when_none=False)
    name = StringType()
    project_id = StringType(deserialize_from="projectId")
    start_time = DateTimeType(deserialize_from="startTime", serialize_when_none=False)
    end_time = DateTimeType(deserialize_from="endTime", serialize_when_none=False)
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
    error_breakdowns = ListType(
        ModelType(ErrorSummary), deserialize_from="errorBreakdowns", default=[]
    )
    transfer_job_name = StringType(deserialize_from="transferJobName")


class TransferOperation(BaseResource):
    """Storage Transfer Operation 모델"""

    metadata = ModelType(OperationMetadata, serialize_when_none=False)
    done = BooleanType(serialize_when_none=False)
    response = DictType(StringType, serialize_when_none=False)
    error = DictType(StringType, serialize_when_none=False)

    # 표시용 정보
    project_id = StringType(serialize_when_none=False)
    transfer_job_name = StringType(serialize_when_none=False)
    duration = StringType(serialize_when_none=False)  # 실행 시간

    labels = ListType(ModelType(Labels), default=[])

    def reference(self):
        return {
            "resource_id": self.name,
            "external_link": f"https://console.cloud.google.com/transfer/jobs?project={self.project_id}",
        }
