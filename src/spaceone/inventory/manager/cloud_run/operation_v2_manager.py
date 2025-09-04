import logging
import time

from spaceone.inventory.conf.cloud_service_conf import REGION_INFO
from spaceone.inventory.connector.cloud_run.cloud_run_v2 import CloudRunV2Connector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.cloud_run.operation_v2.cloud_service import (
    OperationResource,
    OperationResponse,
)
from spaceone.inventory.model.cloud_run.operation_v2.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_run.operation_v2.data import OperationV2

_LOGGER = logging.getLogger(__name__)


class CloudRunOperationV2Manager(GoogleCloudManager):
    connector_name = "CloudRunV2Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug("** Cloud Run Operation V2 START **")
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
        operation_id = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        cloud_run_v2_conn: CloudRunV2Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        # Get lists that relate with operations through Google Cloud API
        all_operations = []
        try:
            # REGION_INFO에서 모든 위치 사용 (global 제외)
            for region_id in REGION_INFO.keys():
                if region_id == "global":
                    continue
                location_id = region_id
                try:
                    parent = f"projects/{project_id}/locations/{location_id}"
                    operations = cloud_run_v2_conn.list_operations(parent)
                    for operation in operations:
                        operation["_location"] = location_id
                    all_operations.extend(operations)
                except Exception as e:
                    _LOGGER.debug(
                        f"Failed to query operations in location {location_id}: {str(e)}"
                    )
                    continue
        except Exception as e:
            _LOGGER.warning(f"Failed to iterate REGION_INFO: {str(e)}")

        for operation in all_operations:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                operation_id = operation.get("name", "")
                operation_name = self.get_param_in_url(operation_id, "operations") if operation_id else ""
                location_id = operation.get("_location", "")
                region = self.parse_region_from_zone(location_id) if location_id else ""

                ##################################
                # 2. Make Base Data
                ##################################
                # Operation V2 데이터 구조에 맞게 변환
                operation_data_dict = {
                    "name": operation_id,
                    "done": operation.get("done", False),
                    "metadata": operation.get("metadata", {}),
                    "response": operation.get("response", {}),
                    "error": operation.get("error", {}),
                    "project": project_id,
                    "location": location_id,
                    "region": region,
                    
                    # 추가 필드들 추출
                    "operation_type": operation.get("metadata", {}).get("@type", "").split(".")[-1] if operation.get("metadata", {}).get("@type") else "Unknown",
                    "target_resource": operation.get("metadata", {}).get("target", ""),
                    "status": "Completed" if operation.get("done") else "Running",
                    "progress": 100 if operation.get("done") else 50,
                    "create_time": operation.get("metadata", {}).get("createTime"),
                    "end_time": operation.get("metadata", {}).get("endTime") if operation.get("done") else None,
                    "labels": {},
                    "annotations": {}
                }

                ##################################
                # 3. Make Return Resource
                ##################################
                operation_data = OperationV2(operation_data_dict, strict=False)

                operation_resource = OperationResource(
                    {
                        "name": operation_name,
                        "account": project_id,
                        "region_code": location_id,
                        "data": operation_data,
                        "reference": ReferenceModel(
                            {
                                "resource_id": operation_data.name,
                                "external_link": f"https://console.cloud.google.com/run/operations/details/{location_id}/{operation_name}?project={project_id}",
                            }
                        ),
                    },
                    strict=False,
                )

                collected_cloud_services.append(OperationResponse({"resource": operation_resource}))

            except Exception as e:
                _LOGGER.error(f"Failed to process operation {operation_id}: {str(e)}")
                error_response = self.generate_resource_error_response(
                    e, "Operation", "CloudRun", operation_id
                )
                error_responses.append(error_response)

        _LOGGER.debug(f"** Cloud Run Operation V2 END ** ({time.time() - start_time:.2f}s)")

        return collected_cloud_services, error_responses
