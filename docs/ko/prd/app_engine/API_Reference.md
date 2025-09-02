# App Engine API 참조 가이드

## 개요

이 문서는 Google Cloud App Engine Admin API를 사용하여 리소스를 수집하는 방법과 API 엔드포인트에 대한 상세한 정보를 제공합니다.

## API 엔드포인트

### 1. Application API

#### `GET /v1/apps/{appsId}`
애플리케이션 정보를 조회합니다.

**요청 파라미터:**
- `appsId` (string, required): 애플리케이션 ID

**응답 예시:**
```json
{
  "id": "my-app",
  "name": "my-app",
  "authDomain": "my-app.appspot.com",
  "locationId": "us-central",
  "codeBucket": "staging.my-app.appspot.com",
  "defaultCookieExpiration": "86400s",
  "servingStatus": "SERVING",
  "defaultHostname": "my-app.appspot.com",
  "defaultBucket": "my-app.appspot.com",
  "serviceAccount": "my-app@appspot.gserviceaccount.com",
  "createTime": "2023-01-01T00:00:00Z",
  "updateTime": "2023-01-01T00:00:00Z"
}
```

### 2. Service API

#### `GET /v1/apps/{appsId}/services`
애플리케이션의 서비스 목록을 조회합니다.

**요청 파라미터:**
- `appsId` (string, required): 애플리케이션 ID
- `pageSize` (integer, optional): 페이지 크기 (기본값: 100)
- `pageToken` (string, optional): 페이지 토큰

**응답 예시:**
```json
{
  "services": [
    {
      "id": "default",
      "name": "default",
      "split": {
        "allocations": {
          "v1": 1.0
        }
      }
    }
  ],
  "nextPageToken": "next-page-token"
}
```

### 3. Version API

#### `GET /v1/apps/{appsId}/services/{servicesId}/versions`
서비스의 버전 목록을 조회합니다.

**요청 파라미터:**
- `appsId` (string, required): 애플리케이션 ID
- `servicesId` (string, required): 서비스 ID
- `pageSize` (integer, optional): 페이지 크기
- `pageToken` (string, optional): 페이지 토큰

**응답 예시:**
```json
{
  "versions": [
    {
      "id": "v1",
      "name": "v1",
      "runtime": "python39",
      "threadsafe": true,
      "instanceClass": "F1",
      "automaticScaling": {
        "minIdleInstances": 0,
        "maxIdleInstances": 1,
        "minPendingLatency": "30ms",
        "maxPendingLatency": "automatic"
      },
      "basicScaling": null,
      "manualScaling": null,
      "createTime": "2023-01-01T00:00:00Z",
      "diskUsageBytes": "0",
      "servingStatus": "SERVING"
    }
  ]
}
```

### 4. Instance API

#### `GET /v1/apps/{appsId}/services/{servicesId}/versions/{versionsId}/instances`
버전의 인스턴스 목록을 조회합니다.

**요청 파라미터:**
- `appsId` (string, required): 애플리케이션 ID
- `servicesId` (string, required): 서비스 ID
- `versionsId` (string, required): 버전 ID
- `pageSize` (integer, optional): 페이지 크기
- `pageToken` (string, optional): 페이지 토큰

**응답 예시:**
```json
{
  "instances": [
    {
      "id": "aef-default-v1-20230101t000000",
      "name": "aef-default-v1-20230101t000000",
      "appEngineRelease": "1.9.76",
      "availability": "DYNAMIC",
      "vmName": "aef-default-v1-20230101t000000",
      "vmZoneName": "us-central1-a",
      "vmStatus": "RUNNING",
      "startTime": "2023-01-01T00:00:00Z",
      "requests": 100,
      "errors": 0,
      "qps": 10.5,
      "averageLatency": 50
    }
  ]
}
```

## 리소스 모델

### Application 리소스
```python
@dataclass
class AppEngineApplication:
    id: str
    name: str
    auth_domain: str
    location_id: str
    code_bucket: str
    default_cookie_expiration: str
    serving_status: str
    default_hostname: str
    default_bucket: str
    service_account: str
    create_time: str
    update_time: str
```

### Service 리소스
```python
@dataclass
class AppEngineService:
    id: str
    name: str
    split: dict
    app_id: str
```

### Version 리소스
```python
@dataclass
class AppEngineVersion:
    id: str
    name: str
    runtime: str
    threadsafe: bool
    instance_class: str
    automatic_scaling: dict
    basic_scaling: dict
    manual_scaling: dict
    create_time: str
    disk_usage_bytes: str
    serving_status: str
    service_id: str
    app_id: str
```

### Instance 리소스
```python
@dataclass
class AppEngineInstance:
    id: str
    name: str
    app_engine_release: str
    availability: str
    vm_name: str
    vm_zone_name: str
    vm_status: str
    start_time: str
    requests: int
    errors: int
    qps: float
    average_latency: int
    version_id: str
    service_id: str
    app_id: str
```

## 에러 코드 및 처리

### HTTP 상태 코드
- **200**: 성공
- **400**: 잘못된 요청
- **401**: 인증 실패
- **403**: 권한 없음
- **404**: 리소스 없음
- **429**: 할당량 초과
- **500**: 내부 서버 오류

### 에러 응답 형식
```json
{
  "error": {
    "code": 403,
    "message": "App Engine Admin API has not been used in project my-project",
    "status": "PERMISSION_DENIED",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.Help",
        "links": [
          {
            "description": "Google developers console API activation",
            "url": "https://console.developers.google.com/apis/api/appengine.googleapis.com/overview?project=my-project"
          }
        ]
      }
    ]
  }
}
```

## 권한 및 인증

### 필요한 IAM 역할
```json
{
  "role": "roles/appengine.admin",
  "permissions": [
    "appengine.applications.get",
    "appengine.services.list",
    "appengine.versions.list",
    "appengine.instances.list"
  ]
}
```

### 최소 권한 설정
```json
{
  "role": "roles/appengine.viewer",
  "permissions": [
    "appengine.applications.get",
    "appengine.services.list",
    "appengine.versions.list",
    "appengine.instances.list"
  ]
}
```

## 할당량 및 제한

### API 할당량
- **읽기 요청**: 초당 1000개
- **페이지 크기**: 최대 1000개
- **동시 요청**: 최대 100개

### 할당량 초과 처리
```python
def handle_quota_exceeded(self, retry_after: int = 60):
    """할당량 초과 시 처리"""
    self.logger.warning(f"API 할당량 초과. {retry_after}초 후 재시도")
    time.sleep(retry_after)
```

## 성능 최적화

### 1. 배치 처리
```python
def collect_all_resources_batch(self, batch_size: int = 100):
    """배치 단위로 모든 리소스 수집"""
    resources = []
    
    # 애플리케이션 정보
    app_info = self._get_application_info()
    resources.append(app_info)
    
    # 서비스 배치 수집
    services = self._collect_services_batch(batch_size)
    resources.extend(services)
    
    # 버전 및 인스턴스 배치 수집
    for service in services:
        versions = self._collect_versions_batch(service["id"], batch_size)
        resources.extend(versions)
        
        for version in versions:
            instances = self._collect_instances_batch(
                service["id"], version["id"], batch_size
            )
            resources.extend(instances)
    
    return resources
```

### 2. 병렬 처리
```python
import concurrent.futures

def collect_services_parallel(self, max_workers: int = 5):
    """서비스 병렬 수집"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_service = {
            executor.submit(self._collect_service_details, service): service
            for service in self._get_service_list()
        }
        
        results = []
        for future in concurrent.futures.as_completed(future_to_service):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                self.logger.error(f"서비스 수집 실패: {e}")
        
        return results
```

### 3. 캐싱 전략
```python
from functools import lru_cache
from datetime import datetime, timedelta

class AppEngineCollector:
    def __init__(self):
        self._cache = {}
        self._cache_ttl = 300  # 5분
    
    def _get_cached_data(self, key: str):
        """캐시된 데이터 조회"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self._cache_ttl):
                return data
            else:
                del self._cache[key]
        return None
    
    def _set_cached_data(self, key: str, data):
        """데이터 캐싱"""
        self._cache[key] = (data, datetime.now())
    
    @lru_cache(maxsize=128)
    def get_application_info(self):
        """애플리케이션 정보 캐싱"""
        cache_key = f"app_info_{self.project_id}"
        cached_data = self._get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        data = self._fetch_application_info()
        self._set_cached_data(cache_key, data)
        return data
```

## 모니터링 및 로깅

### 1. 성능 메트릭 수집
```python
def collect_performance_metrics(self):
    """성능 메트릭 수집"""
    metrics = {
        "collection_start_time": datetime.now().isoformat(),
        "total_resources": 0,
        "api_calls": 0,
        "errors": 0,
        "cache_hits": 0,
        "cache_misses": 0
    }
    
    start_time = time.time()
    
    try:
        resources = self.collect_all_resources()
        metrics["total_resources"] = len(resources)
        metrics["collection_duration"] = time.time() - start_time
        metrics["status"] = "success"
    except Exception as e:
        metrics["status"] = "error"
        metrics["error_message"] = str(e)
        metrics["collection_duration"] = time.time() - start_time
    
    return metrics
```

### 2. 로그 레벨 설정
```python
import logging

def setup_logging(self, level: str = "INFO"):
    """로깅 설정"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    self.logger = logging.getLogger("app_engine_collector")
    
    # 파일 핸들러 추가
    file_handler = logging.FileHandler("app_engine_collection.log")
    file_handler.setLevel(logging.DEBUG)
    
    # 콘솔 핸들러 추가
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    self.logger.addHandler(file_handler)
    self.logger.addHandler(console_handler)
```

## 테스트 및 검증

### 1. API 응답 검증
```python
def validate_api_response(self, response: dict, resource_type: str):
    """API 응답 검증"""
    required_fields = self._get_required_fields(resource_type)
    
    for field in required_fields:
        if field not in response:
            raise ValueError(f"필수 필드 누락: {field}")
    
    return True

def _get_required_fields(self, resource_type: str) -> List[str]:
    """리소스 타입별 필수 필드"""
    field_mapping = {
        "application": ["id", "name", "serving_status"],
        "service": ["id", "name"],
        "version": ["id", "name", "runtime", "serving_status"],
        "instance": ["id", "name", "vm_status"]
    }
    
    return field_mapping.get(resource_type, [])
```

### 2. 데이터 무결성 검사
```python
def validate_data_integrity(self, resources: List[dict]):
    """데이터 무결성 검사"""
    errors = []
    
    for resource in resources:
        # 필수 필드 검사
        if "id" not in resource:
            errors.append(f"ID 필드 누락: {resource}")
        
        # 데이터 타입 검사
        if "metadata" in resource:
            metadata = resource["metadata"]
            if not isinstance(metadata, dict):
                errors.append(f"메타데이터 타입 오류: {resource}")
        
        # 관계 검사
        if resource.get("resource_type") == "app_engine_instance":
            if "version_id" not in resource:
                errors.append(f"버전 ID 누락: {resource}")
    
    if errors:
        raise ValueError(f"데이터 무결성 검사 실패: {errors}")
    
    return True
```

## 배포 및 운영

### 1. 환경별 설정
```yaml
# config/development.yml
app_engine:
  api_version: "v1"
  timeout: 30
  batch_size: 50
  enable_caching: true
  log_level: "DEBUG"
  max_retries: 3

# config/production.yml
app_engine:
  api_version: "v1"
  timeout: 60
  batch_size: 100
  enable_caching: true
  log_level: "INFO"
  max_retries: 5
  enable_health_check: true
```

### 2. 헬스 체크 엔드포인트
```python
def health_check(self) -> dict:
    """헬스 체크"""
    health_status = {
        "service": "app_engine_collector",
        "timestamp": datetime.now().isoformat(),
        "status": "unknown"
    }
    
    try:
        # API 연결 테스트
        self.client.apps().get(appsId=self.project_id).execute()
        health_status["status"] = "healthy"
        health_status["api_status"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["api_status"] = "disconnected"
        health_status["error"] = str(e)
    
    return health_status
```

## 문제 해결 가이드

### 1. 일반적인 문제들

#### API 활성화 오류
```
Error 403: App Engine Admin API has not been used in project
```
**해결 방법:**
1. Google Cloud Console에서 App Engine Admin API 활성화
2. IAM 권한 확인 및 수정
3. 프로젝트 ID 확인

#### 권한 오류
```
Error 403: The caller does not have permission
```
**해결 방법:**
1. Service Account 권한 확인
2. IAM 역할 할당 확인
3. 프로젝트 수준 권한 확인

#### 리소스 없음
```
Error 404: Requested entity was not found
```
**해결 방법:**
1. 프로젝트 ID 확인
2. App Engine 애플리케이션 존재 여부 확인
3. 리전 설정 확인

### 2. 디버깅 도구

#### 로그 분석
```bash
# 로그 파일에서 오류 검색
grep "ERROR" app_engine_collection.log

# 특정 시간대 로그 검색
grep "2023-01-01" app_engine_collection.log

# API 호출 로그 검색
grep "API call" app_engine_collection.log
```

#### API 테스트
```bash
# curl을 사용한 API 테스트
curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://appengine.googleapis.com/v1/apps/PROJECT_ID"
```

## 참고 자료

- [App Engine Admin API 문서](https://cloud.google.com/appengine/docs/admin-api)
- [App Engine REST API 참조](https://cloud.google.com/appengine/docs/admin-api/reference/rest)
- [IAM 권한 가이드](https://cloud.google.com/iam/docs/understanding-roles)
- [API 할당량 관리](https://cloud.google.com/apis/docs/quotas)
- [App Engine 모범 사례](https://cloud.google.com/appengine/docs/standard/python/best-practices)
