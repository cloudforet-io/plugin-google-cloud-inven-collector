import logging
import time

from spaceone.inventory.connector.batch.batch_connector import BatchConnector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.batch.location.cloud_service import (
    LocationResource,
    LocationResponse,
)
from spaceone.inventory.model.batch.location.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.batch.location.data import Location

_LOGGER = logging.getLogger(__name__)


class BatchManager(GoogleCloudManager):
    connector_name = "BatchConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug("** Batch START **")
        start_time = time.time()
        """
        Args:
            params:
                - options
                - schema
                - secret_data
                - filter
        Response:
            CloudServiceResponse/ErrorResourceResponse
        """

        collected_cloud_services = []
        error_responses = []

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        batch_conn: BatchConnector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            # 1. 모든 Location의 Jobs를 글로벌로 조회 (locations/- 패턴 사용)
            all_jobs = batch_conn.list_all_jobs()
            _LOGGER.debug(f"Found {len(all_jobs)} Batch jobs across all locations")

            # 2. Jobs를 location별로 그룹핑
            jobs_by_location = self._group_jobs_by_location(all_jobs)
            _LOGGER.debug(f"Jobs grouped into {len(jobs_by_location)} locations")

            # 3. 각 location별로 리소스 생성
            for location_id, location_jobs in jobs_by_location.items():
                try:
                    # Jobs 데이터 처리 및 상세 정보 수집
                    jobs, job_count = self._collect_jobs_data(
                        batch_conn, location_jobs, params
                    )

                    # Location 리소스 데이터 생성
                    batch_data = {
                        "project_id": project_id,
                        "name": f"projects/{project_id}/locations/{location_id}",
                        "location_id": location_id,
                        "display_name": f"Batch Service - {location_id}",
                        "jobs": jobs,
                        "job_count": job_count,
                    }

                    # Location 모델 생성
                    batch_location = Location(batch_data)

                    # Cloud Service 리소스 생성
                    batch_location_resource = LocationResource(
                        {
                            "name": location_id,
                            "account": project_id,
                            "data": batch_location,
                            "reference": ReferenceModel(batch_location.reference()),
                            "region_code": location_id,
                        }
                    )

                    # Cloud Service Type 정보 추가
                    collected_cloud_services.append(
                        LocationResponse(
                            {
                                "resource_type": "inventory.CloudService",
                                "resource": batch_location_resource,
                            }
                        )
                    )

                    _LOGGER.debug(
                        f"Collected Batch Location: {location_id} with {job_count} jobs"
                    )

                except Exception as e:
                    _LOGGER.error(
                        f"[collect_cloud_service] location {location_id} => {e}",
                        exc_info=True,
                    )
                    error_responses.append(
                        self.generate_error_response(
                            e, location_id, "inventory.CloudService"
                        )
                    )

        except Exception as e:
            _LOGGER.error(f"[collect_cloud_service] => {e}", exc_info=True)
            error_responses.append(
                self.generate_error_response(e, "global", "inventory.CloudService")
            )

        _LOGGER.debug(f"** Batch Finished {time.time() - start_time} Seconds **")
        return collected_cloud_services, error_responses

    def _group_jobs_by_location(self, all_jobs):
        """
        Jobs를 location별로 그룹핑합니다.
        Job name에서 location 정보를 추출합니다.

        Args:
            all_jobs: 모든 jobs 리스트

        Returns:
            dict: {location_id: [jobs]} 형태의 딕셔너리
        """
        jobs_by_location = {}

        for job in all_jobs:
            job_name = job.get("name", "")
            # Job name 형태: projects/{project}/locations/{location}/jobs/{job_id}
            try:
                # /locations/ 이후 /jobs/ 이전의 location_id 추출
                location_start = job_name.find("/locations/") + len("/locations/")
                location_end = job_name.find("/jobs/")

                if (
                    location_start > len("/locations/") - 1
                    and location_end > location_start
                ):
                    location_id = job_name[location_start:location_end]

                    if location_id not in jobs_by_location:
                        jobs_by_location[location_id] = []
                    jobs_by_location[location_id].append(job)
                else:
                    _LOGGER.warning(
                        f"Could not extract location from job name: {job_name}"
                    )
                    # 기본 location으로 처리
                    if "unknown" not in jobs_by_location:
                        jobs_by_location["unknown"] = []
                    jobs_by_location["unknown"].append(job)

            except Exception as e:
                _LOGGER.warning(f"Error parsing job name {job_name}: {e}")
                # 기본 location으로 처리
                if "unknown" not in jobs_by_location:
                    jobs_by_location["unknown"] = []
                jobs_by_location["unknown"].append(job)

        return jobs_by_location

    def _collect_jobs_data(self, batch_conn, all_jobs, params):
        """
        글로벌로 수집된 Jobs 및 관련 TaskGroups, Tasks 데이터를 처리합니다.

        Args:
            batch_conn: BatchConnector 인스턴스
            all_jobs: 모든 jobs 리스트
            params: 수집 파라미터

        Returns:
            tuple: (처리된 jobs 리스트, job 개수)
        """
        try:
            _LOGGER.debug(f"Processing {len(all_jobs)} jobs")

            # Jobs 데이터 처리
            simplified_jobs = []
            for job in all_jobs:
                simplified_job = self._process_job_data(batch_conn, job, params)
                simplified_jobs.append(simplified_job)

            return simplified_jobs, len(all_jobs)

        except Exception as e:
            _LOGGER.warning(f"Failed to process jobs data: {e}")
            return [], 0

    def _process_job_data(self, batch_conn, job, params):
        """
        개별 Job의 TaskGroups와 Tasks 데이터를 처리합니다.

        Args:
            batch_conn: BatchConnector 인스턴스
            job: Job 데이터
            params: 수집 파라미터

        Returns:
            dict: 처리된 Job 데이터
        """
        # TaskGroup 정보 추출 및 처리
        task_groups_raw = job.get("taskGroups", [])
        task_groups_list = []
        allocation_policy = job.get("allocationPolicy", {})
        instances = allocation_policy.get("instances", [])

        for task_group in task_groups_raw:
            task_group_data = self._process_task_group_data(
                batch_conn, task_group, instances, params
            )
            task_groups_list.append(task_group_data)

        # Job 데이터 구성
        simplified_job = {
            "name": job.get("name", ""),
            "uid": job.get("uid", ""),
            "displayName": job.get("displayName", ""),
            "state": job.get("status", {}).get("state", ""),
            "createTime": job.get("createTime", ""),
            "updateTime": job.get("updateTime", ""),
            "taskGroups": task_groups_list,
        }

        return simplified_job

    def _process_task_group_data(self, batch_conn, task_group, instances, params):
        """
        개별 TaskGroup의 데이터를 처리하고 Tasks를 수집합니다.

        Args:
            batch_conn: BatchConnector 인스턴스
            task_group: TaskGroup 데이터
            instances: 할당 정책의 인스턴스 정보
            params: 수집 파라미터

        Returns:
            dict: 처리된 TaskGroup 데이터
        """
        # TaskGroup 기본 정보 추출
        task_group_name = task_group.get("name", "")

        # 머신 타입 추출
        machine_type = ""
        if instances and instances[0].get("policy"):
            machine_type = instances[0]["policy"].get("machineType", "")

        # 이미지 URI, CPU, 메모리 정보 추출
        task_spec = task_group.get("taskSpec", {})
        runnables = task_spec.get("runnables", [])
        image_uri = ""
        if runnables and runnables[0].get("container"):
            image_uri = runnables[0]["container"].get("imageUri", "")

        compute_resource = task_spec.get("computeResource", {})
        cpu_milli = compute_resource.get("cpuMilli", "")
        memory_mib = compute_resource.get("memoryMib", "")

        # Tasks 수집
        tasks_list = []
        if task_group_name:
            try:
                tasks = batch_conn.list_tasks(task_group_name)
                for task in tasks:
                    task_data = {
                        "name": task.get("name", ""),
                        "taskIndex": task.get("taskIndex", 0),
                        "state": task.get("status", {}).get("state", ""),
                        "createTime": task.get("createTime", ""),
                        "startTime": task.get("startTime", ""),
                        "endTime": task.get("endTime", ""),
                        "exitCode": task.get("status", {}).get("exitCode", 0),
                    }
                    tasks_list.append(task_data)
            except Exception as e:
                _LOGGER.warning(
                    f"Failed to get tasks for TaskGroup {task_group_name}: {e}"
                )

        # TaskGroup 데이터 구성
        task_group_data = {
            "name": task_group_name,
            "taskCount": task_group.get("taskCount", "0"),
            "parallelism": task_group.get("parallelism", ""),
            "machineType": machine_type,
            "imageUri": image_uri,
            "cpuMilli": cpu_milli,
            "memoryMib": memory_mib,
            "tasks": tasks_list,
        }

        return task_group_data
