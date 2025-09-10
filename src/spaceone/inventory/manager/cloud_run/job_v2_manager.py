import logging
import time

from spaceone.inventory.connector.cloud_run.cloud_run_v1 import CloudRunV1Connector
from spaceone.inventory.connector.cloud_run.cloud_run_v2 import CloudRunV2Connector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.cloud_run.job_v2.cloud_service import (
    JobResource,
    JobResponse,
)
from spaceone.inventory.model.cloud_run.job_v2.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)

_LOGGER = logging.getLogger(__name__)


class CloudRunJobV2Manager(GoogleCloudManager):
    connector_name = "CloudRunV2Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug("** Cloud Run Job V2 START **")
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
        cloud_run_v2_conn: CloudRunV2Connector = self.locator.get_connector(
            self.connector_name, **params
        )
        cloud_run_v1_conn: CloudRunV1Connector = self.locator.get_connector(
            "CloudRunV1Connector", **params
        )

        # Get lists that relate with jobs through Google Cloud API
        all_jobs = []
        parent = f"projects/{project_id}"

        try:
            locations = cloud_run_v1_conn.list_locations(parent)
            _LOGGER.info(f"V1 API: Found {len(locations)} locations for jobs")
        except Exception as e:
            _LOGGER.warning(
                f"V1 API: Failed to get locations, falling back to empty list: {e}"
            )
            locations = []

        try:
            for location in locations:
                location_id = location.get("locationId", "")
                if location_id:
                    try:
                        parent = f"projects/{project_id}/locations/{location_id}"
                        jobs = cloud_run_v2_conn.list_jobs(parent)
                        for job in jobs:
                            job["_location"] = location_id
                            # Get executions for each job
                            job_name = job.get("name")
                            if job_name:
                                try:
                                    executions = cloud_run_v2_conn.list_job_executions(
                                        job_name
                                    )
                                    # Get tasks for each execution
                                    for execution in executions:
                                        execution_name = execution.get("name")
                                        if execution_name:
                                            # Extract execution name from full path for display
                                            if "/executions/" in execution_name:
                                                execution_display_name = (
                                                    execution_name.split(
                                                        "/executions/"
                                                    )[-1]
                                                )
                                                execution["display_name"] = (
                                                    execution_display_name
                                                )

                                            try:
                                                tasks = cloud_run_v2_conn.list_execution_tasks(
                                                    execution_name
                                                )
                                                execution["tasks"] = tasks
                                                execution["task_count"] = len(tasks)
                                            except Exception as e:
                                                _LOGGER.warning(
                                                    f"Failed to get tasks for execution {execution_name}: {str(e)}"
                                                )
                                                execution["tasks"] = []
                                                execution["task_count"] = 0
                                    job["executions"] = executions
                                    job["execution_count"] = len(executions)
                                except Exception as e:
                                    _LOGGER.warning(
                                        f"Failed to get executions for job {job_name}: {str(e)}"
                                    )
                                    job["executions"] = []
                                    job["execution_count"] = 0
                            all_jobs.append(job)

                    except Exception as e:
                        _LOGGER.debug(
                            f"Failed to query jobs in location {location_id}: {str(e)}"
                        )
                        continue
        except Exception as e:
            _LOGGER.warning(f"Failed to process locations: {str(e)}")

        for job in all_jobs:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                job_id = job.get("name", "")
                job_name = self.get_param_in_url(job_id, "jobs") if job_id else ""
                full_name = job.get("name", job_name)
                location_id = job.get("_location", "")
                region = self.parse_region_from_zone(location_id) if location_id else ""

                ##################################
                # 2. Make Base Data
                ##################################
                job.update(
                    {
                        "name": job_name,
                        "full_name": full_name,
                        "project": project_id,
                        "location": location_id,
                        "region": region,
                    }
                )

                ##################################
                # 3. Make Return Resource
                ##################################
                from spaceone.inventory.model.cloud_run.job_v2.data import Job

                job_data = Job(job, strict=False)

                job_resource = JobResource(
                    {
                        "name": job_name,
                        "account": project_id,
                        "region_code": location_id,
                        "data": job_data,
                        "reference": ReferenceModel(
                            {
                                "resource_id": f"https://cloudrun.googleapis.com/v2/{job_data.full_name}",
                                "external_link": f"https://console.cloud.google.com/run/jobs/details/{location_id}/{job_name}?project={project_id}",
                            }
                        ),
                    },
                    strict=False,
                )

                collected_cloud_services.append(JobResponse({"resource": job_resource}))

            except Exception as e:
                _LOGGER.error(f"Failed to process job {job_id}: {str(e)}")
                error_response = self.generate_resource_error_response(
                    e, "CloudRun", "Job", job_id
                )
                error_responses.append(error_response)

        _LOGGER.debug(f"** Cloud Run Job V2 END ** ({time.time() - start_time:.2f}s)")

        return collected_cloud_services, error_responses
