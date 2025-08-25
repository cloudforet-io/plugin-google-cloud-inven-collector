import logging
import time

from spaceone.inventory.connector.cloud_build.cloud_build_v1 import (
    CloudBuildV1Connector,
)
from spaceone.inventory.connector.cloud_build.cloud_build_v2 import (
    CloudBuildV2Connector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.cloud_build.worker_pool.cloud_service import (
    WorkerPoolResource,
    WorkerPoolResponse,
)
from spaceone.inventory.model.cloud_build.worker_pool.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_build.worker_pool.data import WorkerPool

_LOGGER = logging.getLogger(__name__)


class CloudBuildWorkerPoolManager(GoogleCloudManager):
    connector_name = "CloudBuildV1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "CloudBuild"
        self.cloud_service_type = "WorkerPool"

    def collect_cloud_service(self, params):
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
        _LOGGER.debug(
            f"** [{self.cloud_service_group}] {self.cloud_service_type} START **"
        )

        start_time = time.time()

        collected_cloud_services = []
        error_responses = []

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]
        
        self.cloud_build_v1_connector = CloudBuildV1Connector(**params)
        self.cloud_build_v2_connector = CloudBuildV2Connector(**params)

        # Location별 worker pools 조회
        try:
            locations = self.cloud_build_v2_connector.list_locations(f"projects/{project_id}")
            for location in locations:
                location_id = location.get("locationId")
                if location_id:
                    try:
                        parent = f"projects/{project_id}/locations/{location_id}"
                        worker_pools = self.cloud_build_v1_connector.list_location_worker_pools(parent)
                        if worker_pools:
                            _LOGGER.debug(f"Found {len(worker_pools)} worker pools in {location_id}")
                            for worker_pool in worker_pools:
                                try:
                                    cloud_service = self._make_cloud_build_worker_pool_info(worker_pool, project_id, location_id)
                                    collected_cloud_services.append(WorkerPoolResponse({"resource": cloud_service}))
                                except Exception as e:
                                    _LOGGER.error(f"Failed to process worker pool {worker_pool.get('name', 'unknown')}: {str(e)}")
                                    error_response = self.generate_resource_error_response(e, self.cloud_service_group, "WorkerPool", worker_pool.get('name', 'unknown'))
                                    error_responses.append(error_response)
                    except Exception as e:
                        _LOGGER.debug(f"Failed to query worker pools in {location_id}: {str(e)}")
                        continue
        except Exception as e:
            _LOGGER.error(f"Failed to list locations: {str(e)}")

        _LOGGER.debug(
            f"** [{self.cloud_service_group}] {self.cloud_service_type} END ** "
            f"({time.time() - start_time:.2f}s)"
        )

        return collected_cloud_services, error_responses

    def _make_cloud_build_worker_pool_info(self, worker_pool: dict, project_id: str, location_id: str) -> WorkerPoolResource:
        """Cloud Build Worker Pool 정보를 생성합니다."""
        worker_pool_name = worker_pool.get("name", "")
        
        if "/" in worker_pool_name:
            worker_pool_short_name = worker_pool_name.split("/")[-1]
        else:
            worker_pool_short_name = worker_pool_name
        
        formatted_worker_pool_data = {
            "name": worker_pool.get("name"),
            "displayName": worker_pool.get("displayName"),
            "uid": worker_pool.get("uid"),
            "annotations": worker_pool.get("annotations", {}),
            "createTime": worker_pool.get("createTime"),
            "updateTime": worker_pool.get("updateTime"),
            "deleteTime": worker_pool.get("deleteTime"),
            "state": worker_pool.get("state"),
            "privatePoolV1Config": worker_pool.get("privatePoolV1Config", {}),
            "etag": worker_pool.get("etag"),
        }
        
        worker_pool_data = WorkerPool(formatted_worker_pool_data, strict=False)
        
        return WorkerPoolResource({
            "name": worker_pool_short_name,
            "account": project_id,
            "region_code": location_id,
            "data": worker_pool_data,
            "reference": ReferenceModel({
                "resource_id": worker_pool_data.name,
                "external_link": f"https://console.cloud.google.com/cloud-build/worker-pools/details/{location_id}/{worker_pool_short_name}?project={project_id}"
            })
        })
