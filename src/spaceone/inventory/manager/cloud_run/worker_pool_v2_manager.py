import logging
import time

from spaceone.inventory.conf.cloud_service_conf import REGION_INFO
from spaceone.inventory.connector.cloud_run.cloud_run_v2 import CloudRunV2Connector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.cloud_run.worker_pool_v2.cloud_service import (
    WorkerPoolResource,
    WorkerPoolResponse,
)
from spaceone.inventory.model.cloud_run.worker_pool_v2.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_run.worker_pool_v2.data import (
    WorkerPool,
)

_LOGGER = logging.getLogger(__name__)


class CloudRunWorkerPoolV2Manager(GoogleCloudManager):
    connector_name = "CloudRunV2Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug("** Cloud Run Worker Pool V2 START **")
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
        cloud_run_v2_conn: CloudRunV2Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        # Get lists that relate with worker pools through Google Cloud API
        all_worker_pools = []
        try:
            # REGION_INFO에서 모든 위치 사용 (global 제외)
            for region_id in REGION_INFO.keys():
                if region_id == "global":
                    continue
                location_id = region_id
                try:
                    parent = f"projects/{project_id}/locations/{location_id}"
                    worker_pools = cloud_run_v2_conn.list_worker_pools(parent)
                    for worker_pool in worker_pools:
                        worker_pool["_location"] = location_id
                        # Get worker pool revisions
                        worker_pool_name = worker_pool.get("name")
                        if worker_pool_name:
                            try:
                                revisions = cloud_run_v2_conn.list_worker_pool_revisions(
                                    worker_pool_name
                                )
                                worker_pool["revisions"] = revisions
                                worker_pool["revision_count"] = len(revisions)
                            except Exception as e:
                                _LOGGER.warning(
                                    f"Failed to get revisions for worker pool {worker_pool_name}: {str(e)}"
                                )
                                worker_pool["revisions"] = []
                                worker_pool["revision_count"] = 0
                    all_worker_pools.extend(worker_pools)
                except Exception as e:
                    _LOGGER.debug(
                        f"Failed to query worker pools in location {location_id}: {str(e)}"
                    )
                    continue
        except Exception as e:
            _LOGGER.warning(f"Failed to iterate REGION_INFO: {str(e)}")

        for worker_pool in all_worker_pools:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                worker_pool_id = worker_pool.get("name", "")
                worker_pool_name = (
                    self.get_param_in_url(worker_pool_id, "workerPools") if worker_pool_id else ""
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
                                "external_link": f"https://console.cloud.google.com/run/workerpools/details/{location_id}/{worker_pool_name}?project={project_id}",
                            }
                        ),
                    },
                    strict=False,
                )

                collected_cloud_services.append(WorkerPoolResponse({"resource": worker_pool_resource}))

            except Exception as e:
                _LOGGER.error(f"Failed to process worker pool {worker_pool_id}: {str(e)}")
                error_response = self.generate_resource_error_response(
                    e, "CloudRun", "WorkerPool", worker_pool_id
                )
                error_responses.append(error_response)

        _LOGGER.debug(f"** Cloud Run Worker Pool V2 END ** ({time.time() - start_time:.2f}s)")

        return collected_cloud_services, error_responses