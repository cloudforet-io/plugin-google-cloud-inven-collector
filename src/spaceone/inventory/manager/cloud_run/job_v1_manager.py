import logging
import time

from spaceone.inventory.connector.cloud_run.cloud_run_v1 import CloudRunV1Connector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.cloud_run.job_v1.cloud_service import (
    JobV1Resource,
    JobV1Response,
)
from spaceone.inventory.model.cloud_run.job_v1.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_run.job_v1.data import JobV1

_LOGGER = logging.getLogger(__name__)


class CloudRunJobV1Manager(GoogleCloudManager):
    connector_name = "CloudRunV1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug("** Cloud Run Job V1 START **")
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
        job_id = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        cloud_run_v1_conn: CloudRunV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        # Get lists that relate with jobs through Google Cloud API
        # V1은 namespace 기반이므로 단일 namespace로 모든 리소스 조회 가능
        try:
            namespace = f"namespaces/{project_id}"
            jobs = cloud_run_v1_conn.list_jobs(namespace)
            
            for job in jobs:
                # V1에서는 location 정보가 metadata에 포함되어 있을 수 있음
                location_id = (
                    job.get("metadata", {}).get("labels", {}).get("cloud.googleapis.com/location") or
                    job.get("metadata", {}).get("namespace", "").split("/")[-1] or
                    "us-central1"  # default location
                )
                job["_location"] = location_id
                
                # Get executions and tasks for each job - 단순화된 정보만 저장
                try:
                    executions = cloud_run_v1_conn.list_executions(namespace)
                    # Filter executions for this job
                    job_name = job.get("metadata", {}).get("name", "")
                    job_executions = [
                        exec for exec in executions 
                        if exec.get("metadata", {}).get("labels", {}).get("run.googleapis.com/job") == job_name
                    ]
                    
                    # 복잡한 중첩 구조 대신 필요한 정보만 추출하여 단순화
                    simplified_executions = []
                    for execution in job_executions:
                        metadata = execution.get("metadata", {})
                        
                        # Get tasks for this execution
                        execution_name = metadata.get("name", "")
                        try:
                            tasks = cloud_run_v1_conn.list_tasks(namespace)
                            execution_tasks = [
                                task for task in tasks
                                if task.get("metadata", {}).get("labels", {}).get("run.googleapis.com/execution") == execution_name
                            ]
                            
                            # 단순화된 task 정보
                            simplified_tasks = []
                            for task in execution_tasks:
                                task_metadata = task.get("metadata", {})
                                task_status = task.get("status", {})
                                simplified_task = {
                                    "name": task_metadata.get("name"),
                                    "uid": task_metadata.get("uid"),
                                    "create_time": task_metadata.get("creationTimestamp"),
                                    "completion_time": task_status.get("completionTime"),
                                    "started": task_status.get("startTime") is not None
                                }
                                simplified_tasks.append(simplified_task)
                            
                        except Exception as e:
                            _LOGGER.debug(f"Failed to get tasks for execution {execution_name}: {str(e)}")
                            simplified_tasks = []
                        
                        simplified_execution = {
                            "name": metadata.get("name"),
                            "uid": metadata.get("uid"),
                            "creator": metadata.get("labels", {}).get("run.googleapis.com/creator"),
                            "job": metadata.get("labels", {}).get("run.googleapis.com/job"),
                            "task_count": len(simplified_tasks),
                            "tasks": simplified_tasks
                        }
                        simplified_executions.append(simplified_execution)
                    
                    job["executions"] = simplified_executions
                    job["execution_count"] = len(simplified_executions)
                except Exception as e:
                    _LOGGER.warning(f"Failed to get executions for job: {str(e)}")
                    job["executions"] = []
                    job["execution_count"] = 0
        except Exception as e:
            _LOGGER.warning(f"Failed to query jobs from namespace: {str(e)}")
            jobs = []

        for job in jobs:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                job_id = job.get("metadata", {}).get("name", "")
                location_id = job.get("_location", "")
                region = self.parse_region_from_zone(location_id) if location_id else ""

                ##################################
                # 2. Make Base Data
                ##################################
                job.update(
                    {
                        "project": project_id,
                        "location": location_id,
                        "region": region,
                    }
                )

                ##################################
                # 3. Make Return Resource
                ##################################
                # V1 API 응답의 복잡한 중첩 구조를 처리하기 위해 매우 관대한 설정 사용
                job_data = JobV1(job, strict=False)

                job_resource = JobV1Resource(
                    {
                        "name": job_id,
                        "account": project_id,
                        "region_code": location_id,
                        "data": job_data,
                        "reference": ReferenceModel(
                            {
                                "resource_id": job_data.name,
                                "external_link": f"https://console.cloud.google.com/run/jobs/details/{location_id}/{job_id}?project={project_id}",
                            }
                        ),
                    },
                    strict=False,
                )

                collected_cloud_services.append(JobV1Response({"resource": job_resource}))

            except Exception as e:
                _LOGGER.error(f"Failed to process job {job_id}: {str(e)}")
                error_response = self.generate_resource_error_response(
                    e, "JobV1", "CloudRun", job_id
                )
                error_responses.append(error_response)

        _LOGGER.debug(f"** Cloud Run Job V1 END ** ({time.time() - start_time:.2f}s)")

        return collected_cloud_services, error_responses
