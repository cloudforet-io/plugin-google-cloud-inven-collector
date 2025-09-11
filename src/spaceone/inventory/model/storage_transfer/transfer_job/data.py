import logging
from typing import Any, Dict, Optional, Tuple

from schematics import Model
from schematics.types import (
    BaseType,
    BooleanType,
    DictType,
    ListType,
    ModelType,
    StringType,
)

from spaceone.inventory.libs.schema.cloud_service import BaseResource

_LOGGER = logging.getLogger(__name__)


class Labels(Model):
    key = StringType()
    value = StringType()


class TransferSpec(Model):
    """전송 사양 정보 (Union Field 제약 적용)

    Union Fields:
    - data_source: 정확히 하나의 소스만 지정 가능
      (gcs_data_source, aws_s3_data_source, http_data_source,
       azure_blob_storage_data_source, posix_data_source)

    - data_sink: 정확히 하나의 싱크만 지정 가능
      (gcs_data_sink, posix_data_sink)
    """

    # Union field data_source - 정확히 하나만 설정 가능
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

    # Union field data_sink - 정확히 하나만 설정 가능
    gcs_data_sink = DictType(
        StringType, deserialize_from="gcsDataSink", serialize_when_none=False
    )
    posix_data_sink = DictType(
        StringType, deserialize_from="posixDataSink", serialize_when_none=False
    )

    # 기타 비-Union 필드들
    object_conditions = DictType(
        StringType, deserialize_from="objectConditions", serialize_when_none=False
    )
    transfer_options = DictType(
        BaseType, deserialize_from="transferOptions", serialize_when_none=False
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

    # 소스 우선순위 정의 (높은 숫자가 높은 우선순위)
    SOURCE_PRIORITY = {
        "gcs_data_source": 5,  # 가장 안정적이고 일반적
        "aws_s3_data_source": 4,  # 클라우드 간 마이그레이션 주요 케이스
        "posix_data_source": 3,  # 온프레미스 연동
        "azure_blob_storage_data_source": 2,  # 멀티클라우드 시나리오
        "http_data_source": 1,  # 특수 케이스
    }

    # 싱크 우선순위 정의
    SINK_PRIORITY = {
        "gcs_data_sink": 2,  # 주요 대상
        "posix_data_sink": 1,  # 특수 케이스
    }

    def get_active_source(self) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """활성화된 소스를 우선순위에 따라 반환"""
        sources = {
            "gcs_data_source": self.gcs_data_source,
            "aws_s3_data_source": self.aws_s3_data_source,
            "http_data_source": self.http_data_source,
            "azure_blob_storage_data_source": self.azure_blob_storage_data_source,
            "posix_data_source": self.posix_data_source,
        }

        active_sources = {k: v for k, v in sources.items() if v is not None}

        if not active_sources:
            return None, None

        if len(active_sources) > 1:
            # 경고 로그 출력
            source_names = list(active_sources.keys())
            _LOGGER.warning(
                f"Multiple data sources detected: {source_names}. "
                f"Union Field constraint requires exactly one. "
                f"Selecting highest priority source based on common usage patterns."
            )

        # 우선순위가 가장 높은 소스 선택
        selected_source = max(
            active_sources.keys(), key=lambda x: self.SOURCE_PRIORITY.get(x, 0)
        )

        if len(active_sources) > 1:
            _LOGGER.info(
                f"Selected source: {selected_source} (priority: {self.SOURCE_PRIORITY[selected_source]})"
            )

        return selected_source, active_sources[selected_source]

    def get_active_sink(self) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """활성화된 싱크를 우선순위에 따라 반환"""
        sinks = {
            "gcs_data_sink": self.gcs_data_sink,
            "posix_data_sink": self.posix_data_sink,
        }

        active_sinks = {k: v for k, v in sinks.items() if v is not None}

        if not active_sinks:
            return None, None

        if len(active_sinks) > 1:
            sink_names = list(active_sinks.keys())
            _LOGGER.warning(
                f"Multiple data sinks detected: {sink_names}. "
                f"Union Field constraint requires exactly one. "
                f"Selecting highest priority sink: gcs_data_sink"
            )

        selected_sink = max(
            active_sinks.keys(), key=lambda x: self.SINK_PRIORITY.get(x, 0)
        )

        return selected_sink, active_sinks[selected_sink]

    def get_source_type(self) -> Optional[str]:
        """현재 활성화된 소스 타입 반환"""
        source_name, _ = self.get_active_source()

        if source_name is None:
            _LOGGER.warning("No active data source found")
            return None

        source_type_map = {
            "gcs_data_source": "GCS",
            "aws_s3_data_source": "AWS_S3",
            "http_data_source": "HTTP",
            "azure_blob_storage_data_source": "AZURE_BLOB",
            "posix_data_source": "POSIX",
        }

        return source_type_map.get(source_name)

    def get_sink_type(self) -> Optional[str]:
        """현재 활성화된 싱크 타입 반환"""
        sink_name, _ = self.get_active_sink()

        if sink_name is None:
            _LOGGER.warning("No active data sink found")
            return None

        sink_type_map = {
            "gcs_data_sink": "GCS",
            "posix_data_sink": "POSIX",
        }

        return sink_type_map.get(sink_name)

    def validate_union_fields_with_warnings(self) -> Dict[str, Any]:
        """Union Field 제약을 검증하되, 위반 시 경고만 로그"""

        # 소스 검증
        source_name, source_data = self.get_active_source()
        if source_name is None:
            _LOGGER.error(
                "No data source specified - this may cause transfer job failure"
            )

        # 싱크 검증
        sink_name, sink_data = self.get_active_sink()
        if sink_name is None:
            _LOGGER.error(
                "No data sink specified - this may cause transfer job failure"
            )

        return {
            "active_source": source_name,
            "active_sink": sink_name,
            "source_data": source_data,
            "sink_data": sink_data,
        }

    @staticmethod
    def _format_source_details(source_type: str, source_data: Dict[str, Any]) -> str:
        """Format source details in human-readable format"""
        if not source_data:
            return "⚠️ Not configured"

        if source_type == "GCS":
            bucket = source_data.get("bucketName", "Unknown")
            path = source_data.get("path", "")
            return f"Bucket: {bucket}" + (f", Path: {path}" if path else "")

        elif source_type == "AWS_S3":
            bucket = source_data.get("bucketName", "Unknown")
            path = source_data.get("path", "")
            aws_access = source_data.get("awsAccessKey", {})
            access_key_id = (
                aws_access.get("accessKeyId", "")[:8] + "..."
                if aws_access.get("accessKeyId")
                else ""
            )
            result = f"Bucket: {bucket}"
            if path:
                result += f", Path: {path}"
            if access_key_id:
                result += f", Access Key: {access_key_id}"
            return result

        elif source_type == "POSIX":
            root_dir = source_data.get("rootDirectory", "Unknown")
            return f"Directory: {root_dir}"

        elif source_type == "HTTP":
            list_url = source_data.get("listUrl", "Unknown")
            return f"List URL: {list_url}"

        elif source_type == "AZURE_BLOB":
            container = source_data.get("container", "Unknown")
            storage_account = source_data.get("storageAccount", "")
            result = f"Container: {container}"
            if storage_account:
                result += f", Account: {storage_account}"
            return result

        else:
            # Fallback to JSON format for unknown types
            return str(source_data)

    @staticmethod
    def _format_sink_details(sink_type: str, sink_data: Dict[str, Any]) -> str:
        """Format sink details in human-readable format"""
        if not sink_data:
            return "⚠️ Not configured"

        if sink_type == "GCS":
            bucket = sink_data.get("bucketName", "Unknown")
            path = sink_data.get("path", "")
            return f"Bucket: {bucket}" + (f", Path: {path}" if path else "")

        elif sink_type == "POSIX":
            root_dir = sink_data.get("rootDirectory", "Unknown")
            return f"Directory: {root_dir}"

        else:
            # Fallback to JSON format for unknown types
            return str(sink_data)


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
    """Storage Transfer Job 메인 모델 (Union Field 제약 적용)"""

    full_name = StringType()
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
    creation_time = StringType(deserialize_from="creationTime")
    last_modification_time = StringType(deserialize_from="lastModificationTime")
    deletion_time = StringType(
        deserialize_from="deletionTime", serialize_when_none=False
    )
    latest_operation_name = StringType(
        deserialize_from="latestOperationName", serialize_when_none=False
    )

    # Display information (calculated by Manager)
    source_type = StringType(serialize_when_none=False)  # GCS, S3, Azure, HTTP, POSIX
    sink_type = StringType(serialize_when_none=False)  # GCS, POSIX
    schedule_display = StringType(serialize_when_none=False)
    transfer_options_display = StringType(serialize_when_none=False)

    # Union Field information (active source/sink details)
    active_source_details = StringType(serialize_when_none=False)
    active_sink_details = StringType(serialize_when_none=False)

    def validate(self, raw_data=None, context=None):
        """Flexible validation (warning log approach)"""
        super().validate(raw_data, context)

        if self.transfer_spec:
            # Union Field validation and active configuration check
            active_config = self.transfer_spec.validate_union_fields_with_warnings()

            # Set calculated fields
            if not self.source_type:
                self.source_type = self.transfer_spec.get_source_type()
            if not self.sink_type:
                self.sink_type = self.transfer_spec.get_sink_type()

            # Set active source/sink detail information (human-readable format)
            if active_config["source_data"] and self.source_type:
                self.active_source_details = TransferSpec._format_source_details(
                    self.source_type, active_config["source_data"]
                )
            if active_config["sink_data"] and self.sink_type:
                self.active_sink_details = TransferSpec._format_sink_details(
                    self.sink_type, active_config["sink_data"]
                )

            # Additional logging (for debugging)
            if active_config["active_source"] and active_config["active_sink"]:
                _LOGGER.info(
                    f"Transfer job validated successfully: "
                    f"{active_config['active_source']} -> {active_config['active_sink']}"
                )

    def reference(self):
        return {
            "resource_id": f"https://storagetransfer.googleapis.com/v1/{self.full_name}",
            "external_link": f"https://console.cloud.google.com/transfer/jobs/transferJobs%2F{self.name}?project={self.project}",
        }
