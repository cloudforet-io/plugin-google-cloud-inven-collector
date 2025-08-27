import logging
import time
from typing import Any, Dict, List, Optional

import google.oauth2.service_account
import googleapiclient.discovery
from googleapiclient.errors import HttpError

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["DataprocClusterConnector"]
_LOGGER = logging.getLogger(__name__)


class DataprocClusterConnector(GoogleCloudConnector):
    google_client_service = "dataproc"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cache_ttl = 300  # 5 minutes cache TTL
        self._regions_cache = None
        self._cache_timestamp = 0

    def verify(self, options: Dict[str, Any], secret_data: Dict[str, Any]) -> str:
        """
        연결 상태를 검증합니다.

        Args:
            options: 검증 옵션
            secret_data: Google Cloud 인증 정보

        Returns:
            str: 연결 상태 ("ACTIVE" 또는 "INACTIVE")

        Raises:
            Exception: 연결 실패 시
        """
        try:
            self.get_connect(secret_data)
            return "ACTIVE"
        except Exception as e:
            _LOGGER.error(f"Connection verification failed: {e}")
            raise

    def get_connect(self, secret_data: Dict[str, Any]) -> None:
        """
        Google Cloud Dataproc에 연결을 초기화합니다.

        Args:
            secret_data: Google Cloud 인증을 위한 크리덴셜
                - project_id: Google Cloud 프로젝트 ID
                - 기타 service account 인증에 필요한 정보

        Raises:
            ValueError: project_id가 누락된 경우
            Exception: 인증 실패 시
        """
        if not secret_data.get("project_id"):
            raise ValueError("project_id is required in secret_data")

        self.project_id = secret_data.get("project_id")
        try:
            credentials = (
                google.oauth2.service_account.Credentials.from_service_account_info(
                    secret_data
                )
            )
            self.client = googleapiclient.discovery.build(
                "dataproc", "v1", credentials=credentials
            )
            _LOGGER.info(
                f"Successfully connected to Dataproc for project {self.project_id}"
            )
        except Exception as e:
            _LOGGER.error(f"Failed to initialize Dataproc connection: {e}")
            raise

    def list_clusters(
        self, region: Optional[str] = None, **query: Any
    ) -> List[Dict[str, Any]]:
        """
        Dataproc 클러스터 목록을 조회합니다.

        Args:
            region: 클러스터를 필터링할 리전. None일 경우 모든 리전에서 검색
            **query: API에 전달할 추가 쿼리 파라미터

        Returns:
            클러스터 리소스의 리스트

        Raises:
            ValueError: 필수 파라미터가 누락된 경우
            HttpError: Google Cloud API 에러
        """
        if not hasattr(self, "client") or not self.client:
            raise ValueError("Client not initialized. Call get_connect() first.")

        cluster_list = []

        if region:
            # 특정 리전의 클러스터 조회
            try:
                request = (
                    self.client.projects()
                    .regions()
                    .clusters()
                    .list(projectId=self.project_id, region=region, **query)
                )
                response = request.execute()
                if "clusters" in response:
                    clusters = response.get("clusters", [])
                    cluster_list.extend(clusters)
                    _LOGGER.info(f"Found {len(clusters)} clusters in region {region}")
            except HttpError as e:
                if e.resp.status == 404:
                    _LOGGER.info(f"No clusters found in region {region}")
                else:
                    _LOGGER.error(
                        f"HTTP error listing clusters in region {region}: {e}"
                    )
                    raise
            except Exception as e:
                _LOGGER.error(
                    f"Failed to list Dataproc clusters in region {region}: {e}"
                )
                raise
        else:
            # 모든 리전의 클러스터 조회
            regions = self._get_available_regions()
            for region_name in regions:
                try:
                    request = (
                        self.client.projects()
                        .regions()
                        .clusters()
                        .list(projectId=self.project_id, region=region_name, **query)
                    )
                    response = request.execute()
                    if "clusters" in response:
                        clusters = response.get("clusters", [])
                        cluster_list.extend(clusters)
                        if clusters:
                            _LOGGER.debug(
                                f"Found {len(clusters)} clusters in region {region_name}"
                            )
                except HttpError as e:
                    if e.resp.status == 404:
                        _LOGGER.debug(f"No clusters in region {region_name}")
                    else:
                        _LOGGER.warning(f"HTTP error in region {region_name}: {e}")
                except Exception as e:
                    _LOGGER.debug(f"No Dataproc clusters in region {region_name}: {e}")
                    continue

        _LOGGER.info(f"Total clusters found: {len(cluster_list)}")
        return cluster_list

    def get_cluster(self, cluster_name: str, region: str) -> Optional[Dict[str, Any]]:
        """
        특정 Dataproc 클러스터 정보를 조회합니다.

        Args:
            cluster_name: 클러스터의 이름
            region: 클러스터가 위치한 리전

        Returns:
            발견된 경우 클러스터 리소스, 그렇지 않으면 None

        Raises:
            ValueError: 필수 파라미터가 누락된 경우
            HttpError: Google Cloud API 에러 (404 제외)
        """
        if not cluster_name or not region:
            raise ValueError("cluster_name and region are required")

        if not hasattr(self, "client") or not self.client:
            raise ValueError("Client not initialized. Call get_connect() first.")

        try:
            request = (
                self.client.projects()
                .regions()
                .clusters()
                .get(projectId=self.project_id, region=region, clusterName=cluster_name)
            )
            cluster = request.execute()
            _LOGGER.info(
                f"Successfully retrieved cluster {cluster_name} from region {region}"
            )
            return cluster
        except HttpError as e:
            if e.resp.status == 404:
                _LOGGER.info(f"Cluster {cluster_name} not found in region {region}")
                return None
            else:
                _LOGGER.error(
                    f"HTTP error getting cluster {cluster_name} in region {region}: {e}"
                )
                raise
        except Exception as e:
            _LOGGER.error(
                f"Failed to get Dataproc cluster {cluster_name} in region {region}: {e}"
            )
            return None

    def list_jobs(self, region=None, cluster_name=None, **query):
        """
        Dataproc 작업 목록을 조회합니다.

        Args:
            region (str, optional): 작업을 필터링할 리전. None일 경우 모든 리전에서 검색합니다.
            cluster_name (str, optional): 작업을 필터링할 클러스터의 이름.
            **query: API에 전달할 추가 쿼리 파라미터.

        Returns:
            list: 작업 리소스의 리스트.
        """
        job_list = []

        # 클러스터 필터링
        if cluster_name:
            query["clusterName"] = cluster_name

        if region:
            try:
                request = (
                    self.client.projects()
                    .regions()
                    .jobs()
                    .list(projectId=self.project_id, region=region, **query)
                )
                response = request.execute()
                if "jobs" in response:
                    job_list.extend(response.get("jobs", []))
            except Exception as e:
                _LOGGER.error(f"Failed to list Dataproc jobs in region {region}: {e}")
        else:
            # 모든 리전의 작업 조회
            regions = self._get_available_regions()
            for region_name in regions:
                try:
                    request = (
                        self.client.projects()
                        .regions()
                        .jobs()
                        .list(projectId=self.project_id, region=region_name, **query)
                    )
                    response = request.execute()
                    if "jobs" in response:
                        job_list.extend(response.get("jobs", []))
                except Exception as e:
                    _LOGGER.debug(f"No Dataproc jobs in region {region_name}: {e}")
                    continue

        return job_list

    def list_workflow_templates(self, region=None, **query):
        """
        Dataproc 워크플로 템플릿 목록을 조회합니다.

        Args:
            region (str, optional): 템플릿을 필터링할 리전. None일 경우 모든 리전에서 검색합니다.
            **query: API에 전달할 추가 쿼리 파라미터.

        Returns:
            list: 워크플로 템플릿 리소스의 리스트.
        """
        template_list = []

        if region:
            # 특정 리전의 워크플로 템플릿 조회
            try:
                request = (
                    self.client.projects()
                    .regions()
                    .workflowTemplates()
                    .list(
                        parent=f"projects/{self.project_id}/regions/{region}", **query
                    )
                )
                response = request.execute()
                if "templates" in response:
                    template_list.extend(response.get("templates", []))
            except Exception as e:
                _LOGGER.error(
                    f"Failed to list Dataproc workflow templates in region {region}: {e}"
                )
        else:
            # 모든 리전의 워크플로 템플릿 조회
            regions = self._get_available_regions()
            for region_name in regions:
                try:
                    request = (
                        self.client.projects()
                        .regions()
                        .workflowTemplates()
                        .list(
                            parent=f"projects/{self.project_id}/regions/{region_name}",
                            **query,
                        )
                    )
                    response = request.execute()
                    if "templates" in response:
                        template_list.extend(response.get("templates", []))
                except Exception as e:
                    _LOGGER.debug(
                        f"No Dataproc workflow templates in region {region_name}: {e}"
                    )
                    continue

        return template_list

    def list_autoscaling_policies(self, region=None, **query):
        """
        Dataproc 오토스케일링 정책 목록을 조회합니다.

        Args:
            region (str, optional): 정책을 필터링할 리전. None일 경우 모든 리전에서 검색합니다.
            **query: API에 전달할 추가 쿼리 파라미터.

        Returns:
            list: 오토스케일링 정책 리소스의 리스트.
        """
        policy_list = []

        if region:
            # 특정 리전의 오토스케일링 정책 조회
            try:
                request = (
                    self.client.projects()
                    .regions()
                    .autoscalingPolicies()
                    .list(
                        parent=f"projects/{self.project_id}/regions/{region}", **query
                    )
                )
                response = request.execute()
                if "policies" in response:
                    policy_list.extend(response.get("policies", []))
            except Exception as e:
                _LOGGER.error(
                    f"Failed to list Dataproc autoscaling policies in region {region}: {e}"
                )
        else:
            # 모든 리전의 오토스케일링 정책 조회
            regions = self._get_available_regions()
            for region_name in regions:
                try:
                    request = (
                        self.client.projects()
                        .regions()
                        .autoscalingPolicies()
                        .list(
                            parent=f"projects/{self.project_id}/regions/{region_name}",
                            **query,
                        )
                    )
                    response = request.execute()
                    if "policies" in response:
                        policy_list.extend(response.get("policies", []))
                except Exception as e:
                    _LOGGER.debug(
                        f"No Dataproc autoscaling policies in region {region_name}: {e}"
                    )
                    continue

        return policy_list

    def _get_available_regions(self) -> List[str]:
        """
        사용 가능한 Dataproc 리전 목록을 반환합니다.

        캐시를 사용하여 성능을 최적화합니다.

        Returns:
            Dataproc을 사용할 수 있는 Google Cloud 리전의 리스트
        """
        current_time = time.time()

        # 캐시가 유효한 경우 캐시된 값 반환
        if (
            self._regions_cache is not None
            and current_time - self._cache_timestamp < self._cache_ttl
        ):
            return self._regions_cache

        # 캐시 만료 또는 최초 호출 시 새로 로드
        regions = [
            "asia-east1",
            "asia-east2",
            "asia-northeast1",
            "asia-northeast2",
            "asia-northeast3",
            "asia-south1",
            "asia-south2",
            "asia-southeast1",
            "asia-southeast2",
            "australia-southeast1",
            "australia-southeast2",
            "europe-north1",
            "europe-west1",
            "europe-west2",
            "europe-west3",
            "europe-west4",
            "europe-west6",
            "europe-central2",
            "northamerica-northeast1",
            "northamerica-northeast2",
            "southamerica-east1",
            "southamerica-west1",
            "us-central1",
            "us-east1",
            "us-east4",
            "us-west1",
            "us-west2",
            "us-west3",
            "us-west4",
        ]

        # 캐시 업데이트
        self._regions_cache = regions
        self._cache_timestamp = current_time

        _LOGGER.debug(f"Loaded {len(regions)} available regions for Dataproc")
        return regions
