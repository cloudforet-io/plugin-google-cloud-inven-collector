import logging
import re
import time
from typing import Dict, List, Tuple

from spaceone.inventory.connector.batch.batch_v1 import BatchV1Connector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.batch_processor import BatchJobProcessor
from spaceone.inventory.libs.schema.base import ReferenceModel, reset_state_counters, log_state_summary
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResponse, ErrorResourceResponse
from spaceone.inventory.model.batch.job.cloud_service import (
    JobResource,
    JobResponse,
)
from spaceone.inventory.model.batch.job.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.batch.job.data import BatchJobResource

_LOGGER = logging.getLogger(__name__)


class BatchManager(GoogleCloudManager):
    """Job 기준 Batch Manager - 개별 Job을 리소스로 관리"""

    connector_name = "BatchV1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params) -> Tuple[List[CloudServiceResponse], List]:
        """
        Batch Job들을 개별 리소스로 수집합니다.

        Args:
            params: 수집 파라미터 (secret_data, options, schema, filter)

        Returns:
            Tuple[List[CloudServiceResponse], List]: (수집된 Job 리소스들, 에러 응답들)
        """
        _LOGGER.debug("** Batch Job Collection START **")
        start_time = time.time()

        # v2.0 로깅 시스템 초기화
        reset_state_counters()

        collected_cloud_services = []
        error_responses = []

        try:
            project_id = params["secret_data"]["project_id"]
            batch_connector = self._get_connector(params)

            # 1. 모든 Batch Jobs 수집
            all_jobs = batch_connector.list_all_jobs()
            if not all_jobs:
                _LOGGER.info("No Batch jobs found")
                return collected_cloud_services, error_responses

            _LOGGER.debug(f"Found {len(all_jobs)} Batch jobs")

            # 2. 각 Job을 개별 리소스로 처리
            for job in all_jobs:
                try:
                    job_resource = self._create_job_resource(
                        job, project_id, batch_connector, params
                    )
                    collected_cloud_services.append(job_resource)

                    _LOGGER.debug(f"Collected Batch Job: {job.get('name', 'unknown')}")

                except Exception as e:
                    job_name = job.get("name", "unknown")
                    _LOGGER.error(f"Failed to process job {job_name}: {e}", exc_info=True)
                    
                    # v2.0 로깅 시스템: 에러 응답 생성
                    error_response = ErrorResourceResponse.create_with_logging(
                        error=e,
                        provider="google_cloud",
                        cloud_service_group="Batch",
                        cloud_service_type="Job",
                        resource_id=job_name,
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(f"Batch Job collection failed: {e}", exc_info=True)
            error_response = ErrorResourceResponse.create_with_logging(
                error=e,
                provider="google_cloud",
                cloud_service_group="Batch",
                cloud_service_type="Job",
                resource_id="batch-service",
            )
            error_responses.append(error_response)

        # v2.0 로깅 시스템: 수집 완료 시 상태 요약 로깅
        log_state_summary()
        _LOGGER.debug(f"** Batch Job Collection Finished {time.time() - start_time:.2f} Seconds **")
        _LOGGER.info(f"Collected {len(collected_cloud_services)} Batch Jobs")
        return collected_cloud_services, error_responses

    def _get_connector(self, params) -> BatchV1Connector:
        """Connector 인스턴스를 가져옵니다."""
        return self.locator.get_connector(self.connector_name, **params)

    def _parse_job_name(self, job_name: str) -> Tuple[str, str, str]:
        """
        Job name에서 project, location, job_id를 추출합니다.

        Args:
            job_name: Job의 전체 경로명

        Returns:
            Tuple[str, str, str]: (project_id, location_id, job_id)
        """
        try:
            # Job name 형태: projects/{project}/locations/{location}/jobs/{job_id}
            job_pattern = r'projects/([^/]+)/locations/([^/]+)/jobs/([^/]+)'
            match = re.match(job_pattern, job_name)
            
            if match:
                return match.group(1), match.group(2), match.group(3)

        except Exception as e:
            _LOGGER.warning(f"Error parsing job name {job_name}: {e}")

        _LOGGER.warning(f"Could not parse job name: {job_name}")
        return "unknown", "unknown", job_name

    def _create_job_resource(
        self,
        job: Dict,
        project_id: str,
        batch_connector: BatchV1Connector,
        params: Dict,
    ) -> CloudServiceResponse:
        """
        개별 Job 리소스를 생성합니다.

        Args:
            job: Job 데이터
            project_id: Project ID
            batch_connector: Batch connector
            params: 수집 파라미터

        Returns:
            CloudServiceResponse: 생성된 Job 리소스 응답
        """
        try:
            job_name = job.get("name", "")
            _, location_id, job_id = self._parse_job_name(job_name)

            # Jobs 데이터 처리 (기존 헬퍼 클래스 활용)
            job_processor = BatchJobProcessor(batch_connector)
            processed_jobs = job_processor.process_jobs([job])
            
            if not processed_jobs:
                raise ValueError(f"Failed to process job data for {job_name}")
            
            processed_job = processed_jobs[0]

            # Task 개수 계산 및 모든 Task 수집
            task_count = 0
            all_tasks = []
            task_groups = processed_job.get("task_groups", [])
            for task_group in task_groups:
                # TaskGroup의 task_count를 사용 (문자열이므로 int로 변환)
                group_task_count = task_group.get("task_count", "0")
                try:
                    task_count += int(group_task_count)
                except (ValueError, TypeError):
                    _LOGGER.warning(f"Invalid task_count value: {group_task_count}")
                    task_count += 0
                
                # 각 TaskGroup의 tasks를 all_tasks에 추가
                tasks = task_group.get("tasks", [])
                all_tasks.extend(tasks)

            # Display name 설정 (빈 값이면 Job ID 사용)
            display_name = processed_job.get("display_name", "")
            if not display_name:
                display_name = job_id
            
            # Job 리소스 데이터 생성
            job_data = BatchJobResource({
                "name": job_name,
                "uid": processed_job.get("uid"),
                "display_name": display_name,
                "state": processed_job.get("state"),
                "create_time": processed_job.get("create_time"),
                "update_time": processed_job.get("update_time"),
                "location_id": location_id,
                "project_id": project_id,
                "task_groups": task_groups,
                "task_count": task_count,
                "all_tasks": all_tasks,  # UI에서 표시할 모든 Task 목록
                "labels": job.get("labels", {}),
                "annotations": job.get("annotations", {}),
            })

            # Cloud Service 리소스 생성
            resource = JobResource({
                "name": job_id,  # Job ID를 리소스 이름으로 사용
                "account": project_id,
                "data": job_data,
                "reference": ReferenceModel(job_data.reference()),
                "region_code": location_id,
            })

            # 표준 응답 생성 (다른 모듈들과 동일한 방식)
            return JobResponse({"resource": resource})

        except Exception as e:
            _LOGGER.error(f"Failed to create Batch job resource for {job.get('name', 'unknown')}: {e}", exc_info=True)
            raise e


