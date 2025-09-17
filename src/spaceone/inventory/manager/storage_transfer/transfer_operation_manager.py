import logging
import time
from datetime import datetime
from typing import Dict, List, Tuple

from spaceone.inventory.connector.storage_transfer.storage_transfer_v1 import (
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

        collected_cloud_services = []
        error_responses = []
        operation_name = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        try:
            ##################################
            # 0. Gather All Related Resources
            ##################################
            storage_transfer_conn: StorageTransferConnector = (
                self.locator.get_connector(self.connector_name, **params)
            )

            # Get transfer operations
            operations = storage_transfer_conn.list_transfer_operations()
            _LOGGER.info(f"Found {len(operations)} transfer operations to process")

            for operation in operations:
                try:
                    ##################################
                    # 1. Set Basic Information
                    ##################################
                    operation_name = operation.get("name", "")
                    operation_id = (
                        operation_name.split("/")[-1]
                        if "/" in operation_name
                        else operation_name
                    )
                    metadata = operation.get("metadata", {})
                    transfer_job_name = metadata.get("transferJobName", "")
                    transfer_job_id = (
                        transfer_job_name.split("/")[-1]
                        if "/" in transfer_job_name
                        else transfer_job_name
                    )

                    ##################################
                    # 2. Make Base Data
                    ##################################
                    # Calculate Duration
                    duration = self._calculate_duration(metadata)

                    operation.update(
                        {
                            "name": operation_id,
                            "full_name": operation_name,
                            "project": project_id,
                            "transfer_job_id": transfer_job_id,
                            "transfer_job_name": transfer_job_name,
                            "duration": duration,
                        }
                    )

                    operation_data = TransferOperation(operation, strict=False)

                    ##################################
                    # 3. Make Return Resource
                    ##################################
                    operation_resource = TransferOperationResource(
                        {
                            "name": operation_id,
                            "account": project_id,
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
                        f"Failed to process transfer operation {operation_name}: {e}",
                        exc_info=True,
                    )
                    error_response = self.generate_resource_error_response(
                        e, "StorageTransfer", "TransferOperation", operation_name
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(
                f"Failed to collect Storage Transfer Operations: {e}", exc_info=True
            )
            error_response = self.generate_resource_error_response(
                e, "StorageTransfer", "TransferOperation", "collection"
            )
            error_responses.append(error_response)

        _LOGGER.debug(
            f"** Storage Transfer Operation Finished {time.time() - start_time} Seconds **"
        )

        return collected_cloud_services, error_responses

    @staticmethod
    def _parse_iso_datetime(datetime_str: str) -> datetime:
        # Convert Z to +00:00
        normalized_str = datetime_str.replace("Z", "+00:00")

        # Convert nanoseconds (9 digits) to microseconds (6 digits)
        if "." in normalized_str and "+" in normalized_str:
            # Separate decimal part and timezone part
            datetime_part, tz_part = normalized_str.rsplit("+", 1)
            if "." in datetime_part:
                main_part, fractional_part = datetime_part.split(".", 1)
                # Convert 9-digit nanoseconds to 6-digit microseconds
                if len(fractional_part) > 6:
                    fractional_part = fractional_part[:6]
                normalized_str = f"{main_part}.{fractional_part}+{tz_part}"

        return datetime.fromisoformat(normalized_str)

    @staticmethod
    def _calculate_duration(metadata: Dict) -> str:
        """Calculate execution time"""
        start_time_str = metadata.get("startTime")
        end_time_str = metadata.get("endTime")

        if not start_time_str:
            return ""

        try:
            start_time = StorageTransferOperationManager._parse_iso_datetime(
                start_time_str
            )

            if end_time_str:
                end_time = StorageTransferOperationManager._parse_iso_datetime(
                    end_time_str
                )
                duration = end_time - start_time

                # Format time
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
                # In progress job
                now = datetime.now(start_time.tzinfo)
                duration = now - start_time
                total_seconds = int(duration.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)

                if hours > 0:
                    return f"{hours}h {minutes}m"
                elif minutes > 0:
                    return f"{minutes}m {seconds}s"
                else:
                    return f"{seconds}s"

        except Exception as e:
            _LOGGER.warning(f"Failed to parse datetime: {e}")
            return ""
