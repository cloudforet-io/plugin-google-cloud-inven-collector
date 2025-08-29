from schematics import Model
from schematics.types import (
    BooleanType,
    DateTimeType,
    DictType,
    ListType,
    ModelType,
    StringType,
)

from spaceone.inventory.libs.schema.cloud_service import BaseResource


class Labels(Model):
    key = StringType()
    value = StringType()


class TransferSpec(Model):
    """전송 사양 정보"""

    gcs_data_sink = DictType(
        StringType, deserialize_from="gcsDataSink", serialize_when_none=False
    )
    gcs_data_source = DictType(
        StringType, deserialize_from="gcsDataSource", serialize_when_none=False
    )
    aws_s3_data_source = DictType(
        StringType, deserialize_from="awsS3DataSource", serialize_when_none=False
    )
    http_data_source = DictType(
        StringType, deserialize_from="httpDataSource", serialize_when_none=False
    )
    azure_blob_storage_data_source = DictType(
        StringType,
        deserialize_from="azureBlobStorageDataSource",
        serialize_when_none=False,
    )
    posix_data_source = DictType(
        StringType, deserialize_from="posixDataSource", serialize_when_none=False
    )
    posix_data_sink = DictType(
        StringType, deserialize_from="posixDataSink", serialize_when_none=False
    )
    object_conditions = DictType(
        StringType, deserialize_from="objectConditions", serialize_when_none=False
    )
    transfer_options = DictType(
        StringType, deserialize_from="transferOptions", serialize_when_none=False
    )
    transfer_manifest = DictType(
        StringType, deserialize_from="transferManifest", serialize_when_none=False
    )
    source_agent_pool_name = StringType(
        deserialize_from="sourceAgentPoolName", serialize_when_none=False
    )
    sink_agent_pool_name = StringType(
        deserialize_from="sinkAgentPoolName", serialize_when_none=False
    )


class Schedule(Model):
    """전송 스케줄 정보"""

    schedule_start_date = DictType(
        StringType, deserialize_from="scheduleStartDate", serialize_when_none=False
    )
    schedule_end_date = DictType(
        StringType, deserialize_from="scheduleEndDate", serialize_when_none=False
    )
    start_time_of_day = DictType(
        StringType, deserialize_from="startTimeOfDay", serialize_when_none=False
    )
    repeat_interval = StringType(
        deserialize_from="repeatInterval", serialize_when_none=False
    )


class NotificationConfig(Model):
    """알림 설정 정보"""

    pubsub_topic = StringType(deserialize_from="pubsubTopic")
    event_types = ListType(StringType, deserialize_from="eventTypes", default=[])
    payload_format = StringType(
        deserialize_from="payloadFormat", serialize_when_none=False
    )


class LoggingConfig(Model):
    """로깅 설정 정보"""

    log_actions = ListType(StringType, deserialize_from="logActions", default=[])
    log_action_states = ListType(
        StringType, deserialize_from="logActionStates", default=[]
    )
    enable_onprem_gcs_transfer_logs = BooleanType(
        deserialize_from="enableOnpremGcsTransferLogs", serialize_when_none=False
    )


class TransferJob(BaseResource):
    """Storage Transfer Job 메인 모델 (간소화 버전)"""

    project_id = StringType(deserialize_from="projectId")
    description = StringType(serialize_when_none=False)
    transfer_spec = ModelType(TransferSpec, deserialize_from="transferSpec")
    notification_config = ModelType(
        NotificationConfig,
        deserialize_from="notificationConfig",
        serialize_when_none=False,
    )
    logging_config = ModelType(
        LoggingConfig, deserialize_from="loggingConfig", serialize_when_none=False
    )
    schedule = ModelType(Schedule, serialize_when_none=False)
    status = StringType(choices=("ENABLED", "DISABLED", "DELETED"))
    creation_time = DateTimeType(deserialize_from="creationTime")
    last_modification_time = DateTimeType(deserialize_from="lastModificationTime")
    deletion_time = DateTimeType(
        deserialize_from="deletionTime", serialize_when_none=False
    )
    latest_operation_name = StringType(
        deserialize_from="latestOperationName", serialize_when_none=False
    )

    # 표시용 정보 (Manager에서 계산)
    source_type = StringType(serialize_when_none=False)  # GCS, S3, Azure, HTTP, POSIX
    sink_type = StringType(serialize_when_none=False)  # GCS, POSIX
    schedule_display = StringType(serialize_when_none=False)
    transfer_options_display = StringType(serialize_when_none=False)

    labels = ListType(ModelType(Labels), default=[])

    def reference(self):
        return {
            "resource_id": self.self_link,
            "external_link": f"https://console.cloud.google.com/transfer/jobs/{self.name}?project={self.project_id}",
        }
