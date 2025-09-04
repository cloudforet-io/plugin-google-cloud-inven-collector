import logging
import time

from spaceone.inventory.conf.cloud_service_conf import REGION_INFO
from spaceone.inventory.connector.cloud_build.cloud_build_v1 import (
    CloudBuildV1Connector,
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


class CloudBuildWorkerPoolV1Manager(GoogleCloudManager):
    connector_name = "CloudBuildV1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug("** Cloud Build WorkerPool START **")
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
        worker_pool_id = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        cloud_build_v1_conn: CloudBuildV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        # Get lists that relate with worker pools through Google Cloud API using REGION_INFO fallback
        all_worker_pools = []
        parent = f"projects/{project_id}"
        
        # V1에서는 locations API가 지원되지 않으므로 REGION_INFO를 사용
        locations = [
            {
                "locationId": region_id,
                "name": f"{parent}/locations/{region_id}",
                "displayName": REGION_INFO[region_id]["name"]
            }
            for region_id in REGION_INFO.keys()
            if region_id != "global"
        ]
        
        for location in locations:
            location_id = location.get("locationId", "")
            if location_id:
                try:
                    parent = f"projects/{project_id}/locations/{location_id}"
                    worker_pools = cloud_build_v1_conn.list_location_worker_pools(
                        parent
                    )
                    for worker_pool in worker_pools:
                        worker_pool["_location"] = location_id
                    all_worker_pools.extend(worker_pools)
                except Exception as e:
                    _LOGGER.debug(
                        f"Failed to query worker pools in location {location_id}: {str(e)}"
                    )
                    continue

        _LOGGER.info(
            f"cloud worker pool all_worker_pools length: {len(all_worker_pools)}"
        )
        for worker_pool in all_worker_pools:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                worker_pool_id = worker_pool.get("name", "")
                worker_pool_name = (
                    self.get_param_in_url(worker_pool_id, "workerPools")
                    if worker_pool_id
                    else ""
                )
                location_id = worker_pool.get("_location", "")
                region = self.parse_region_from_zone(location_id) if location_id else ""

                ##################################
                # 2. Make Base Data
                ##################################
                worker_pool.update(
                    {
                        "project": project_id,
                        "location": location_id,
                        "region": region,
                    }
                )

                ##################################
                # 3. Make Return Resource
                ##################################
                worker_pool_data = WorkerPool(worker_pool, strict=False)

                worker_pool_resource = WorkerPoolResource(
                    {
                        "name": worker_pool_name,
                        "account": project_id,
                        "region_code": location_id,
                        "data": worker_pool_data,
                        "reference": ReferenceModel(
                            {
                                "resource_id": worker_pool_data.name,
                                "external_link": f"https://console.cloud.google.com/cloud-build/worker-pools?project={project_id}",
                            }
                        ),
                    },
                    strict=False,
                )

                collected_cloud_services.append(
                    WorkerPoolResponse({"resource": worker_pool_resource})
                )

            except Exception as e:
                _LOGGER.error(
                    f"Failed to process worker pool {worker_pool_id}: {str(e)}"
                )
                error_response = self.generate_resource_error_response(
                    e, "CloudBuild", "WorkerPool", worker_pool_id
                )
                error_responses.append(error_response)

        _LOGGER.debug(
            f"** Cloud Build WorkerPool END ** ({time.time() - start_time:.2f}s)"
        )

        return collected_cloud_services, error_responses
