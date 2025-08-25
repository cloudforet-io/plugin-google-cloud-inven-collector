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
            # 1. Batch 지원 Location 목록 조회
            batch_locations = batch_conn.list_locations()
            _LOGGER.debug(f"Found {len(batch_locations)} Batch locations")

            for location_info in batch_locations:
                try:
                    location_data = location_info.copy()
                    location_data["project_id"] = project_id

                    # 2. 해당 Location의 Jobs 조회 및 상세 정보 수집
                    location_id = location_data.get("locationId", "")
                    if location_id:
                        location_data = self._collect_jobs_data(
                            batch_conn, location_data, params
                        )

                    # 3. Location 모델 생성
                    batch_location = Location(location_data)

                    # 4. Cloud Service 리소스 생성
                    batch_location_resource = LocationResource(
                        {
                            "name": batch_location.location_id,
                            "account": project_id,
                            "data": batch_location,
                            "reference": ReferenceModel(batch_location.reference()),
                            "region_code": batch_location.location_id,
                        }
                    )

                    # 5. Cloud Service Type 정보 추가
                    collected_cloud_services.append(
                        LocationResponse(
                            {
                                "resource_type": "inventory.CloudService",
                                "resource": batch_location_resource,
                            }
                        )
                    )

                    _LOGGER.debug(f"Collected Batch Location: {location_id}")

                except Exception as e:
                    _LOGGER.error(f"[collect_cloud_service] => {e}", exc_info=True)
                    error_responses.append(
                        self.generate_error_response(
                            e,
                            location_info.get("locationId", ""),
                            "inventory.CloudService",
                        )
                    )

        except Exception as e:
            _LOGGER.error(f"[collect_cloud_service] => {e}", exc_info=True)

        _LOGGER.debug(f"** Batch Finished {time.time() - start_time} Seconds **")

        return collected_cloud_services, error_responses

    def _collect_jobs_data(self, batch_conn, location_data, params):
        """
        특정 Location의 Jobs 및 관련 TaskGroups, Tasks 데이터를 수집합니다.

        Args:
            batch_conn: BatchConnector 인스턴스
            location_data: Location 데이터
            params: 수집 파라미터

        Returns:
            dict: Jobs 정보가 추가된 Location 데이터
        """
        location_id = location_data.get("locationId", "")

        try:
            # Jobs 목록 조회
            jobs = batch_conn.list_jobs(location_id)
            _LOGGER.debug(f"Found {len(jobs)} jobs in location {location_id}")

            # Jobs 데이터 처리
            simplified_jobs = []
            for job in jobs:
                simplified_job = self._process_job_data(batch_conn, job, params)
                simplified_jobs.append(simplified_job)

            location_data["jobs"] = simplified_jobs
            location_data["job_count"] = len(jobs)

        except Exception as e:
            _LOGGER.warning(f"Failed to get jobs for location {location_id}: {e}")
            location_data["jobs"] = []
            location_data["job_count"] = 0

        return location_data

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
