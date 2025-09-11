import logging
import re
import time
from typing import Dict, List, Tuple

from spaceone.inventory.connector.batch.batch_v1 import BatchV1Connector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.batch_processor import BatchJobProcessor
from spaceone.inventory.libs.schema.base import ReferenceModel, reset_state_counters, log_state_summary
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResponse
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

    connector_name = "BatchV1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params) -> Tuple[List[CloudServiceResponse], List]:
        """
        Batch 리소스를 효율적으로 수집합니다.

        Args:
            params: 수집 파라미터 (secret_data, options, schema, filter)

        Returns:
            Tuple[List[CloudServiceResponse], List]: (수집된 리소스들, 에러 응답들)
        """
        _LOGGER.debug("** Batch START **")
        start_time = time.time()

        # v2.0 로깅 시스템 초기화
        reset_state_counters()

        collected_cloud_services = []
        error_responses = []

        try:
            project_id = params["secret_data"]["project_id"]
            batch_connector = self._get_connector(params)

            # 1. 글로벌 Jobs 수집 (locations/- 패턴)
            all_jobs = batch_connector.list_all_jobs()
            if not all_jobs:
                _LOGGER.info("No Batch jobs found in any location")
                return collected_cloud_services, error_responses

            _LOGGER.debug(f"Found {len(all_jobs)} Batch jobs across all locations")

            # 2. Location별 그룹핑 및 리소스 생성
            jobs_by_location = self._group_jobs_by_location(all_jobs)

            for location_id, location_jobs in jobs_by_location.items():
                try:
                    resource = self._create_location_resource(
                        location_id, location_jobs, project_id, batch_connector, params
                    )
                    collected_cloud_services.append(resource)

                    _LOGGER.debug(
                        f"Collected Batch Location: {location_id} with {len(location_jobs)} jobs"
                    )

                except Exception as e:
                    _LOGGER.error(f"Failed to process location {location_id}: {e}", exc_info=True)
                    error_responses.append(
                        self.generate_resource_error_response(
                            e, "Batch", "Location", location_id
                        )
                    )

        except Exception as e:
            _LOGGER.error(f"Batch collection failed: {e}", exc_info=True)
            error_responses.append(
                self.generate_resource_error_response(e, "Batch", "Service", "batch")
            )

        # v2.0 로깅 시스템: 수집 완료 시 상태 요약 로깅
        log_state_summary()
        _LOGGER.debug(f"** Batch Finished {time.time() - start_time:.2f} Seconds **")
        _LOGGER.info(f"Collected {len(collected_cloud_services)} Batch Locations")
        return collected_cloud_services, error_responses

    def _get_connector(self, params) -> BatchV1Connector:
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
        Job name에서 location ID를 추출합니다 (정규 표현식 사용).

        Args:
            job_name: Job의 전체 경로명

        Returns:
            str: Location ID 또는 'unknown'
        """
        try:
            # Job name 형태: projects/{project}/locations/{location}/jobs/{job_id}
            job_pattern = r'projects/([^/]+)/locations/([^/]+)/jobs/([^/]+)'
            match = re.match(job_pattern, job_name)
            
            if match:
                location_id = match.group(2)
                return location_id

        except Exception as e:
            _LOGGER.warning(f"Error parsing job name {job_name}: {e}")

        _LOGGER.warning(f"Could not extract location from job name: {job_name}")
        return "unknown"

    def _create_location_resource(
        self,
        location_id: str,
        location_jobs: List[Dict],
        project_id: str,
        batch_connector: BatchV1Connector,
        params: Dict,
    ) -> CloudServiceResponse:
        """
        Location 리소스를 생성합니다.

        Args:
            location_id: Location ID
            location_jobs: 해당 location의 jobs 리스트
            project_id: Project ID
            batch_connector: Batch connector
            params: 수집 파라미터

        Returns:
            CloudServiceResponse: 생성된 리소스 응답
        """
        try:
            # Jobs 데이터 처리 (헬퍼 클래스 사용)
            job_processor = BatchJobProcessor(batch_connector)
            processed_jobs = job_processor.process_jobs(location_jobs)

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

            # 표준 응답 생성 (다른 모듈들과 동일한 방식)
            return LocationResponse({"resource": resource})

        except Exception as e:
            _LOGGER.error(f"Failed to create Batch location resource for {location_id}: {e}", exc_info=True)
            raise e


