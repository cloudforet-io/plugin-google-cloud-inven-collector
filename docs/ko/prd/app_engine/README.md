# Google Cloud App Engine 도메인 가이드

## 개요

Google Cloud App Engine은 완전 관리형 서버리스 플랫폼으로, 웹 애플리케이션과 백엔드 서비스를 쉽게 배포하고 확장할 수 있게 해줍니다. 이 문서는 SpaceONE Google Cloud Inventory Collector에서 App Engine 리소스를 수집하는 방법과 관련 아키텍처를 설명합니다.

## 아키텍처

### 서비스 구조
```
App Engine
├── Application (애플리케이션)
├── Service (서비스)
│   ├── Version (버전)
│   │   ├── Instance (인스턴스)
│   │   └── Traffic Split (트래픽 분할)
│   └── Scaling (스케일링)
└── Configuration (설정)
```

### 계층별 리소스 수집

#### 1. Application Level
- **리소스**: `appengine.googleapis.com/Application`
- **수집 정보**: 
  - 애플리케이션 ID 및 이름
  - 프로젝트 ID
  - 생성 시간 및 수정 시간
  - 기본 도메인
  - 기본 버킷
  - 서비스 계정

#### 2. Service Level
- **리소스**: `appengine.googleapis.com/Service`
- **수집 정보**:
  - 서비스 이름
  - 서비스 ID
  - 분할 정보
  - 스케일링 설정
  - 네트워크 설정

#### 3. Version Level
- **리소스**: `appengine.googleapis.com/Version`
- **수집 정보**:
  - 버전 ID
  - 런타임 환경 (Python, Node.js, Java, Go 등)
  - 인스턴 클래스
  - 자동 스케일링 설정
  - 수동 스케일링 설정
  - 환경 변수
  - 리소스 할당량

#### 4. Instance Level
- **리소스**: `appengine.googleapis.com/Instance`
- **수집 정보**:
  - 인스턴스 ID
  - 상태 (RUNNING, STOPPED, PENDING 등)
  - 가용성 영역
  - 시작 시간
  - 메모리 및 CPU 사용량
  - 요청 수

## API 버전 관리

### 지원 API 버전
- **v1**: 현재 안정 버전, 프로덕션 환경 권장
- **v1beta**: 베타 기능 테스트용, 하위 호환성 지원

### API 선택 기준
```python
# v1 API 우선 사용
if self.api_version == "v1":
    return self._get_v1_client()
else:
    return self._get_v1beta_client()
```

## 리소스 수집 프로세스

### 1. 초기화 단계
```python
def initialize(self, options: dict) -> None:
    """App Engine 수집기 초기화"""
    self.project_id = options.get("project_id")
    self.api_version = options.get("api_version", "v1")
    self.client = self._create_client()
```

### 2. 수집 단계
```python
def collect(self) -> List[dict]:
    """App Engine 리소스 수집"""
    resources = []
    
    # 1. 애플리케이션 정보 수집
    app_info = self._collect_application()
    resources.append(app_info)
    
    # 2. 서비스 목록 수집
    services = self._collect_services()
    resources.extend(services)
    
    # 3. 각 서비스의 버전 수집
    for service in services:
        versions = self._collect_versions(service["name"])
        resources.extend(versions)
        
        # 4. 각 버전의 인스턴스 수집
        for version in versions:
            instances = self._collect_instances(service["name"], version["id"])
            resources.extend(instances)
    
    return resources
```

### 3. 메타데이터 처리
```python
def _process_metadata(self, resource: dict) -> dict:
    """리소스 메타데이터 처리"""
    metadata = {
        "resource_type": "app_engine",
        "collection_timestamp": datetime.utcnow().isoformat(),
        "project_id": self.project_id,
        "api_version": self.api_version
    }
    
    resource["metadata"] = metadata
    return resource
```

## 권한 관리

### 필요한 IAM 권한
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

### 최소 권한 원칙
- **읽기 전용**: 수집 목적으로는 읽기 권한만 필요
- **범위 제한**: 특정 애플리케이션에 대한 권한만 부여
- **감사 로그**: 모든 API 호출에 대한 감사 로그 활성화

## 성능 최적화

### 1. 배치 처리
```python
def _collect_services_batch(self, batch_size: int = 100) -> List[dict]:
    """서비스 배치 수집"""
    services = []
    page_token = None
    
    while True:
        response = self.client.apps().services().list(
            appsId=self.project_id,
            pageSize=batch_size,
            pageToken=page_token
        ).execute()
        
        services.extend(response.get("services", []))
        page_token = response.get("nextPageToken")
        
        if not page_token:
            break
    
    return services
```

### 2. 캐싱 전략
```python
@lru_cache(maxsize=128)
def _get_application_info(self) -> dict:
    """애플리케이션 정보 캐싱"""
    return self.client.apps().get(appsId=self.project_id).execute()
```

### 3. 타임아웃 관리
```python
def _create_client(self) -> Resource:
    """API 클라이언트 생성 (타임아웃 설정)"""
    return build(
        "appengine",
        self.api_version,
        credentials=self.credentials,
        cache_discovery=False,
        timeout=30
    )
```

## 에러 처리

### 1. API 오류 처리
```python
def _handle_api_error(self, error: HttpError) -> None:
    """API 오류 처리"""
    if error.resp.status == 403:
        raise PermissionError(f"App Engine API 접근 권한이 없습니다: {error}")
    elif error.resp.status == 404:
        raise ResourceNotFoundError(f"App Engine 리소스를 찾을 수 없습니다: {error}")
    else:
        raise AppEngineError(f"App Engine API 오류: {error}")
```

### 2. 재시도 로직
```python
@retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000)
def _api_call_with_retry(self, api_method, *args, **kwargs):
    """재시도 로직이 포함된 API 호출"""
    try:
        return api_method(*args, **kwargs).execute()
    except HttpError as e:
        if e.resp.status in [429, 500, 502, 503, 504]:
            raise  # 재시도 가능한 오류
        else:
            raise  # 재시도 불가능한 오류
```

## 모니터링 및 로깅

### 1. 성능 메트릭
```python
def _log_collection_metrics(self, start_time: float, resource_count: int):
    """수집 성능 메트릭 로깅"""
    duration = time.time() - start_time
    self.logger.info(
        f"App Engine 수집 완료: {resource_count}개 리소스, "
        f"소요시간: {duration:.2f}초"
    )
```

### 2. 상태 추적
```python
def _track_collection_status(self, status: str, details: str = None):
    """수집 상태 추적"""
    self.collection_status = {
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "details": details
    }
```

## 테스트 전략

### 1. 단위 테스트
```python
def test_collect_application(self):
    """애플리케이션 수집 테스트"""
    # Given
    mock_client = Mock()
    mock_client.apps().get().execute.return_value = {
        "id": "test-app",
        "name": "test-app"
    }
    
    # When
    result = self.collector._collect_application()
    
    # Then
    assert result["id"] == "test-app"
    assert result["name"] == "test-app"
```

### 2. 통합 테스트
```python
def test_end_to_end_collection(self):
    """전체 수집 프로세스 테스트"""
    # Given
    options = {"project_id": "test-project"}
    
    # When
    resources = self.collector.collect()
    
    # Then
    assert len(resources) > 0
    assert all("metadata" in resource for resource in resources)
```

## 배포 및 운영

### 1. 환경별 설정
```yaml
# development.yml
app_engine:
  api_version: "v1"
  timeout: 30
  batch_size: 50
  enable_caching: true

# production.yml
app_engine:
  api_version: "v1"
  timeout: 60
  batch_size: 100
  enable_caching: true
  enable_retry: true
  max_retries: 3
```

### 2. 헬스 체크
```python
def health_check(self) -> dict:
    """App Engine 수집기 헬스 체크"""
    try:
        # 간단한 API 호출로 연결 상태 확인
        self.client.apps().get(appsId=self.project_id).execute()
        return {"status": "healthy", "service": "app_engine"}
    except Exception as e:
        return {"status": "unhealthy", "service": "app_engine", "error": str(e)}
```

## 문제 해결

### 1. 일반적인 문제들

#### 권한 오류
```
Error 403: App Engine Admin API has not been used in project
```
**해결 방법**: 프로젝트에서 App Engine Admin API 활성화 및 적절한 IAM 권한 부여

#### 리소스 없음
```
Error 404: Requested entity was not found
```
**해결 방법**: 프로젝트 ID 확인 및 App Engine 애플리케이션 존재 여부 확인

#### API 할당량 초과
```
Error 429: Quota exceeded
```
**해결 방법**: API 할당량 증가 요청 또는 재시도 로직 구현

### 2. 디버깅 팁
- API 응답 로깅 활성화
- 네트워크 지연 시간 모니터링
- 메모리 사용량 추적
- API 호출 빈도 제한

## 참고 자료

- [App Engine Admin API 문서](https://cloud.google.com/appengine/docs/admin-api)
- [App Engine 리소스 모델](https://cloud.google.com/appengine/docs/admin-api/reference/rest)
- [IAM 권한 가이드](https://cloud.google.com/iam/docs/understanding-roles)
- [API 할당량 관리](https://cloud.google.com/apis/docs/quotas)
