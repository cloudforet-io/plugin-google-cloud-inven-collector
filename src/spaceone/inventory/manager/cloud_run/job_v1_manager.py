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

        try:
            namespace = f"namespaces/{project_id}"
            jobs = cloud_run_v1_conn.list_jobs(namespace)

            for job in jobs:
                location_id = (
                    job.get("metadata", {})
                    .get("labels", {})
                    .get("cloud.googleapis.com/location")
                    or job.get("metadata", {}).get("namespace", "").split("/")[-1]
                    or "us-central1"  # default location
                )
                job["_location"] = location_id

                try:
                    executions = cloud_run_v1_conn.list_executions(namespace)
                    job_name = job.get("metadata", {}).get("name", "")
                    job_executions = [
                        exec
                        for exec in executions
                        if exec.get("metadata", {})
                        .get("labels", {})
                        .get("run.googleapis.com/job")
                        == job_name
                    ]

                    simplified_executions = []
                    for execution in job_executions:
                        metadata = execution.get("metadata", {})
                        execution_name = metadata.get("name", "")
                        try:
                            tasks = cloud_run_v1_conn.list_tasks(namespace)
                            execution_tasks = [
                                task
                                for task in tasks
                                if task.get("metadata", {})
                                .get("labels", {})
                                .get("run.googleapis.com/execution")
                                == execution_name
                            ]

                            simplified_tasks = []
                            for task in execution_tasks:
                                task_metadata = task.get("metadata", {})
                                task_status = task.get("status", {})
                                simplified_task = {
                                    "name": task_metadata.get("name"),
                                    "uid": task_metadata.get("uid"),
                                    "create_time": task_metadata.get(
                                        "creationTimestamp"
                                    ),
                                    "completion_time": task_status.get(
                                        "completionTime"
                                    ),
                                    "started": task_status.get("startTime") is not None,
                                }
                                simplified_tasks.append(simplified_task)

                        except Exception as e:
                            _LOGGER.debug(
                                f"Failed to get tasks for execution {execution_name}: {str(e)}"
                            )
                            simplified_tasks = []

                        simplified_execution = {
                            "name": metadata.get("name"),
                            "uid": metadata.get("uid"),
                            "creator": metadata.get("labels", {}).get(
                                "run.googleapis.com/creator"
                            ),
                            "job": metadata.get("labels", {}).get(
                                "run.googleapis.com/job"
                            ),
                            "task_count": len(simplified_tasks),
                            "tasks": simplified_tasks,
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
                        "google_cloud_logging": self.set_google_cloud_logging(
                            "CloudRun", "Job", project_id, job_id
                        ),
                    }
                )

                ##################################
                # 3. Make Return Resource
                ##################################
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

                collected_cloud_services.append(
                    JobV1Response({"resource": job_resource})
                )

            except Exception as e:
                _LOGGER.error(f"Failed to process job {job_id}: {str(e)}")
                error_response = self.generate_resource_error_response(
                    e, "JobV1", "CloudRun", job_id
                )
                error_responses.append(error_response)

        _LOGGER.debug(f"** Cloud Run Job V1 END ** ({time.time() - start_time:.2f}s)")

        return collected_cloud_services, error_responses
