import logging
import time
from typing import Dict, List, Tuple

from spaceone.inventory.connector.storage_transfer.storage_transfer_v1 import (
    StorageTransferConnector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.storage_transfer.transfer_job.cloud_service import (
    TransferJobResource,
    TransferJobResponse,
)
from spaceone.inventory.model.storage_transfer.transfer_job.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.storage_transfer.transfer_job.data import TransferJob

_LOGGER = logging.getLogger(__name__)


class StorageTransferManager(GoogleCloudManager):
    """Storage Transfer Job 리소스 관리자"""

    connector_name = "StorageTransferConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params) -> Tuple[List[TransferJobResponse], List]:
        """Storage Transfer Job 리소스를 수집합니다.

        Args:
            params: 수집 파라미터
                - options: 수집 옵션
                - schema: 스키마 정보
                - secret_data: 인증 정보
                - filter: 필터 조건
                - zones: 대상 영역

        Returns:
            수집된 CloudService 응답과 에러 응답의 튜플
        """
        _LOGGER.info("** Storage Transfer Job START **")
        start_time = time.time()

        collected_cloud_services = []
        error_responses = []
        transfer_job_name = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        try:
            ##################################
            # 0. Gather All Related Resources
            ##################################
            storage_transfer_conn: StorageTransferConnector = (
                self.locator.get_connector(self.connector_name, **params)
            )

            # Get transfer jobs only
            transfer_jobs = storage_transfer_conn.list_transfer_jobs()
            _LOGGER.info(f"Found {len(transfer_jobs)} transfer jobs to process")

            for transfer_job in transfer_jobs:
                try:
                    ##################################
                    # 1. Set Basic Information
                    ##################################
                    transfer_job_name = transfer_job.get("name", "")

                    ##################################
                    # 2. Make Base Data
                    ##################################
                    # 소스 및 싱크 타입 결정
                    transfer_spec = transfer_job.get("transferSpec", {})
                    source_type = self._determine_source_type(transfer_spec)
                    sink_type = self._determine_sink_type(transfer_spec)

                    # 스케줄 표시 문자열 생성
                    schedule_display = self._make_schedule_display(
                        transfer_job.get("schedule", {})
                    )

                    # Transfer options 표시 문자열 생성
                    transfer_options_display = self._make_transfer_options_display(
                        transfer_spec.get("transferOptions", {})
                    )

                    # 라벨 변환
                    labels = self.convert_labels_format(transfer_job.get("labels", {}))

                    # 데이터 업데이트
                    transfer_job.update(
                        {
                            "source_type": source_type,
                            "sink_type": sink_type,
                            "schedule_display": schedule_display,
                            "transfer_options_display": transfer_options_display,
                            "labels": labels,
                        }
                    )

                    transfer_job.update(
                        {
                            "google_cloud_logging": self.set_google_cloud_logging(
                                "StorageTransfer",
                                "TransferJob",
                                project_id,
                                transfer_job_name,
                            ),
                        }
                    )

                    transfer_job_data = TransferJob(transfer_job, strict=False)

                    ##################################
                    # 3. Make Return Resource
                    ##################################
                    transfer_job_resource = TransferJobResource(
                        {
                            "name": transfer_job_name,
                            "account": project_id,
                            "tags": labels,
                            "region_code": "global",  # Storage Transfer는 글로벌 서비스
                            "instance_type": source_type,
                            "instance_size": 0,
                            "data": transfer_job_data,
                            "reference": ReferenceModel(transfer_job_data.reference()),
                        }
                    )

                    ##################################
                    # 4. Make Collected Region Code
                    ##################################
                    self.set_region_code("global")

                    ##################################
                    # 5. Make Resource Response Object
                    ##################################
                    collected_cloud_services.append(
                        TransferJobResponse({"resource": transfer_job_resource})
                    )

                except Exception as e:
                    _LOGGER.error(
                        f"Failed to process transfer job {transfer_job_name}: {e}",
                        exc_info=True,
                    )
                    error_response = self.generate_resource_error_response(
                        e, "StorageTransfer", "TransferJob", transfer_job_name
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(
                f"Failed to collect Storage Transfer Jobs: {e}", exc_info=True
            )
            error_response = self.generate_resource_error_response(
                e, "StorageTransfer", "TransferJob", "collection"
            )
            error_responses.append(error_response)

        # 수집 완료 로깅
        _LOGGER.debug(
            f"** Storage Transfer Job Finished {time.time() - start_time} Seconds **"
        )

        return collected_cloud_services, error_responses

    @staticmethod
    def _determine_source_type(transfer_spec: Dict) -> str:
        """전송 사양에서 소스 타입을 결정합니다.

        Args:
            transfer_spec: 전송 사양 딕셔너리

        Returns:
            소스 타입 문자열
        """
        if "gcsDataSource" in transfer_spec:
            return "GCS"
        elif "awsS3DataSource" in transfer_spec:
            return "S3"
        elif "azureBlobStorageDataSource" in transfer_spec:
            return "Azure"
        elif "httpDataSource" in transfer_spec:
            return "HTTP"
        elif "posixDataSource" in transfer_spec:
            return "POSIX"
        else:
            return "Unknown"

    @staticmethod
    def _determine_sink_type(transfer_spec: Dict) -> str:
        """전송 사양에서 싱크 타입을 결정합니다.

        Args:
            transfer_spec: 전송 사양 딕셔너리

        Returns:
            싱크 타입 문자열
        """
        if "gcsDataSink" in transfer_spec:
            return "GCS"
        elif "posixDataSink" in transfer_spec:
            return "POSIX"
        else:
            return "Unknown"

    @staticmethod
    def _make_schedule_display(schedule: Dict) -> str:
        """스케줄 정보를 표시용 문자열로 변환합니다.

        Args:
            schedule: 스케줄 정보 딕셔너리

        Returns:
            표시용 스케줄 문자열
        """
        if not schedule:
            return "One-time"

        repeat_interval = schedule.get("repeatInterval")
        if repeat_interval:
            # 예: "86400s" -> "Daily"
            if repeat_interval == "86400s":
                return "Daily"
            elif repeat_interval == "604800s":
                return "Weekly"
            else:
                return f"Every {repeat_interval}"

        start_date = schedule.get("scheduleStartDate")
        end_date = schedule.get("scheduleEndDate")

        if start_date and end_date:
            return f"Scheduled ({start_date} - {end_date})"
        elif start_date:
            return f"Scheduled (from {start_date})"
        else:
            return "Scheduled"

    @staticmethod
    def _make_transfer_options_display(transfer_options: Dict) -> str:
        """전송 옵션을 표시용 문자열로 변환합니다.

        Args:
            transfer_options: 전송 옵션 딕셔너리

        Returns:
            표시용 전송 옵션 문자열
        """
        if not transfer_options:
            return "Default"

        options = []
        if transfer_options.get("overwriteObjectsAlreadyExistingInSink"):
            options.append("Overwrite existing")
        if transfer_options.get("deleteObjectsUniqueInSink"):
            options.append("Delete unique in sink")
        if transfer_options.get("deleteObjectsFromSourceAfterTransfer"):
            options.append("Delete from source")

        return ", ".join(options) if options else "Default"
