import logging
import time

from spaceone.inventory.connector.cloud_run.cloud_run_v1 import CloudRunV1Connector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.cloud_run.worker_pool_v1.cloud_service import (
    WorkerPoolV1Resource,
    WorkerPoolV1Response,
)
from spaceone.inventory.model.cloud_run.worker_pool_v1.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_run.worker_pool_v1.data import WorkerPoolV1

_LOGGER = logging.getLogger(__name__)


class CloudRunWorkerPoolV1Manager(GoogleCloudManager):
    connector_name = "CloudRunV1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug("** Cloud Run WorkerPool V1 START **")
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
        cloud_run_v1_conn: CloudRunV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        # Get lists that relate with worker pools through Google Cloud API
        # V1은 namespace 기반이므로 단일 namespace로 모든 리소스 조회 가능
        try:
            namespace = f"namespaces/{project_id}"
            worker_pools = cloud_run_v1_conn.list_worker_pools(namespace)
            
            for worker_pool in worker_pools:
                # V1에서는 location 정보가 metadata에 포함되어 있을 수 있음
                location_id = (
                    worker_pool.get("metadata", {}).get("labels", {}).get("cloud.googleapis.com/location") or
                    worker_pool.get("metadata", {}).get("namespace", "").split("/")[-1] or
                    "us-central1"  # default location
                )
                worker_pool["_location"] = location_id
                
                # Get revisions for each worker pool (V1에서는 workerPool 라벨 사용)
                try:
                    revisions = cloud_run_v1_conn.list_revisions(namespace)
                    # Filter revisions for this worker pool - 올바른 라벨 사용
                    worker_pool_name = worker_pool.get("metadata", {}).get("name", "")
                    worker_pool_revisions = [
                        rev for rev in revisions
                        if rev.get("metadata", {}).get("labels", {}).get("run.googleapis.com/workerPool") == worker_pool_name
                    ]
                    
                    # 복잡한 중첩 구조 대신 필요한 정보만 추출하여 단순화
                    simplified_revisions = []
                    for rev in worker_pool_revisions:
                        metadata = rev.get("metadata", {})
                        status = rev.get("status", {})
                        simplified_revision = {
                            "name": metadata.get("name"),
                            "uid": metadata.get("uid"),
                            "generation": metadata.get("generation"),
                            "create_time": metadata.get("creationTimestamp"),
                            "update_time": status.get("lastTransitionTime"),
                            "worker_pool": metadata.get("labels", {}).get("run.googleapis.com/workerPool"),
                            "conditions": [
                                {
                                    "type": cond.get("type"),
                                    "status": cond.get("status"),
                                    "reason": cond.get("reason")
                                }
                                for cond in status.get("conditions", [])
                                if isinstance(cond, dict)
                            ]
                        }
                        simplified_revisions.append(simplified_revision)
                    
                    worker_pool["revisions"] = simplified_revisions
                    worker_pool["revision_count"] = len(simplified_revisions)
                except Exception as e:
                    _LOGGER.warning(f"Failed to get revisions for worker pool: {str(e)}")
                    worker_pool["revisions"] = []
                    worker_pool["revision_count"] = 0
        except Exception as e:
            _LOGGER.warning(f"Failed to query worker pools from namespace: {str(e)}")
            worker_pools = []

        for worker_pool in worker_pools:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                worker_pool_id = worker_pool.get("metadata", {}).get("name", "")
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
                worker_pool_data = WorkerPoolV1(worker_pool, strict=False)

                worker_pool_resource = WorkerPoolV1Resource(
                    {
                        "name": worker_pool_id,
                        "account": project_id,
                        "region_code": location_id,
                        "data": worker_pool_data,
                        "reference": ReferenceModel(
                            {
                                "resource_id": getattr(worker_pool_data, 'metadata', {}).get('uid') or worker_pool_id,
                                "external_link": f"https://console.cloud.google.com/run/workerpools/details/{location_id}/{worker_pool_id}?project={project_id}",
                            }
                        ),
                    },
                    strict=False,
                )

                collected_cloud_services.append(
                    WorkerPoolV1Response({"resource": worker_pool_resource})
                )

            except Exception as e:
                _LOGGER.error(f"Failed to process worker pool {worker_pool_id}: {str(e)}")
                error_response = self.generate_resource_error_response(
                    e, "WorkerPoolV1", "CloudRun", worker_pool_id
                )
                error_responses.append(error_response)

        _LOGGER.debug(f"** Cloud Run WorkerPool V1 END ** ({time.time() - start_time:.2f}s)")

        return collected_cloud_services, error_responses
