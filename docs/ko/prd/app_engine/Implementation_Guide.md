# App Engine 구현 가이드

## 개요

이 문서는 SpaceONE Google Cloud Inventory Collector에서 App Engine 리소스를 수집하는 구현 방법을 단계별로 설명합니다.

## 구현 단계

### 1. 프로젝트 구조 설정

```
src/spaceone/inventory/
├── connector/
│   └── app_engine/
│       ├── __init__.py
│       ├── application_v1.py
│       ├── service_v1.py
│       ├── version_v1.py
│       └── instance_v1.py
├── manager/
│   └── app_engine/
│       ├── __init__.py
│       ├── application_v1_manager.py
│       ├── service_v1_manager.py
│       ├── version_v1_manager.py
│       └── instance_v1_manager.py
└── model/
    └── app_engine/
        ├── __init__.py
        ├── application.py
        ├── service.py
        ├── version.py
        └── instance.py
```

### 2. Connector 구현

#### Application Connector
```python
# src/spaceone/inventory/connector/app_engine/application_v1.py

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from spaceone.inventory.connector.base import BaseConnector

class AppEngineApplicationV1Connector(BaseConnector):
    def __init__(self, credentials, project_id):
        self.credentials = credentials
        self.project_id = project_id
        self.client = build('appengine', 'v1', credentials=credentials)
    
    def get_application(self):
        """애플리케이션 정보 조회"""
        try:
            request = self.client.apps().get(appsId=self.project_id)
            response = request.execute()
            return response
        except HttpError as e:
            self._handle_error(e)
    
    def _handle_error(self, error):
        """에러 처리"""
        if error.resp.status == 403:
            raise PermissionError(f"App Engine API 접근 권한이 없습니다: {error}")
        elif error.resp.status == 404:
            raise ResourceNotFoundError(f"App Engine 애플리케이션을 찾을 수 없습니다: {error}")
        else:
            raise AppEngineError(f"App Engine API 오류: {error}")
```

#### Service Connector
```python
# src/spaceone/inventory/connector/app_engine/service_v1.py

class AppEngineServiceV1Connector(BaseConnector):
    def __init__(self, credentials, project_id):
        self.credentials = credentials
        self.project_id = project_id
        self.client = build('appengine', 'v1', credentials=credentials)
    
    def list_services(self, page_size=100):
        """서비스 목록 조회"""
        services = []
        page_token = None
        
        while True:
            try:
                request = self.client.apps().services().list(
                    appsId=self.project_id,
                    pageSize=page_size,
                    pageToken=page_token
                )
                response = request.execute()
                
                services.extend(response.get('services', []))
                page_token = response.get('nextPageToken')
                
                if not page_token:
                    break
                    
            except HttpError as e:
                self._handle_error(e)
        
        return services
```

### 3. Manager 구현

#### Application Manager
```python
# src/spaceone/inventory/manager/app_engine/application_v1_manager.py

from spaceone.inventory.manager.base import BaseManager
from spaceone.inventory.connector.app_engine.application_v1 import AppEngineApplicationV1Connector

class AppEngineApplicationV1Manager(BaseManager):
    def __init__(self, credentials, project_id):
        self.connector = AppEngineApplicationV1Connector(credentials, project_id)
    
    def collect(self):
        """애플리케이션 정보 수집"""
        try:
            app_info = self.connector.get_application()
            
            # 메타데이터 추가
            app_info['resource_type'] = 'app_engine_application'
            app_info['project_id'] = self.project_id
            app_info['collection_timestamp'] = datetime.utcnow().isoformat()
            
            return [app_info]
            
        except Exception as e:
            self.logger.error(f"애플리케이션 수집 실패: {e}")
            raise
```

#### Service Manager
```python
# src/spaceone/inventory/manager/app_engine/service_v1_manager.py

class AppEngineServiceV1Manager(BaseManager):
    def __init__(self, credentials, project_id):
        self.connector = AppEngineServiceV1Connector(credentials, project_id)
    
    def collect(self):
        """서비스 정보 수집"""
        try:
            services = self.connector.list_services()
            
            # 메타데이터 추가
            for service in services:
                service['resource_type'] = 'app_engine_service'
                service['project_id'] = self.project_id
                service['collection_timestamp'] = datetime.utcnow().isoformat()
            
            return services
            
        except Exception as e:
            self.logger.error(f"서비스 수집 실패: {e}")
            raise
```

### 4. Model 정의

#### Application Model
```python
# src/spaceone/inventory/model/app_engine/application.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class AppEngineApplication:
    id: str
    name: str
    auth_domain: str
    location_id: str
    code_bucket: str
    serving_status: str
    default_hostname: str
    default_bucket: str
    service_account: str
    create_time: str
    update_time: str
    project_id: str
    resource_type: str = "app_engine_application"
    collection_timestamp: Optional[str] = None
```

### 5. 통합 및 등록

#### Manager 등록
```python
# src/spaceone/inventory/manager/__init__.py

from .app_engine.application_v1_manager import AppEngineApplicationV1Manager
from .app_engine.service_v1_manager import AppEngineServiceV1Manager

MANAGER_REGISTRY = {
    'app_engine_application_v1': AppEngineApplicationV1Manager,
    'app_engine_service_v1': AppEngineServiceV1Manager,
    # ... 기타 매니저들
}
```

#### Service에서 사용
```python
# src/spaceone/inventory/service/collector_service.py

class CollectorService:
    def collect_app_engine_resources(self, credentials, project_id):
        """App Engine 리소스 수집"""
        resources = []
        
        # 애플리케이션 수집
        app_manager = AppEngineApplicationV1Manager(credentials, project_id)
        app_resources = app_manager.collect()
        resources.extend(app_resources)
        
        # 서비스 수집
        service_manager = AppEngineServiceV1Manager(credentials, project_id)
        service_resources = service_manager.collect()
        resources.extend(service_resources)
        
        return resources
```

## 설정 및 환경 변수

### 1. 환경 변수 설정
```bash
# .env 파일
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
APP_ENGINE_API_VERSION=v1
APP_ENGINE_TIMEOUT=60
APP_ENGINE_BATCH_SIZE=100
```

### 2. 설정 파일
```yaml
# config/app_engine.yml
app_engine:
  api_version: "v1"
  timeout: 60
  batch_size: 100
  enable_caching: true
  max_retries: 3
  retry_delay: 1000
```

## 테스트 구현

### 1. 단위 테스트
```python
# test/test_app_engine_manager.py

import pytest
from unittest.mock import Mock, patch
from spaceone.inventory.manager.app_engine.application_v1_manager import AppEngineApplicationV1Manager

class TestAppEngineApplicationManager:
    def setup_method(self):
        self.credentials = Mock()
        self.project_id = "test-project"
        self.manager = AppEngineApplicationV1Manager(self.credentials, self.project_id)
    
    def test_collect_application_success(self):
        """애플리케이션 수집 성공 테스트"""
        # Given
        mock_app_info = {
            "id": "test-app",
            "name": "test-app",
            "servingStatus": "SERVING"
        }
        
        with patch.object(self.manager.connector, 'get_application', return_value=mock_app_info):
            # When
            result = self.manager.collect()
            
            # Then
            assert len(result) == 1
            assert result[0]["id"] == "test-app"
            assert result[0]["resource_type"] == "app_engine_application"
    
    def test_collect_application_error(self):
        """애플리케이션 수집 실패 테스트"""
        # Given
        with patch.object(self.manager.connector, 'get_application', side_effect=Exception("API Error")):
            # When & Then
            with pytest.raises(Exception):
                self.manager.collect()
```

### 2. 통합 테스트
```python
# test/integration/test_app_engine_integration.py

class TestAppEngineIntegration:
    def test_end_to_end_collection(self):
        """전체 수집 프로세스 테스트"""
        # Given
        credentials = self.get_test_credentials()
        project_id = "test-project"
        
        # When
        collector_service = CollectorService()
        resources = collector_service.collect_app_engine_resources(credentials, project_id)
        
        # Then
        assert len(resources) > 0
        assert all("resource_type" in resource for resource in resources)
        assert all("collection_timestamp" in resource for resource in resources)
```

## 성능 최적화

### 1. 배치 처리
```python
def collect_services_batch(self, batch_size=100):
    """서비스 배치 수집"""
    services = []
    page_token = None
    
    while True:
        response = self.connector.list_services_page(batch_size, page_token)
        services.extend(response.get('services', []))
        page_token = response.get('nextPageToken')
        
        if not page_token:
            break
    
    return services
```

### 2. 캐싱 구현
```python
from functools import lru_cache

class AppEngineManager(BaseManager):
    @lru_cache(maxsize=128)
    def get_cached_application_info(self):
        """애플리케이션 정보 캐싱"""
        return self.connector.get_application()
```

## 에러 처리 및 로깅

### 1. 에러 처리
```python
def handle_collection_error(self, error, resource_type):
    """수집 에러 처리"""
    error_info = {
        "resource_type": resource_type,
        "error": str(error),
        "timestamp": datetime.utcnow().isoformat(),
        "project_id": self.project_id
    }
    
    self.logger.error(f"리소스 수집 실패: {error_info}")
    
    # 에러 메트릭 업데이트
    self.update_error_metrics(resource_type, error)
    
    raise CollectionError(f"{resource_type} 수집 실패: {error}")
```

### 2. 로깅 설정
```python
import logging

def setup_logging(self):
    """로깅 설정"""
    logger = logging.getLogger("app_engine_collector")
    logger.setLevel(logging.INFO)
    
    # 파일 핸들러
    file_handler = logging.FileHandler("app_engine_collection.log")
    file_handler.setLevel(logging.DEBUG)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
```

## 배포 및 운영

### 1. Docker 설정
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/

CMD ["python", "-m", "spaceone.inventory.service.collector_service"]
```

### 2. 헬스 체크
```python
def health_check(self):
    """헬스 체크"""
    try:
        # 간단한 API 호출로 연결 상태 확인
        self.connector.get_application()
        return {"status": "healthy", "service": "app_engine_collector"}
    except Exception as e:
        return {"status": "unhealthy", "service": "app_engine_collector", "error": str(e)}
```

## 모니터링 및 메트릭

### 1. 성능 메트릭
```python
def collect_metrics(self):
    """성능 메트릭 수집"""
    metrics = {
        "collection_start_time": datetime.now().isoformat(),
        "total_resources": 0,
        "api_calls": 0,
        "errors": 0,
        "duration": 0
    }
    
    start_time = time.time()
    
    try:
        resources = self.collect_all_resources()
        metrics["total_resources"] = len(resources)
        metrics["duration"] = time.time() - start_time
        metrics["status"] = "success"
    except Exception as e:
        metrics["status"] = "error"
        metrics["error_message"] = str(e)
        metrics["duration"] = time.time() - start_time
    
    return metrics
```

## 문제 해결

### 1. 일반적인 문제들

#### 권한 오류
```
Error 403: App Engine Admin API has not been used in project
```
**해결 방법:**
1. Google Cloud Console에서 App Engine Admin API 활성화
2. IAM 권한 확인 및 수정
3. Service Account 키 파일 확인

#### 리소스 없음
```
Error 404: Requested entity was not found
```
**해결 방법:**
1. 프로젝트 ID 확인
2. App Engine 애플리케이션 존재 여부 확인
3. 리전 설정 확인

### 2. 디버깅 팁
- API 응답 로깅 활성화
- 네트워크 지연 시간 모니터링
- 메모리 사용량 추적
- API 호출 빈도 제한

## 참고 자료

- [App Engine Admin API 문서](https://cloud.google.com/appengine/docs/admin-api)
- [App Engine REST API 참조](https://cloud.google.com/appengine/docs/admin-api/reference/rest)
- [IAM 권한 가이드](https://cloud.google.com/iam/docs/understanding-roles)
- [API 할당량 관리](https://cloud.google.com/apis/docs/quotas)
