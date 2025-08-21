import logging
import time

from spaceone.inventory.connector.cloud_run.cloud_run_v1 import CloudRunV1Connector
from spaceone.inventory.connector.cloud_run.cloud_run_v2 import CloudRunV2Connector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.cloud_run.job.cloud_service import (
    JobResource,
    JobResponse,
)
from spaceone.inventory.model.cloud_run.job.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)

_LOGGER = logging.getLogger(__name__)


class CloudRunJobManager(GoogleCloudManager):
    connector_name = ["CloudRunV1Connector", "CloudRunV2Connector"]
    cloud_service_types = CLOUD_SERVICE_TYPES

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "CloudRun"
        self.cloud_service_type = "Job"
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
        
        # 각 location에서 Cloud Run Jobs 조회
        for location_id in location_ids:
            parent = f"projects/{project_id}/locations/{location_id}"
            
            try:                
                # Cloud Run Jobs 조회
                jobs = self.cloud_run_v2_connector.list_jobs(parent)
                if jobs:
                    _LOGGER.debug(f"Found {len(jobs)} jobs in {location_id}")
                    for job in jobs:
                        try:
                            # 각 Job의 Executions 정보도 조회
                            job_name = job.get("name")
                            if job_name:
                                executions = self.cloud_run_v2_connector.list_executions(job_name)
                                formatted_executions = []
                                
                                # 각 Execution의 Tasks 정보도 조회
                                for execution in executions:
                                    execution_name = execution.get("name")
                                    formatted_execution = {
                                        "name": execution.get("name"),
                                        "uid": execution.get("uid"),
                                        "creator": execution.get("creator"),
                                        "job": execution.get("job"),
                                        "tasks": [],
                                        "task_count": 0
                                    }
                                    
                                    if execution_name:
                                        tasks = self.cloud_run_v2_connector.list_tasks(execution_name)
                                        formatted_tasks = []
                                        for task in tasks:
                                            formatted_task = {
                                                "name": task.get("name"),
                                                "uid": task.get("uid"),
                                                "job": task.get("job"),
                                                "execution": task.get("execution")
                                            }
                                            formatted_tasks.append(formatted_task)
                                        
                                        formatted_execution["tasks"] = formatted_tasks
                                        formatted_execution["task_count"] = len(formatted_tasks)
                                    
                                    formatted_executions.append(formatted_execution)
                                
                                job["executions"] = formatted_executions
                                job["execution_count"] = len(formatted_executions)
                            
                            cloud_service = self._make_cloud_run_job_info(job, project_id, location_id)
                            collected_cloud_services.append(JobResponse({"resource": cloud_service}))
                        except Exception as e:
                            _LOGGER.error(f"Failed to process job {job.get('name', 'unknown')}: {str(e)}")
                            error_response = self.generate_resource_error_response(e, self.cloud_service_group, "Job", job.get('name', 'unknown'))
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

    def _make_cloud_run_job_info(self, job: dict, project_id: str, location_id: str) -> JobResource:
        """Cloud Run Job 정보를 생성합니다."""
        job_name = job.get("name", "")
        
        if "/" in job_name:
            job_short_name = job_name.split("/")[-1]
        else:
            job_short_name = job_name
        
        formatted_job_data = {
            "name": job.get("name"),
            "uid": job.get("uid"),
            "generation": job.get("generation"),
            "labels": job.get("labels", {}),
            "annotations": job.get("annotations", {}),
            "createTime": job.get("createTime"),
            "updateTime": job.get("updateTime"),
            "deleteTime": job.get("deleteTime"),
            "expireTime": job.get("expireTime"),
            "creator": job.get("creator"),
            "lastModifier": job.get("lastModifier"),
            "client": job.get("client"),
            "launchStage": job.get("launchStage"),
            # "template": job.get("template", {}),
            "observedGeneration": job.get("observedGeneration"),
            "terminalCondition": job.get("terminalCondition"),
            "conditions": job.get("conditions", []),
            "etag": job.get("etag"),
            "executions": job.get("executions", []),
            "execution_count": job.get("execution_count", 0),
            "latestCreatedExecution": job.get("latestCreatedExecution"),
        }
        
        from spaceone.inventory.model.cloud_run.job.data import Job
        job_data = Job(formatted_job_data, strict=False)
        
        return JobResource({
            "name": job_short_name,
            "account": project_id,
            "region_code": location_id,
            "data": job_data,
            "reference": ReferenceModel({
                "resource_id": job_data.uid,
                "external_link": f"https://console.cloud.google.com/run/jobs/details/{job_data.name}"
            })
        })
