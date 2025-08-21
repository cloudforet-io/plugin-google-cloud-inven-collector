import logging
import time

from spaceone.inventory.connector.cloud_run.cloud_run_v1 import CloudRunV1Connector
from spaceone.inventory.connector.cloud_run.cloud_run_v2 import CloudRunV2Connector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.cloud_run.worker_pool.cloud_service import (
    WorkerPoolResource,
    WorkerPoolResponse,
)
from spaceone.inventory.model.cloud_run.worker_pool.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_run.worker_pool.data import WorkerPool

_LOGGER = logging.getLogger(__name__)


class CloudRunWorkerPoolManager(GoogleCloudManager):
    connector_name = ["CloudRunV1Connector", "CloudRunV2Connector"]
    cloud_service_types = CLOUD_SERVICE_TYPES

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "CloudRun"
        self.cloud_service_type = "WorkerPool"
        self.cloud_run_v1_connector = None
        self.cloud_run_v2_connector = None

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
        
        self.cloud_run_v1_connector = CloudRunV1Connector(**params)
        self.cloud_run_v2_connector = CloudRunV2Connector(**params)

        # Cloud Run v1 API를 사용하여 location 목록 조회
        locations = self.cloud_run_v1_connector.list_locations()
        location_ids = [location.get('locationId') for location in locations if location.get('locationId')]
        
        # 각 location에서 Cloud Run Worker Pools 조회
        for location_id in location_ids:
            parent = f"projects/{project_id}/locations/{location_id}"
            
            try:                
                # Cloud Run Worker Pools 조회
                worker_pools = self.cloud_run_v2_connector.list_worker_pools(parent)
                if worker_pools:
                    _LOGGER.debug(f"Found {len(worker_pools)} worker pools in {location_id}")
                    for worker_pool in worker_pools:
                        try:
                            # 각 Worker Pool의 Revisions 정보도 조회
                            worker_pool_name = worker_pool.get("name")
                            if worker_pool_name:
                                revisions = self.cloud_run_v2_connector.list_worker_pool_revisions(worker_pool_name)
                                worker_pool["revisions"] = revisions
                                worker_pool["revision_count"] = len(revisions)
                            
                            cloud_service = self._make_cloud_run_worker_pool_info(worker_pool, project_id, location_id)
                            collected_cloud_services.append(WorkerPoolResponse({"resource": cloud_service}))
                        except Exception as e:
                            _LOGGER.error(f"Failed to process worker pool {worker_pool.get('name', 'unknown')}: {str(e)}")
                            error_response = self.generate_resource_error_response(e, self.cloud_service_group, "WorkerPool", worker_pool.get('name', 'unknown'))
                            error_responses.append(error_response)
                        
            except Exception as e:
                # 특정 location에서 API 호출이 실패해도 다른 location은 계속 확인
                _LOGGER.debug(f"Failed to query {location_id}: {str(e)}")
                continue

        _LOGGER.debug(
            f"** [{self.cloud_service_group}] {self.cloud_service_type} END ** "
            f"({time.time() - start_time:.2f}s)"
        )

        return collected_cloud_services, error_responses

    def _make_cloud_run_worker_pool_info(self, worker_pool: dict, project_id: str, location_id: str) -> WorkerPoolResource:
        """Cloud Run Worker Pool 정보를 생성합니다."""
        worker_pool_name = worker_pool.get("name", "")

        if "/" in worker_pool_name:
            worker_pool_short_name = worker_pool_name.split("/")[-1]
        else:
            worker_pool_short_name = worker_pool_name
        
        formatted_worker_pool_data = {
            "name": worker_pool.get("name"),
            "uid": worker_pool.get("uid"),
            "generation": worker_pool.get("generation"),
            "labels": worker_pool.get("labels", {}),
            "annotations": worker_pool.get("annotations", {}),
            "createTime": worker_pool.get("createTime"),
            "updateTime": worker_pool.get("updateTime"),
            "deleteTime": worker_pool.get("deleteTime"),
            "expireTime": worker_pool.get("expireTime"),
            "creator": worker_pool.get("creator"),
            "lastModifier": worker_pool.get("lastModifier"),
            "client": worker_pool.get("client"),
            "launchStage": worker_pool.get("launchStage"),
            # "template": worker_pool.get("template", {}),
            "observedGeneration": worker_pool.get("observedGeneration"),
            "terminalCondition": worker_pool.get("terminalCondition"),
            "conditions": worker_pool.get("conditions", []),
            "etag": worker_pool.get("etag"),
            "revisions": [ 
                {
                    "name": revision.get("name"),
                    "uid": revision.get("uid"),
                    "service": revision.get("service"),
                    "generation": revision.get("generation"),
                    "createTime": revision.get("createTime"),
                    "updateTime": revision.get("updateTime"),
                    "conditions": revision.get("conditions", []),
                }
                for revision in worker_pool.get("revisions", [])
            ],
            "revision_count": worker_pool.get("revision_count", 0),
        }
        
        worker_pool_data = WorkerPool(formatted_worker_pool_data, strict=False)
        
        return WorkerPoolResource({
            "name": worker_pool_short_name,
            "account": project_id,
            "region_code": location_id,
            "data": worker_pool_data,
            "reference": ReferenceModel({
                "resource_id": worker_pool_data.uid,
                "external_link": f"https://console.cloud.google.com/run/worker-pools/details/{worker_pool_data.name}"
            })
        })
