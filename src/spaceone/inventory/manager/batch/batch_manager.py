import logging
import time
from typing import Dict, List, Tuple

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
    """최적화된 Batch Manager - 효율적인 리소스 수집과 처리"""

    connector_name = "BatchConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params) -> Tuple[List[LocationResponse], List]:
        """
        Batch 리소스를 효율적으로 수집합니다.

        Args:
            params: 수집 파라미터 (secret_data, options, schema, filter)

        Returns:
            Tuple[List[LocationResponse], List]: (수집된 리소스들, 에러 응답들)
        """
        _LOGGER.debug("** Batch START **")
        start_time = time.time()

        collected_cloud_services = []
        error_responses = []

        try:
            project_id = params["secret_data"]["project_id"]
            batch_conn = self._get_connector(params)

            # 1. 글로벌 Jobs 수집 (locations/- 패턴)
            all_jobs = batch_conn.list_all_jobs()
            if not all_jobs:
                _LOGGER.info("No Batch jobs found in any location")
                return collected_cloud_services, error_responses

            _LOGGER.debug(f"Found {len(all_jobs)} Batch jobs across all locations")

            # 2. Location별 그룹핑 및 리소스 생성
            jobs_by_location = self._group_jobs_by_location(all_jobs)

            for location_id, location_jobs in jobs_by_location.items():
                try:
                    resource = self._create_location_resource(
                        location_id, location_jobs, project_id, batch_conn, params
                    )
                    collected_cloud_services.append(resource)

                    _LOGGER.debug(
                        f"Collected Batch Location: {location_id} with {len(location_jobs)} jobs"
                    )

                except Exception as e:
                    _LOGGER.error(
                        f"Failed to process location {location_id}: {e}", exc_info=True
                    )
                    error_responses.append(
                        self.generate_error_response(
                            e, location_id, "inventory.CloudService"
                        )
                    )

        except Exception as e:
            _LOGGER.error(f"Batch collection failed: {e}", exc_info=True)
            error_responses.append(
                self.generate_error_response(e, "batch", "inventory.CloudService")
            )

        _LOGGER.debug(f"** Batch Finished {time.time() - start_time:.2f} Seconds **")
        return collected_cloud_services, error_responses

    def _get_connector(self, params) -> BatchConnector:
        """Connector 인스턴스를 가져옵니다."""
        return self.locator.get_connector(self.connector_name, **params)

    def _group_jobs_by_location(self, all_jobs: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Jobs를 location별로 효율적으로 그룹핑합니다.

        Args:
            all_jobs: 모든 jobs 리스트

        Returns:
            Dict[str, List[Dict]]: {location_id: [jobs]} 형태의 딕셔너리
        """
        jobs_by_location = {}

        for job in all_jobs:
            location_id = self._extract_location_from_job_name(job.get("name", ""))

            if location_id not in jobs_by_location:
                jobs_by_location[location_id] = []
            jobs_by_location[location_id].append(job)

        _LOGGER.debug(f"Jobs grouped into {len(jobs_by_location)} locations")
        return jobs_by_location

    def _extract_location_from_job_name(self, job_name: str) -> str:
        """
        Job name에서 location ID를 추출합니다.

        Args:
            job_name: Job의 전체 경로명

        Returns:
            str: Location ID 또는 'unknown'
        """
        try:
            # Job name 형태: projects/{project}/locations/{location}/jobs/{job_id}
            location_start = job_name.find("/locations/") + len("/locations/")
            location_end = job_name.find("/jobs/")

            if (
                location_start > len("/locations/") - 1
                and location_end > location_start
            ):
                return job_name[location_start:location_end]

        except Exception as e:
            _LOGGER.warning(f"Error parsing job name {job_name}: {e}")

        _LOGGER.warning(f"Could not extract location from job name: {job_name}")
        return "unknown"

    def _create_location_resource(
        self,
        location_id: str,
        location_jobs: List[Dict],
        project_id: str,
        batch_conn: BatchConnector,
        params: Dict,
    ) -> LocationResponse:
        """
        Location 리소스를 생성합니다.

        Args:
            location_id: Location ID
            location_jobs: 해당 location의 jobs 리스트
            project_id: Project ID
            batch_conn: Batch connector
            params: 수집 파라미터

        Returns:
            LocationResponse: 생성된 리소스 응답
        """
        # Jobs 데이터 처리
        processed_jobs = self._process_jobs(location_jobs, batch_conn)

        # 깔끔한 데이터 구조 생성 (location 정보 제외)
        clean_data = Location(
            {
                "project_id": project_id,
                "jobs": processed_jobs,
                "job_count": len(location_jobs),
            }
        )

        # Reference용 임시 location 데이터
        reference_data = Location(
            {
                "project_id": project_id,
                "location_id": location_id,
                "jobs": processed_jobs,
                "job_count": len(location_jobs),
            }
        )

        # Cloud Service 리소스 생성
        resource = LocationResource(
            {
                "name": location_id,
                "account": project_id,
                "data": clean_data,
                "reference": ReferenceModel(reference_data.reference()),
                "region_code": location_id,
            }
        )

        return LocationResponse(
            {
                "resource_type": "inventory.CloudService",
                "resource": resource,
            }
        )

    def _process_jobs(self, jobs: List[Dict], batch_conn: BatchConnector) -> List[Dict]:
        """
        Jobs 데이터를 효율적으로 처리합니다.

        Args:
            jobs: 처리할 jobs 리스트
            batch_conn: Batch connector

        Returns:
            List[Dict]: 처리된 jobs 데이터
        """
        processed_jobs = []

        for job in jobs:
            try:
                processed_job = self._process_single_job(job, batch_conn)
                processed_jobs.append(processed_job)
            except Exception as e:
                job_name = job.get("name", "unknown")
                _LOGGER.warning(f"Failed to process job {job_name}: {e}")
                # 기본 job 정보라도 포함
                processed_jobs.append(self._create_basic_job_data(job))

        return processed_jobs

    def _process_single_job(self, job: Dict, batch_conn: BatchConnector) -> Dict:
        """
        개별 Job을 처리합니다.

        Args:
            job: Job 데이터
            batch_conn: Batch connector

        Returns:
            Dict: 처리된 Job 데이터
        """
        # TaskGroup 처리
        task_groups = self._process_task_groups(
            job.get("taskGroups", []), job.get("allocationPolicy", {}), batch_conn
        )

        # Job 기본 정보
        return {
            "name": job.get("name", ""),
            "uid": job.get("uid", ""),
            "displayName": job.get("displayName", ""),
            "state": job.get("status", {}).get("state", ""),
            "createTime": job.get("createTime", ""),
            "updateTime": job.get("updateTime", ""),
            "taskGroups": task_groups,
        }

    def _process_task_groups(
        self,
        task_groups_raw: List[Dict],
        allocation_policy: Dict,
        batch_conn: BatchConnector,
    ) -> List[Dict]:
        """
        TaskGroup들을 효율적으로 처리합니다.

        Args:
            task_groups_raw: 원본 TaskGroup 데이터
            allocation_policy: 할당 정책
            batch_conn: Batch connector

        Returns:
            List[Dict]: 처리된 TaskGroup 데이터
        """
        instances = allocation_policy.get("instances", [])
        machine_type = ""
        if instances and instances[0].get("policy"):
            machine_type = instances[0]["policy"].get("machineType", "")

        processed_groups = []
        for task_group in task_groups_raw:
            try:
                processed_group = self._process_single_task_group(
                    task_group, machine_type, batch_conn
                )
                processed_groups.append(processed_group)
            except Exception as e:
                group_name = task_group.get("name", "unknown")
                _LOGGER.warning(f"Failed to process task group {group_name}: {e}")
                # 기본 데이터라도 포함
                processed_groups.append(self._create_basic_task_group_data(task_group))

        return processed_groups

    def _process_single_task_group(
        self, task_group: Dict, machine_type: str, batch_conn: BatchConnector
    ) -> Dict:
        """
        개별 TaskGroup을 처리합니다.

        Args:
            task_group: TaskGroup 데이터
            machine_type: 머신 타입
            batch_conn: Batch connector

        Returns:
            Dict: 처리된 TaskGroup 데이터
        """
        # 기본 정보 추출
        task_spec = task_group.get("taskSpec", {})
        runnables = task_spec.get("runnables", [])

        image_uri = ""
        if runnables and runnables[0].get("container"):
            image_uri = runnables[0]["container"].get("imageUri", "")

        compute_resource = task_spec.get("computeResource", {})

        # Tasks 수집 (최적화: 에러가 발생해도 계속 진행)
        tasks = self._collect_tasks_safe(task_group.get("name", ""), batch_conn)

        return {
            "name": task_group.get("name", ""),
            "taskCount": task_group.get("taskCount", "0"),
            "parallelism": task_group.get("parallelism", ""),
            "machineType": machine_type,
            "imageUri": image_uri,
            "cpuMilli": compute_resource.get("cpuMilli", ""),
            "memoryMib": compute_resource.get("memoryMib", ""),
            "tasks": tasks,
        }

    def _collect_tasks_safe(
        self, task_group_name: str, batch_conn: BatchConnector
    ) -> List[Dict]:
        """
        Tasks를 안전하게 수집합니다.

        Args:
            task_group_name: TaskGroup 이름
            batch_conn: Batch connector

        Returns:
            List[Dict]: Tasks 데이터
        """
        if not task_group_name:
            return []

        try:
            tasks = batch_conn.list_tasks(task_group_name)
            return [
                {
                    "name": task.get("name", ""),
                    "taskIndex": task.get("taskIndex", 0),
                    "state": task.get("status", {}).get("state", ""),
                    "createTime": task.get("createTime", ""),
                    "startTime": task.get("startTime", ""),
                    "endTime": task.get("endTime", ""),
                    "exitCode": task.get("status", {}).get("exitCode", 0),
                }
                for task in tasks
            ]
        except Exception as e:
            _LOGGER.warning(f"Failed to collect tasks for {task_group_name}: {e}")
            return []

    def _create_basic_job_data(self, job: Dict) -> Dict:
        """기본 Job 데이터를 생성합니다."""
        return {
            "name": job.get("name", ""),
            "uid": job.get("uid", ""),
            "displayName": job.get("displayName", ""),
            "state": job.get("status", {}).get("state", "UNKNOWN"),
            "createTime": job.get("createTime", ""),
            "updateTime": job.get("updateTime", ""),
            "taskGroups": [],
        }

    def _create_basic_task_group_data(self, task_group: Dict) -> Dict:
        """기본 TaskGroup 데이터를 생성합니다."""
        return {
            "name": task_group.get("name", ""),
            "taskCount": task_group.get("taskCount", "0"),
            "parallelism": task_group.get("parallelism", ""),
            "machineType": "",
            "imageUri": "",
            "cpuMilli": "",
            "memoryMib": "",
            "tasks": [],
        }
