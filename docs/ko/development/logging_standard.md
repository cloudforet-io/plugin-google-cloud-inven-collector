---
alwaysApply: true
---

# SpaceONE Google Cloud Inventory Collector 로깅 표준

## 로깅의 필요성

-   **문제 진단**: Google Cloud API 오류 원인 파악, 수집 성능 병목 식별
-   **보안**: 인증 시도 탐지, Google Cloud 리소스 접근 감사
-   **운영 모니터링**: 인벤토리 수집 상태, 플러그인 성능 추적

### ⚠️ print() 사용 절대 금지

```python
# ❌ 절대 금지
print(f"Collecting clusters from project {project_id}")

# ✅ 올바른 방법
logger.info(f"Collecting clusters from project {project_id}")
```

## 로깅 레벨 이해하기

### 로깅 레벨별 사용 목적 (SpaceONE 플러그인 특화)

각 로깅 레벨은 **명확한 목적**을 가지고 있습니다:

| 레벨         | 목적                   | 언제 사용할까?         | SpaceONE 플러그인 예시                     |
| ------------ | ---------------------- | ---------------------- | ------------------------------------------ |
| **DEBUG**    | 상세한 개발 정보       | 개발/테스트 환경에서만 | API 요청/응답 상세, 데이터 변환 과정       |
| **INFO**     | 정상적인 프로세스 흐름 | 중요한 수집 이벤트     | 수집 시작/완료, 리소스 발견, 인증 성공     |
| **WARNING**  | 예상 가능한 문제       | 복구 가능한 오류 상황  | API 할당량 경고, 리전 접근 제한            |
| **ERROR**    | 처리되지 않은 오류     | 기능 실행 실패         | 인증 실패, API 호출 오류, 데이터 파싱 실패 |
| **CRITICAL** | 서비스 중단급 오류     | 시스템 전체 장애       | 플러그인 초기화 실패, 치명적 설정 오류     |

### 환경별 로깅 레벨 설정

```
로컬 개발환경: DEBUG 이상 (상세한 API 디버깅)
SpaceONE 테스트환경: INFO 이상 (수집 플로우 추적)
SpaceONE 스테이징환경: INFO 이상 (성능 모니터링)
SpaceONE 운영환경: WARNING 이상 (오류 및 경고만)
```

## 무엇을 언제 로그해야 하는가?

### 필수 로깅 대상 (Google Cloud 수집기 특화)

**1. 인증 및 권한 관련**

-   Google Cloud Service Account 인증 시도 (성공/실패)
-   프로젝트별 권한 확인 결과
-   API 키 갱신 및 만료

**2. 중요한 수집 이벤트**

-   수집 작업 시작/완료
-   리소스 발견 및 분류
-   새로운 리소스 유형 감지

**3. Google Cloud API 상태**

-   API 응답 시간 및 상태
-   할당량 사용량 및 제한
-   리전별 가용성 확인

**4. 오류 및 예외 상황**

-   API 호출 실패 및 재시도
-   데이터 변환 오류
-   네트워크 연결 문제

### 로깅하지 말아야 할 데이터

**절대 로깅 금지 항목:**

-   **인증 정보**: Service Account 키, 액세스 토큰 원문
-   **민감한 리소스 정보**: 내부 IP, 보안 그룹 세부사항
-   **개인정보**: 사용자 식별 정보, 이메일
-   **기밀 정보**: 프로젝트 내부 구조, 보안 정책

**⚠️ 보안 위험 예시:**

```python
# ❌ 절대 하지 말 것
logger.info(f"Service account key: {service_account_key}")
logger.debug(f"Access token: {access_token}")
logger.info(f"Internal IP: {instance.internal_ip}")

# ✅ 올바른 방법
logger.info("Service account authentication successful")
logger.debug("Access token refreshed successfully")
logger.info(f"Instance discovered: {instance.name} in zone {instance.zone}")
```

## 구조화된 로깅

### JSON 형태 로깅 설정

```python
import logging
import json
from datetime import datetime

class SpaceONEJSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "plugin": "google-cloud-inventory-collector",
            "service": getattr(record, 'service', 'unknown')
        }
        return json.dumps(log_data, ensure_ascii=False)

def setup_logging():
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(SpaceONEJSONFormatter())
    logger.addHandler(handler)
```

### 실용적 로깅 방법

**간단한 메시지 내 포함 방식 권장:**

```python
# ✅ 권장: 메시지 내 직접 포함
logger.info(f"Collected {cluster_count} Dataproc clusters from project {project_id}")
logger.warning(f"API quota 80% reached for project {project_id}")
logger.error(f"Failed to connect to region {region}: {error}")

# 복잡한 extra 사용은 특별한 경우에만
logger.info("Critical collection event", extra={'event_type': 'quota_exceeded', 'project': project_id})
```

## 레이어별 로깅 전략 (SpaceONE 플러그인 구조)

### 1. Service 레이어 (spaceone/inventory/service/collector_service.py)

- 플러그인 엔트리포인트 및 수집 작업 전체 플로우
- 인증 및 권한 검증
- 전체 수집 성능 및 결과 요약
- 상태 카운터 초기화 및 최종 요약 로깅

```python
import logging
import time
from spaceone.core.service import BaseService
from spaceone.inventory.manager.dataproc.cluster_manager import DataprocClusterManager
from spaceone.inventory.libs.schema.base import (
    reset_state_counters,
    log_state_summary
)

logger = logging.getLogger(__name__)

class CollectorService(BaseService):
    def collect_cloud_service(self, secret_data, options, **kwargs):
        start_time = time.time()
        
        # 상태 카운터 초기화
        reset_state_counters()
        
        logger.info(f"Starting Google Cloud Dataproc collection for project {secret_data.get('project_id')}")
        
        try:
            cluster_manager = DataprocClusterManager()
            resources = cluster_manager.collect_resources(secret_data, options)
            
            # 최종 요약 정보 로깅
            log_state_summary()
            logger.info(f"Successfully collected {len(resources)} Dataproc clusters in {time.time() - start_time:.2f}s")
            return resources
        except Exception as e:
            logger.error(f"Failed to collect Dataproc resources: {str(e)}")
            raise
    
    @staticmethod
    def generate_error_response(e, cloud_service_group, cloud_service_type):
        """
        개선된 로깅 기능을 사용하여 에러 응답을 생성합니다.
        """
        from spaceone.inventory.libs.schema.cloud_service import ErrorResourceResponse
        import json
        
        if type(e) is dict:
            error_message = json.dumps(e)
            error_code = "DICT_ERROR"
        else:
            error_message = str(e)
            error_code = type(e).__name__
        
        # 로깅과 함께 에러 응답 생성
        return ErrorResourceResponse.create_with_logging(
            error_message=error_message,
            error_code=error_code,
            additional_data={
                "cloud_service_group": cloud_service_group,
                "cloud_service_type": cloud_service_type,
            }
        )
```

### 2. Manager 레이어 (spaceone/inventory/manager/dataproc/cluster_manager.py)

- 비즈니스 로직 실행
- 데이터 변환 및 검증
- Connector 호출 결과 처리

```python
import logging
from spaceone.core.manager import BaseManager
from spaceone.inventory.connector.dataproc.cluster_connector import DataprocClusterConnector

logger = logging.getLogger(__name__)

class DataprocClusterManager(BaseManager):
    def collect_resources(self, secret_data, options):
        logger.info("Starting Dataproc cluster collection")
        
        connector = DataprocClusterConnector()
        connector.set_secret_data(secret_data)
        
        try:
            # 리전별 순차 수집
            regions = connector.list_regions()
            logger.debug(f"Found {len(regions)} regions for Dataproc collection")
            
            resources = []
            for region in regions:
                clusters = connector.list_clusters(region)
                logger.debug(f"Found {len(clusters)} clusters in region {region}")
                resources.extend(self._convert_clusters_to_resources(clusters))
            
            logger.info(f"Collected {len(resources)} total Dataproc clusters")
            return resources
            
        except Exception as e:
            logger.error(f"Error during cluster collection: {str(e)}")
            raise
```

### 3. Connector 레이어 (spaceone/inventory/connector/dataproc/cluster_connector.py)

- Google Cloud API 호출
- 외부 API 응답 처리
- 순차 처리 및 안정성
- 네트워크 오류 및 재시도 로직

```python
import logging
import time
import socket
import ssl
# 순차 처리 방식으로 변경됨 - ThreadPoolExecutor 사용 안 함
from googleapiclient.errors import HttpError
from spaceone.core.connector import BaseConnector

logger = logging.getLogger(__name__)

class DataprocClusterConnector(BaseConnector):
    def list_clusters(self, **query):
        """순차 처리를 통한 모든 리전의 클러스터 조회"""
        if query.get("region"):
            # 특정 리전 조회
            return self._list_single_region_clusters(query["region"], **query)
        else:
            # 모든 리전 병렬 조회
            return self._list_clusters_sequential(**query)
    
    def _list_clusters_parallel(self, **query):
        """병렬 처리를 통해 모든 리전의 클러스터를 조회합니다."""
        regions = self._get_optimized_regions()
        cluster_list = []
        
        # 메모리 안정성을 위해 최대 3개 워커로 제한
        max_workers = min(3, len(regions))
        
        logger.info(f"Starting parallel cluster collection across {len(regions)} regions with {max_workers} workers")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_region = {
                executor.submit(self._list_clusters_in_region, region, **query): region
                for region in regions
            }
            
            try:
                for future in as_completed(future_to_region, timeout=90):
                    region = future_to_region[future]
                    try:
                        clusters = future.result(timeout=60)
                        if clusters:
                            cluster_list.extend(clusters)
                            logger.debug(f"Found {len(clusters)} clusters in region {region}")
                    except Exception as e:
                        logger.debug(f"Error processing region {region}: {e}")
                        continue
                        
            except Exception as e:
                logger.warning(f"Timeout waiting for region processing: {e}")
        
        logger.info(f"Parallel collection completed: {len(cluster_list)} total clusters")
        return cluster_list
    
    def _list_clusters_in_region(self, region, **query):
        """특정 리전의 클러스터를 조회 (강화된 에러 처리 포함)"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                # 스레드별 독립적인 클라이언트 사용
                client = self._get_thread_safe_client()
                if not client:
                    logger.warning(f"No client available for region {region}")
                    return []
                
                request = client.projects().regions().clusters().list(
                    projectId=self.project_id, region=region, **query
                )
                response = request.execute()
                return response.get("clusters", [])
                
            except HttpError as e:
                if e.resp.status in [404, 403]:
                    return []
                elif e.resp.status == 429:
                    wait_time = retry_delay * (2**attempt)
                    logger.warning(f"Rate limit in region {region}, waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                elif e.resp.status >= 500 and attempt < max_retries - 1:
                    logger.warning(f"Server error in region {region}, retrying...")
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    logger.warning(f"HTTP error in region {region}: {e}")
                    return []
                    
            except (ConnectionError, TimeoutError, socket.timeout, ssl.SSLError) as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Network/SSL error in region {region}, retrying (attempt {attempt + 1}): {e}")
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    logger.warning(f"Network/SSL error in region {region} after {max_retries} attempts: {e}")
                    return []
                    
            except Exception as e:
                logger.debug(f"Unexpected error in region {region}: {e}")
                return []
        
        return []
```

### 4. 순차 처리 로깅 패턴 (v3.0) - 안정성 최적화

순차 처리 시스템에서는 메모리 효율성과 안정성을 우선시하며, 각 단계별 처리 상태를 상세히 로깅합니다:

```python
import logging
import time
# 순차 처리 방식으로 변경됨 - ThreadPoolExecutor 사용 안 함

logger = logging.getLogger(__name__)

def _list_clusters_parallel(self, **query):
    """병렬 처리를 통한 클러스터 수집 (상세 로깅 포함)"""
    start_time = time.time()
    regions = self._get_optimized_regions()
    cluster_list = []
    
    # 고성능 워커 수 및 타임아웃 설정 (최적화됨)
    max_workers = min(12, len(regions))  # 최고 성능을 위한 12개 워커
    
    # 병렬 처리 시작 로깅 (최적화된 설정 정보 포함)
    logger.info(
        f"🚀 Starting parallel cluster collection: "
        f"regions={len(regions)}, max_workers={max_workers}, "
        f"global_timeout=90s, individual_timeout=60s (optimized for 12 workers)"
    )
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_region = {
            executor.submit(self._list_clusters_in_region, region, **query): region
            for region in regions
        }
        
        try:
            for future in as_completed(future_to_region, timeout=90):
                region = future_to_region[future]
                try:
                    clusters = future.result(timeout=60)
                    if clusters:
                        cluster_list.extend(clusters)
                        logger.debug(f"Found {len(clusters)} clusters in region {region}")
                except Exception as e:
                    logger.debug(f"Error processing region {region}: {e}")
                    continue
                    
        except Exception as e:
            logger.warning(f"Timeout waiting for region processing: {e}")
    
    # 병렬 처리 완료 로깅 (성능 메트릭 포함)
    execution_time = time.time() - start_time
    logger.info(
        f"✅ Parallel cluster collection completed: "
        f"total_clusters={len(cluster_list)}, "
        f"processed_regions={len(regions)}, "
        f"execution_time={execution_time:.2f}s, "
        f"avg_time_per_region={execution_time / len(regions):.2f}s, "
        f"throughput={len(cluster_list)/execution_time:.1f} clusters/sec"
    )
    
    return cluster_list

def _list_jobs_parallel(self, **query):
    """병렬 작업 수집 (최적화된 로깅)"""
    start_time = time.time()
    regions = self._get_optimized_regions()
    job_list = []
    
    # 작업 수집용 최적화된 워커 수 (6개로 증가)
    max_workers = min(6, len(regions))  # 최고 성능을 위한 6개 워커
    
    logger.info(
        f"⚡ Starting parallel job collection: "
        f"regions={len(regions)}, max_workers={max_workers}, "
        f"individual_timeout=15s (optimized for 6 workers)"
    )
    
    # ... 처리 로직 ...
    
    execution_time = time.time() - start_time
    logger.info(
        f"⚡ Parallel job collection completed: "
        f"total_jobs={len(job_list)}, "
        f"processed_regions={len(regions)}, "
        f"execution_time={execution_time:.2f}s, "
        f"throughput={len(job_list)/max(execution_time, 0.001):.1f} jobs/sec"
    )
    
    return job_list
```

#### 병렬 처리 로깅 가이드라인 (v2.0 고성능 최적화)

**시작 로깅 (INFO 레벨)**:
- 고성능 워커 수 (`max_workers=12` for clusters, `max_workers=6` for jobs)
- 처리 대상 수 (`regions=N`)
- 차등 타임아웃 설정 (`global_timeout=90s, individual_timeout=60s/15s`)
- 최적화 정보 (`optimized for 12 workers` / `optimized for 6 workers`)

**완료 로깅 (INFO 레벨)**:
- 총 수집 결과 (`total_clusters=N, total_jobs=N`)
- 처리된 리전 수 (`processed_regions=N`)
- 실행 시간 (`execution_time=N.NNs`)
- 성능 메트릭 (`throughput=N.N items/sec`)
- 평균 시간 (`avg_time_per_region=N.NNs`)

**개별 리전 로깅 (DEBUG 레벨)**:
- 리전별 성공/실패 상태
- 리전별 수집 결과 수

**에러 로깅 (WARNING/DEBUG 레벨)**:
- 타임아웃 발생 시 WARNING
- 개별 리전 실패 시 DEBUG

## 동적 리전 조회 로깅 패턴 (v2.0)

### Google Cloud Compute API를 통한 실시간 리전 조회

새로운 동적 리전 조회 시스템은 Google Cloud Compute API를 통해 실시간으로 사용 가능한 리전 목록을 조회하고, 실패 시 fallback 리전을 사용합니다:

```python
import logging
import googleapiclient.discovery

logger = logging.getLogger(__name__)

def _get_optimized_regions(self):
    """최적화된 리전 목록 반환 (캐시 및 동적 조회 포함)"""
    current_time = time.time()
    
    # 캐시 유효성 검사 (5분 TTL)
    if (self._regions_cache is not None and 
        current_time - self._cache_timestamp < self._cache_ttl):
        logger.debug(f"Using cached regions: {len(self._regions_cache)} regions")
        return self._regions_cache
    
    try:
        # 동적 리전 조회 시도
        regions = self._fetch_dataproc_regions()
        logger.info(f"Successfully fetched {len(regions)} Dataproc regions dynamically")
    except Exception as e:
        logger.warning(f"Failed to fetch dynamic regions, using core regions: {e}")
        # 핵심 리전으로 fallback (성능 최적화)
        regions = self._get_core_regions()
    
    # 캐시 업데이트
    self._regions_cache = regions
    self._cache_timestamp = current_time
    
    logger.debug(f"Using {len(regions)} regions for Dataproc scanning")
    return regions

def _fetch_dataproc_regions(self):
    """Google Cloud Compute API를 통한 동적 리전 조회"""
    if not hasattr(self, "client") or not self.client:
        raise ValueError("Client not initialized for dynamic region fetching")
    
    try:
        # Compute Engine API 클라이언트 생성
        compute_client = googleapiclient.discovery.build(
            "compute", "v1", credentials=self.credentials
        )
        request = compute_client.regions().list(project=self.project_id)
        response = request.execute()
        
        all_regions = []
        if "items" in response:
            for region in response["items"]:
                region_name = region.get("name", "")
                if region_name and region.get("status") == "UP":
                    all_regions.append(region_name)
        
        # 알려진 Dataproc 미지원 리전 제외
        excluded_regions = {"global"}
        supported_regions = [r for r in all_regions if r not in excluded_regions]
        
        if not supported_regions:
            raise Exception("No supported regions found")
        
        logger.info(f"Dynamic region query successful: {len(supported_regions)} regions available")
        return sorted(supported_regions)
        
    except Exception as e:
        logger.error(f"Failed to fetch regions from Compute API: {e}")
        raise

def _get_core_regions(self):
    """동적 조회 실패 시 사용할 핵심 리전 (성능 최적화)"""
    core_regions = [
        # 아시아 주요 리전
        "asia-east1", "asia-northeast1", "asia-northeast3", "asia-southeast1",
        # 유럽 주요 리전  
        "europe-west1", "europe-west4",
        # 미국 주요 리전
        "us-central1", "us-east1", "us-west1", "us-west2",
    ]
    logger.info(f"Using core regions for optimization: {len(core_regions)} regions")
    return core_regions
```

### 동적 리전 조회 로깅 가이드라인

**성공 시 (INFO 레벨)**:
- `"Successfully fetched N Dataproc regions dynamically"`
- `"Dynamic region query successful: N regions available"`

**실패 시 (WARNING 레벨)**:
- `"Failed to fetch dynamic regions, using core regions: {error}"`
- 자동으로 핵심 리전으로 fallback 수행

**캐시 사용 시 (DEBUG 레벨)**:
- `"Using cached regions: N regions"`
- 캐시 TTL(5분) 정보 포함

**성능 최적화 정보 (INFO 레벨)**:
- `"Using core regions for optimization: N regions"`
- 핵심 리전 사용 시 성능 최적화 의도 명시

## SpaceONE 플러그인 로깅 미들웨어

- SpaceONE Core 프레임워크의 표준 로깅 구조 활용
- 플러그인별 고유 식별자 포함
- 수집 성능 메트릭 자동 기록

```python
import logging
from spaceone.core.logger import set_logger

# SpaceONE 표준 로거 설정
set_logger('spaceone.inventory')

# 플러그인별 로거 생성
logger = logging.getLogger('spaceone.inventory.google_cloud')
```

## 상태 추적 로깅 시스템 (v2.0)

### 응답 상태별 자동 카운터 및 로깅

새로운 상태 추적 시스템이 도입되어 수집 결과를 체계적으로 모니터링할 수 있습니다. 이 시스템은 글로벌 카운터를 통해 SUCCESS, FAILURE, TIMEOUT, UNKNOWN 상태를 자동으로 추적하고, 각 상태에 따라 적절한 로깅을 수행합니다:

```python
from spaceone.inventory.libs.schema.base import (
    BaseResponse, 
    log_state_summary, 
    reset_state_counters,
    get_state_counters
)

# 수집 시작 시 카운터 초기화
reset_state_counters()

# 성공 응답 생성 (자동 로깅)
success_response = BaseResponse.create_with_logging(
    state="SUCCESS",
    resource_type="inventory.CloudService",
    message="Cluster collection completed",
    resource=cluster_data
)

# 실패 응답 생성 (자동 에러 로깅)
error_response = BaseResponse.create_with_logging(
    state="FAILURE", 
    resource_type="inventory.ErrorResource",
    message="Authentication failed",
)

# 타임아웃 응답 생성 (자동 경고 로깅)
timeout_response = BaseResponse.create_with_logging(
    state="TIMEOUT",
    resource_type="inventory.CloudService", 
    message="API call timeout after 90 seconds"
)

# 수집 완료 시 요약 정보 로깅
log_state_summary()
# 출력 예시: "📊 Response State Summary: Total=150, SUCCESS=140 (93.3%), FAILURE=8, TIMEOUT=2, UNKNOWN=0"
```

### 상태별 로깅 동작

| 상태 | 로깅 레벨 | 자동 동작 | 예시 |
|------|----------|----------|-----|
| **SUCCESS** | 없음 | 카운터만 증가 | 정상 처리 (로그 스팸 방지) |
| **FAILURE** | ERROR | 에러 로그 기록 | `"Response state: FAILURE, resource_type: inventory.CloudService, message: API authentication failed"` |
| **TIMEOUT** | WARNING | 경고 로그 기록 | `"Response state: TIMEOUT, resource_type: inventory.CloudService, message: Request timeout after 90s"` |
| **UNKNOWN** | WARNING | 경고 로그 기록 | 알 수 없는 상태 감지 |

### 에러 응답 자동 로깅

```python
from spaceone.inventory.libs.schema.cloud_service import ErrorResourceResponse

# 에러 응답 생성 시 자동 로깅
error_response = ErrorResourceResponse.create_with_logging(
    error_message="Connection refused to Dataproc API",
    error_code="ConnectionError", 
    resource_type="inventory.ErrorResource",
    additional_data={
        "cloud_service_group": "Dataproc",
        "cloud_service_type": "Cluster"
    }
)
# 자동 로그: "Response state: FAILURE, resource_type: inventory.ErrorResource, error_code: ConnectionError, message: Connection refused to Dataproc API"
```

## 성능 최적화

### 조건부 로깅

```python
# ❌ 항상 문자열 생성
logger.debug(f"Processing cluster data: {expensive_cluster_serialization()}")

# ✅ 로그 레벨 체크 후 처리
if logger.isEnabledFor(logging.DEBUG):
    logger.debug(f"Processing cluster data: {expensive_cluster_serialization()}")
```

### Google Cloud API 로깅 최적화

```python
# API 응답 크기가 클 경우 요약만 로깅
logger.info(f"Received {len(clusters)} clusters (total size: {sys.getsizeof(clusters)} bytes)")

# 대신 전체 응답 로깅 피함
# logger.debug(f"Full API response: {clusters}")  # ❌ 너무 큰 데이터
```

## 로그 보안

### Google Cloud 특화 민감 데이터 로깅 금지

**절대 로깅하면 안 되는 것:**

- Service Account 키 파일 내용
- 액세스 토큰 및 인증 헤더
- 인스턴스 내부 IP 주소
- 보안 그룹 및 방화벽 규칙 세부사항
- 프로젝트 번호 및 내부 식별자

### 로그 마스킹 예시

```python
def mask_sensitive_data(message: str) -> str:
    """민감한 데이터를 마스킹하여 로그에 안전하게 기록"""
    import re
    
    # 이메일 마스킹
    message = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '***@***.***', message)
    
    # IP 주소 마스킹 (내부 IP만)
    message = re.sub(r'10\.\d+\.\d+\.\d+', '10.***.***.***', message)
    message = re.sub(r'192\.168\.\d+\.\d+', '192.168.***.***', message)
    
    return message

# 사용 예시
logger.info(mask_sensitive_data(f"Connected to instance {instance_info}"))
```