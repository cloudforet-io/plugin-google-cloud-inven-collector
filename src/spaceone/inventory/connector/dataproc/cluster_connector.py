import logging
import socket
import ssl
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

import google.oauth2.service_account
import googleapiclient.discovery
from googleapiclient.errors import HttpError

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["DataprocClusterConnector"]
logger = logging.getLogger(__name__)


class DataprocClusterConnector(GoogleCloudConnector):
    google_client_service = "dataproc"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cache_ttl = 300  # 5 minutes cache TTL
        self._regions_cache = None
        self._cache_timestamp = 0
        self._client_lock = threading.Lock()  # 스레드 안전성을 위한 락
        self._thread_local = threading.local()  # 스레드별 독립적인 클라이언트

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
            logger.error(f"Connection verification failed: {e}")
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
            logger.info("Successfully connected to Dataproc service")
        except ValueError as e:
            logger.error(f"Invalid service account credentials: {e}")
            raise
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Network error during Dataproc connection: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Dataproc connection: {e}")
            raise

    def _get_thread_safe_client(self):
        """
        스레드별로 독립적인 클라이언트 인스턴스를 반환합니다.

        Returns:
            스레드별 독립적인 Google API 클라이언트
        """
        if (
            not hasattr(self._thread_local, "client")
            or self._thread_local.client is None
        ):
            # 각 스레드마다 독립적인 클라이언트 생성
            try:
                if hasattr(self, "credentials") and self.credentials:
                    self._thread_local.client = googleapiclient.discovery.build(
                        "dataproc",
                        "v1",
                        credentials=self.credentials,
                        cache_discovery=False,
                    )
                else:
                    # 메인 클라이언트가 있는 경우 크리덴셜을 추출하여 새 클라이언트 생성
                    if hasattr(self, "client") and self.client:
                        # 기본 클라이언트에서 크리덴셜 가져오기
                        credentials = getattr(self.client, "_credentials", None)
                        if credentials:
                            self._thread_local.client = googleapiclient.discovery.build(
                                "dataproc",
                                "v1",
                                credentials=credentials,
                                cache_discovery=False,
                            )
                        else:
                            self._thread_local.client = self.client
                    else:
                        raise ValueError(
                            "No client or credentials available for thread-safe access"
                        )
            except Exception as e:
                logger.error(f"Failed to create thread-safe client: {e}")
                # Fallback to main client (thread-unsafe but functional)
                self._thread_local.client = getattr(self, "client", None)

        return self._thread_local.client

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
                    logger.info(f"Found {len(clusters)} clusters in specified region")
            except HttpError as e:
                if e.resp.status == 404:
                    logger.info("No clusters found in specified region")
                else:
                    logger.error(f"HTTP error listing clusters in region: {e}")
                    raise
            except Exception as e:
                logger.error(f"Failed to list Dataproc clusters in region: {e}")
                raise
        else:
            # 모든 리전의 클러스터 조회 (병렬 처리)
            cluster_list = self._list_clusters_parallel(**query)

        logger.info(f"Total clusters found: {len(cluster_list)}")
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
            logger.info("Successfully retrieved cluster from region")
            return cluster
        except HttpError as e:
            if e.resp.status == 404:
                logger.info("Cluster not found in specified region")
                return None
            else:
                logger.error(f"HTTP error getting cluster in region: {e}")
                raise
        except Exception as e:
            logger.error(f"Failed to get Dataproc cluster in region: {e}")
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
                logger.error(f"Failed to list Dataproc jobs in region: {e}")
        else:
            # 모든 리전의 작업 조회 (병렬 처리)
            job_list = self._list_jobs_parallel(**query)

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
                logger.error(
                    f"Failed to list Dataproc workflow templates in region: {e}"
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
                    logger.debug(f"No Dataproc workflow templates in region: {e}")
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
                logger.error(
                    f"Failed to list Dataproc autoscaling policies in region: {e}"
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
                    logger.debug(f"No Dataproc autoscaling policies in region: {e}")
                    continue

        return policy_list

    def _list_clusters_parallel(self, **query) -> List[Dict[str, Any]]:
        """
        병렬 처리를 통해 모든 리전의 클러스터를 조회합니다.

        Args:
            **query: API에 전달할 추가 쿼리 파라미터

        Returns:
            모든 리전에서 발견된 클러스터 리스트
        """
        start_time = time.time()
        regions = self._get_optimized_regions()
        cluster_list = []

        # ThreadPoolExecutor를 사용한 병렬 처리 (메모리 제약 환경 최적화)
        MAX_WORKERS = (
            2  # 메모리 제약 환경에서 안정적 성능을 위한 최적 설정 (실측 테스트 검증)
        )
        max_workers = min(MAX_WORKERS, len(regions))

        # 병렬 처리 시작 로깅
        logger.info(
            f"🚀 Starting parallel cluster collection: "
            f"regions={len(regions)}, max_workers={max_workers}, "
            f"global_timeout=90s, individual_timeout=60s (MAX_WORKERS={MAX_WORKERS})"
        )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 각 리전에 대해 비동기 작업 생성
            future_to_region = {
                executor.submit(self._list_clusters_in_region, region, **query): region
                for region in regions
            }

            # 완료된 작업 결과 수집 (더 긴 타임아웃)
            try:
                for future in as_completed(
                    future_to_region, timeout=90
                ):  # 90초 타임아웃
                    region = future_to_region[future]
                    try:
                        clusters = future.result(timeout=60)  # 개별 작업 60초 타임아웃
                        if clusters:
                            cluster_list.extend(clusters)
                            logger.debug(
                                f"Found {len(clusters)} clusters in region {region}"
                            )
                    except Exception as e:
                        logger.debug(f"Error processing region {region}: {e}")
                        continue
            except Exception as e:
                logger.warning(f"Timeout waiting for region processing: {e}")

        # 병렬 처리 완료 로깅
        execution_time = time.time() - start_time
        logger.info(
            f"✅ Parallel cluster collection completed: "
            f"total_clusters={len(cluster_list)}, "
            f"processed_regions={len(regions)}, "
            f"execution_time={execution_time:.2f}s, "
            f"avg_time_per_region={execution_time / len(regions):.2f}s, "
            f"throughput={len(cluster_list) / execution_time:.1f} clusters/sec"
        )

        return cluster_list

    def _list_jobs_parallel(self, **query) -> List[Dict[str, Any]]:
        """
        병렬 처리를 통해 모든 리전의 작업을 조회합니다.

        Args:
            **query: API에 전달할 추가 쿼리 파라미터

        Returns:
            모든 리전에서 발견된 작업 리스트
        """
        start_time = time.time()
        regions = self._get_optimized_regions()
        job_list = []

        # 작업 수집은 클러스터보다 덜 중요하므로 더 적은 워커 사용 (메모리 제약 환경 최적화)
        MAX_JOB_WORKERS = (
            1  # 메모리 제약 환경에서 안정적 성능을 위한 최적 설정 (실측 테스트 검증)
        )
        max_workers = min(MAX_JOB_WORKERS, len(regions))

        # 병렬 처리 시작 로깅
        logger.info(
            f"⚡ Starting parallel job collection: "
            f"regions={len(regions)}, max_workers={max_workers}, "
            f"individual_timeout=15s (MAX_JOB_WORKERS={MAX_JOB_WORKERS})"
        )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_region = {
                executor.submit(self._list_jobs_in_region, region, **query): region
                for region in regions
            }

            for future in as_completed(future_to_region):
                region = future_to_region[future]
                try:
                    jobs = future.result(
                        timeout=15
                    )  # 15초 타임아웃 (클러스터보다 짧게)
                    if jobs:
                        job_list.extend(jobs)
                except Exception as e:
                    logger.debug(f"Error processing jobs in region {region}: {e}")
                    continue

        # 병렬 처리 완료 로깅
        execution_time = time.time() - start_time
        logger.info(
            f"⚡ Parallel job collection completed: "
            f"total_jobs={len(job_list)}, "
            f"processed_regions={len(regions)}, "
            f"execution_time={execution_time:.2f}s, "
            f"throughput={len(job_list) / max(execution_time, 0.001):.1f} jobs/sec"
        )

        return job_list

    def _list_jobs_in_region(self, region: str, **query) -> List[Dict[str, Any]]:
        """
        특정 리전의 작업을 조회합니다 (강화된 에러 처리 포함).

        Args:
            region: 조회할 리전명
            **query: API에 전달할 추가 쿼리 파라미터

        Returns:
            해당 리전의 작업 리스트
        """
        max_retries = 2  # Job은 클러스터보다 덜 중요하므로 재시도 횟수 축소
        retry_delay = 1

        for attempt in range(max_retries):
            client = None
            try:
                # 스레드별 독립적인 클라이언트 사용
                client = self._get_thread_safe_client()
                if not client:
                    logger.warning(f"No client available for jobs in region {region}")
                    return []

                request = (
                    client.projects()
                    .regions()
                    .jobs()
                    .list(projectId=self.project_id, region=region, **query)
                )
                response = request.execute()
                return response.get("jobs", [])

            except HttpError as e:
                if e.resp.status in [404, 403]:
                    return []
                elif e.resp.status == 429 and attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    logger.debug(f"HTTP error listing jobs in region {region}: {e}")
                    return []

            except (ConnectionError, TimeoutError, socket.timeout, ssl.SSLError) as e:
                if attempt < max_retries - 1:
                    logger.debug(
                        f"Network/SSL error listing jobs in region {region}, retrying: {e}"
                    )
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    logger.debug(
                        f"Network/SSL error listing jobs in region {region}: {e}"
                    )
                    return []

            except Exception as e:
                logger.debug(f"No Dataproc jobs in region {region}: {e}")
                return []

        return []

    def _list_clusters_in_region(self, region: str, **query) -> List[Dict[str, Any]]:
        """
        특정 리전의 클러스터를 조회합니다 (강화된 에러 처리 및 스레드 안전성 포함).

        Args:
            region: 조회할 리전명
            **query: API에 전달할 추가 쿼리 파라미터

        Returns:
            해당 리전의 클러스터 리스트
        """
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            client = None
            try:
                # 스레드별 독립적인 클라이언트 사용
                client = self._get_thread_safe_client()
                if not client:
                    logger.warning(f"No client available for region {region}")
                    return []

                request = (
                    client.projects()
                    .regions()
                    .clusters()
                    .list(projectId=self.project_id, region=region, **query)
                )
                response = request.execute()
                return response.get("clusters", [])

            except HttpError as e:
                if e.resp.status in [404, 403]:
                    # 404: 리전에 클러스터 없음, 403: 접근 권한 없음
                    return []
                elif e.resp.status == 429:
                    # Rate limit - 지수백오프로 대기
                    wait_time = retry_delay * (2**attempt)
                    logger.warning(
                        f"Rate limit in region {region}, waiting {wait_time}s"
                    )
                    time.sleep(wait_time)
                    continue
                elif e.resp.status >= 500:
                    # 서버 에러 - 재시도
                    if attempt < max_retries - 1:
                        logger.warning(f"Server error in region {region}, retrying...")
                        time.sleep(retry_delay * (attempt + 1))
                        continue
                else:
                    logger.warning(f"HTTP error in region {region}: {e}")
                    return []

            except (ConnectionError, TimeoutError, socket.timeout) as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Network error in region {region}, retrying (attempt {attempt + 1}): {e}"
                    )
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    logger.warning(
                        f"Network error in region {region} after {max_retries} attempts: {e}"
                    )
                    return []

            except ssl.SSLError as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"SSL error in region {region}, retrying (attempt {attempt + 1}): {e}"
                    )
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    logger.warning(
                        f"SSL error in region {region} after {max_retries} attempts: {e}"
                    )
                    return []

            except Exception as e:
                # 예상치 못한 에러는 로그만 남기고 빈 리스트 반환
                logger.debug(f"Unexpected error in region {region}: {e}")
                return []

        return []

    def _get_optimized_regions(self) -> List[str]:
        """
        최적화된 리전 목록을 반환합니다.

        동적 조회 실패 시 핵심 리전만 조회하여 성능을 개선합니다.

        Returns:
            최적화된 리전 리스트
        """
        current_time = time.time()

        # 캐시가 유효한 경우 캐시된 값 반환
        if (
            self._regions_cache is not None
            and current_time - self._cache_timestamp < self._cache_ttl
        ):
            return self._regions_cache

        try:
            # 동적 리전 조회 시도
            regions = self._fetch_dataproc_regions()
            logger.info(
                f"Successfully fetched {len(regions)} Dataproc regions dynamically"
            )
        except Exception as e:
            logger.warning(f"Failed to fetch dynamic regions, using core regions: {e}")
            # 동적 조회 실패 시 핵심 리전만 사용 (성능 최적화)
            regions = self._get_core_regions()

        # 캐시 업데이트
        self._regions_cache = regions
        self._cache_timestamp = current_time

        logger.debug(f"Using {len(regions)} regions for Dataproc scanning")
        return regions

    def _get_core_regions(self) -> List[str]:
        """
        핵심 리전만 반환하여 성능을 최적화합니다.

        Returns:
            주요 사용 리전 리스트
        """
        return [
            # 아시아 주요 리전
            "asia-east1",  # 대만
            "asia-northeast1",  # 도쿄
            "asia-northeast3",  # 서울
            "asia-southeast1",  # 싱가포르
            # 유럽 주요 리전
            "europe-west1",  # 벨기에
            "europe-west4",  # 네덜란드
            # 미국 주요 리전
            "us-central1",  # 아이오와
            "us-east1",  # 사우스 캐롤라이나
            "us-west1",  # 오레곤
            "us-west2",  # 로스앤젤레스
        ]

    def _get_available_regions(self) -> List[str]:
        """
        사용 가능한 Dataproc 리전 목록을 반환합니다.

        캐시를 사용하여 성능을 최적화하며, 동적으로 리전 목록을 조회합니다.

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

        # 동적 리전 조회 시도, 실패 시 fallback 사용
        try:
            regions = self._fetch_dataproc_regions()
            logger.info(
                f"Successfully fetched {len(regions)} Dataproc regions dynamically"
            )
        except Exception as e:
            logger.warning(f"Failed to fetch dynamic regions, using fallback: {e}")
            regions = self._get_fallback_regions()

        # 캐시 업데이트
        self._regions_cache = regions
        self._cache_timestamp = current_time

        logger.debug(f"Loaded {len(regions)} available regions for Dataproc")
        return regions

    def _fetch_dataproc_regions(self) -> List[str]:
        """
        Google Cloud API를 통해 Dataproc 지원 리전을 동적으로 조회합니다.

        Returns:
            Dataproc을 지원하는 Google Cloud 리전의 리스트

        Raises:
            Exception: API 호출 실패 시
        """
        if not hasattr(self, "client") or not self.client:
            raise ValueError("Client not initialized for dynamic region fetching")

        try:
            # Compute Engine API를 통해 사용 가능한 리전 조회
            # 부모 클래스에서 설정된 credentials 사용
            compute_client = googleapiclient.discovery.build(
                "compute", "v1", credentials=self.credentials
            )
            request = compute_client.regions().list(project=self.project_id)
            response = request.execute()

            all_regions = []
            if "items" in response:
                for region in response["items"]:
                    region_name = region.get("name", "")
                    # Dataproc 지원 리전 필터링 (일반적으로 대부분의 리전에서 지원)
                    if region_name and region.get("status") == "UP":
                        all_regions.append(region_name)

            # 일반적으로 알려진 Dataproc 미지원 리전 제외
            excluded_regions = {"global"}
            supported_regions = [r for r in all_regions if r not in excluded_regions]

            if not supported_regions:
                raise Exception("No supported regions found")

            return sorted(supported_regions)

        except Exception as e:
            logger.error(f"Failed to fetch regions from Compute API: {e}")
            raise

    def _get_fallback_regions(self) -> List[str]:
        """
        동적 조회 실패 시 사용할 fallback 리전 목록을 반환합니다.

        Returns:
            알려진 Dataproc 지원 리전의 리스트
        """
        return [
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
