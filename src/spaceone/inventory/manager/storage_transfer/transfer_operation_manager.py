import logging
import time
from datetime import datetime
from typing import List, Tuple

from spaceone.inventory.connector.storage_transfer.transfer_job import (
    StorageTransferConnector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.storage_transfer.transfer_operation.cloud_service import (
    TransferOperationResource,
    TransferOperationResponse,
)
from spaceone.inventory.model.storage_transfer.transfer_operation.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.storage_transfer.transfer_operation.data import (
    TransferOperation,
)

_LOGGER = logging.getLogger(__name__)


class StorageTransferOperationManager(GoogleCloudManager):
    connector_name = "StorageTransferConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(
        self, params
    ) -> Tuple[List[TransferOperationResponse], List]:
        _LOGGER.debug("** Storage Transfer Operation START **")
        start_time = time.time()
        """
        Args:
            params:
                - options
                - schema
                - secret_data
                - filter
                - zones
        Response:
            CloudServiceResponse/ErrorResourceResponse
        """
        collected_cloud_services = []
        error_responses = []
        operation_name = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        ##################################
        # 0. Gather All Related Resources
        ##################################
        storage_transfer_conn: StorageTransferConnector = self.locator.get_connector(
            self.connector_name, **params
        )

        # Get transfer operations
        operations = storage_transfer_conn.list_transfer_operations()

        for operation in operations:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                operation_name = operation.get("name", "")
                metadata = operation.get("metadata", {})

                ##################################
                # 2. Make Base Data
                ##################################
                # Duration 계산
                duration = self._calculate_duration(metadata)

                # 라벨 변환
                labels = self.convert_labels_format(operation.get("labels", {}))

                # 데이터 업데이트
                operation.update(
                    {
                        "project_id": project_id,
                        "transfer_job_name": metadata.get("transferJobName", ""),
                        "duration": duration,
                        "labels": labels,
                    }
                )

                operation_data = TransferOperation(operation, strict=False)

                ##################################
                # 3. Make Return Resource
                ##################################
                operation_resource = TransferOperationResource(
                    {
                        "name": operation_name,
                        "account": project_id,
                        "tags": labels,
                        "region_code": "global",
                        "instance_type": metadata.get("status", ""),
                        "instance_size": metadata.get("counters", {}).get(
                            "bytesCopiedToSink", 0
                        ),
                        "data": operation_data,
                        "reference": ReferenceModel(operation_data.reference()),
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
                    TransferOperationResponse({"resource": operation_resource})
                )

            except Exception as e:
                _LOGGER.error(
                    f"[collect_cloud_service] operation => {operation_name}, error => {e}",
                    exc_info=True,
                )
                error_response = self.generate_resource_error_response(
                    e, "StorageTransfer", "TransferOperation", operation_name
                )
                error_responses.append(error_response)

        _LOGGER.debug(
            f"** Storage Transfer Operation Finished {time.time() - start_time} Seconds **"
        )
        return collected_cloud_services, error_responses

    @staticmethod
    def _calculate_duration(metadata: dict) -> str:
        """실행 시간을 계산합니다."""
        start_time_str = metadata.get("startTime")
        end_time_str = metadata.get("endTime")

        if not start_time_str:
            return ""

        try:
            start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))

            if end_time_str:
                end_time = datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))
                duration = end_time - start_time

                # 시간 포맷팅
                total_seconds = int(duration.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)

                if hours > 0:
                    return f"{hours}h {minutes}m {seconds}s"
                elif minutes > 0:
                    return f"{minutes}m {seconds}s"
                else:
                    return f"{seconds}s"
            else:
                # 진행 중인 작업
                now = datetime.now(start_time.tzinfo)
                duration = now - start_time
                total_seconds = int(duration.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)

                if hours > 0:
                    return f"{hours}h {minutes}m (ongoing)"
                elif minutes > 0:
                    return f"{minutes}m {seconds}s (ongoing)"
                else:
                    return f"{seconds}s (ongoing)"

        except Exception:
            return ""
