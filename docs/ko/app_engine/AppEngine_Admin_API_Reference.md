# SpaceONE Google Cloud App Engine Collector 구현 가이드

## 개요

이 문서는 SpaceONE Google Cloud Inventory Collector 플러그인에서 구현된 App Engine 관련 기능을 설명합니다. 현재 플러그인은 Google Cloud App Engine Admin API v1을 사용하여 App Engine 리소스를 수집합니다.

**서비스**: `appengine.googleapis.com`
**API 버전**: `v1`

## 구현된 Connector 클래스

### 1. AppEngineApplicationV1Connector

애플리케이션 정보를 조회하는 Connector입니다.

**위치**: `src/spaceone/inventory/connector/app_engine/application_v1.py`

**주요 메서드**:
- `get_application()`: App Engine 애플리케이션 정보 조회
- `list_services()`: 서비스 목록 조회
- `get_service()`: 특정 서비스 정보 조회
- `list_versions()`: 버전 목록 조회

**API 엔드포인트**:
```python
# 애플리케이션 조회
GET /v1/apps/{appsId}

# 서비스 목록 조회
GET /v1/apps/{appsId}/services

# 특정 서비스 조회
GET /v1/apps/{appsId}/services/{servicesId}

# 버전 목록 조회
GET /v1/apps/{appsId}/services/{servicesId}/versions
```

### 2. AppEngineServiceV1Connector

서비스 정보를 조회하는 Connector입니다.

**위치**: `src/spaceone/inventory/connector/app_engine/service_v1.py`

**주요 메서드**:
- `list_services()`: 서비스 목록 조회
- `get_service()`: 특정 서비스 정보 조회
- `list_versions()`: 버전 목록 조회

### 3. AppEngineVersionV1Connector

버전 정보를 조회하는 Connector입니다.

**위치**: `src/spaceone/inventory/connector/app_engine/version_v1.py`

**주요 메서드**:
- `list_versions()`: 버전 목록 조회
- `get_version()`: 특정 버전 정보 조회
- `list_instances()`: 인스턴스 목록 조회

**API 엔드포인트**:
```python
# 버전 목록 조회
GET /v1/apps/{appsId}/services/{servicesId}/versions

# 특정 버전 조회
GET /v1/apps/{appsId}/services/{servicesId}/versions/{versionsId}

# 인스턴스 목록 조회
GET /v1/apps/{appsId}/services/{servicesId}/versions/{versionsId}/instances
```

### 4. AppEngineInstanceV1Connector

인스턴스 정보를 조회하는 Connector입니다.

**위치**: `src/spaceone/inventory/connector/app_engine/instance_v1.py`

**주요 메서드**:
- `list_instances()`: 인스턴스 목록 조회
- `get_instance()`: 특정 인스턴스 정보 조회
- `list_all_instances()`: 모든 인스턴스 조회

**API 엔드포인트**:
```python
# 인스턴스 목록 조회
GET /v1/apps/{appsId}/services/{servicesId}/versions/{versionsId}/instances

# 특정 인스턴스 조회
GET /v1/apps/{appsId}/services/{servicesId}/versions/{versionsId}/instances/{instancesId}
```

## 구현된 Manager 클래스

### 1. AppEngineApplicationV1Manager

애플리케이션 리소스를 관리하는 Manager입니다.

**위치**: `src/spaceone/inventory/manager/app_engine/application_v1_manager.py`

**주요 기능**:
- 애플리케이션 정보 수집
- 메타데이터 생성
- 리소스 참조 정보 생성

### 2. AppEngineServiceV1Manager

서비스 리소스를 관리하는 Manager입니다.

**위치**: `src/spaceone/inventory/manager/app_engine/service_v1_manager.py`

**주요 기능**:
- 서비스 정보 수집
- 트래픽 분할 정보 처리
- 네트워크 설정 정보 처리

### 3. AppEngineVersionV1Manager

버전 리소스를 관리하는 Manager입니다.

**위치**: `src/spaceone/inventory/manager/app_engine/version_v1_manager.py`

**주요 기능**:
- 버전 정보 수집
- 런타임 정보 처리
- 스케일링 설정 정보 처리

### 4. AppEngineInstanceV1Manager

인스턴스 리소스를 관리하는 Manager입니다.

**위치**: `src/spaceone/inventory/manager/app_engine/instance_v1_manager.py`

**주요 기능**:
- 인스턴스 정보 수집
- 상태 정보 처리
- 리소스 사용량 정보 처리

## 데이터 모델

### 1. AppEngineApplication

애플리케이션 데이터 모델입니다.

**위치**: `src/spaceone/inventory/model/app_engine/application/data.py`

**주요 필드**:
- `name`: 애플리케이션 이름
- `project_id`: 프로젝트 ID
- `location_id`: 위치 ID
- `serving_status`: 서빙 상태
- `default_hostname`: 기본 호스트명
- `code_bucket`: 코드 버킷
- `gcr_domain`: GCR 도메인
- `feature_settings`: 기능 설정
- `iap`: IAP 설정
- `dispatch_rules`: 디스패치 규칙

### 2. AppEngineService

서비스 데이터 모델입니다.

**위치**: `src/spaceone/inventory/model/app_engine/service/data.py`

**주요 필드**:
- `name`: 서비스 이름
- `project_id`: 프로젝트 ID
- `service_id`: 서비스 ID
- `serving_status`: 서빙 상태
- `split`: 트래픽 분할 설정
- `network`: 네트워크 설정

### 3. AppEngineVersion

버전 데이터 모델입니다.

**위치**: `src/spaceone/inventory/model/app_engine/version/data.py`

**주요 필드**:
- `name`: 버전 이름
- `project_id`: 프로젝트 ID
- `service_id`: 서비스 ID
- `version_id`: 버전 ID
- `runtime`: 런타임 정보
- `serving_status`: 서빙 상태
- `scaling`: 스케일링 설정
- `deployment`: 배포 정보

### 4. AppEngineInstance

인스턴스 데이터 모델입니다.

**위치**: `src/spaceone/inventory/model/app_engine/instance/data.py`

**주요 필드**:
- `name`: 인스턴스 이름
- `project_id`: 프로젝트 ID
- `service_id`: 서비스 ID
- `version_id`: 버전 ID
- `instance_id`: 인스턴스 ID
- `status`: 상태
- `vm_status`: VM 상태
- `vm_debug_enabled`: VM 디버그 활성화 여부

## 수집 가능한 리소스

### 1. App Engine Application
- 애플리케이션 기본 정보
- 위치, 서빙 상태
- 기본 호스트명, 코드 버킷
- 기능 설정, IAP 설정
- 디스패치 규칙

### 2. App Engine Services
- 서비스 정보
- 트래픽 분할 설정
- 네트워크 설정
- 서빙 상태

### 3. App Engine Versions
- 버전 정보
- 런타임 설정
- 스케일링 설정
- 배포 정보
- 환경 변수

### 4. App Engine Instances
- 인스턴스 정보
- 상태 정보
- VM 상태
- 디버그 설정

## 인증 및 권한

### 필요한 권한
```json
{
  "https://www.googleapis.com/auth/appengine.admin": "View and manage your applications deployed on Google App Engine"
}
```

### 인증 설정
```python
credentials = google.oauth2.service_account.Credentials.from_service_account_info(secret_data)
client = googleapiclient.discovery.build("appengine", "v1", credentials=credentials)
```

## 사용 예시

### 애플리케이션 정보 조회
```python
connector = AppEngineApplicationV1Connector(secret_data=secret_data)
application = connector.get_application()
```

### 서비스 목록 조회
```python
connector = AppEngineServiceV1Connector(secret_data=secret_data)
services = connector.list_services()
```

### 버전 목록 조회
```python
connector = AppEngineVersionV1Connector(secret_data=secret_data)
versions = connector.list_versions(service_id="default")
```

### 인스턴스 목록 조회
```python
connector = AppEngineInstanceV1Connector(secret_data=secret_data)
instances = connector.list_instances(service_id="default", version_id="v1")
```

## 페이지네이션 처리

모든 목록 조회 메서드는 자동 페이지네이션을 지원합니다:

```python
def list_services(self, **query):
    service_list = []
    query.update({"appsId": self.project_id})
    
    try:
        request = self.client.apps().services().list(**query)
        while request is not None:
            response = request.execute()
            if "services" in response:
                service_list.extend(response.get("services", []))
            
            # 페이지네이션 처리
            try:
                request = self.client.apps().services().list_next(
                    previous_request=request, previous_response=response
                )
            except AttributeError:
                break
    except Exception as e:
        _LOGGER.error(f"Failed to list App Engine services (v1): {e}")
        
    return service_list
```

## 에러 처리

모든 Connector는 적절한 에러 처리를 포함합니다:

```python
try:
    request = self.client.apps().get(appsId=self.project_id)
    return request.execute()
except Exception as e:
    _LOGGER.error(f"Failed to get App Engine application (v1): {e}")
    return None
```

## 참고 자료

- [Google Cloud App Engine Admin API v1](https://cloud.google.com/appengine/docs/admin-api/reference/rest/v1)
- [SpaceONE Inventory Collector 가이드](https://spaceone.io/docs/guides/inventory-collector/)
- [Google Cloud 클라이언트 라이브러리](https://cloud.google.com/apis/docs/cloud-client-libraries)

---

*이 문서는 SpaceONE Google Cloud Inventory Collector 플러그인의 실제 구현 내용을 기반으로 작성되었습니다.*
