# Google Cloud Build 리소스 수집기 요구사항 정의서 (플러그인 기반)

본 문서는 현재 `plugin-google-cloud-inven-collector` 플러그인에 구현된 Cloud Build 수집 기능의 요구사항을 명세한다. 수집된 데이터는 시스템의 인벤토리 정보로 활용되며, 단순 개수 수집 방식을 통해 대시보드에서 리소스 현황을 시각화하는 것을 목표로 한다.

✅ **현재 상태**: 단순 개수 수집 방식으로 다른 Google Cloud 도메인과 일관된 메트릭 체계를 구축하여 안정적이고 유지보수 가능한 모니터링 시스템을 제공한다.

---

## 📚 참고 문서

### Google Cloud Build 공식 문서

- **[Cloud Build 개요](https://cloud.google.com/build/docs/overview)**: Cloud Build 서비스의 전반적인 개념과 기능 설명
- **[Cloud Build API Reference](https://cloud.google.com/build/docs/api/reference/rest)**: REST API 상세 명세 및 리소스 구조
- **[Build 구성 파일 참조](https://cloud.google.com/build/docs/build-config-file-schema)**: cloudbuild.yaml 파일 스키마
- **[트리거 관리](https://cloud.google.com/build/docs/automating-builds/create-manage-triggers)**: 빌드 트리거 생성 및 관리 가이드
- **[워커풀 관리](https://cloud.google.com/build/docs/private-pools/private-pools-overview)**: 비공개 워커풀 구성 및 관리

### API 리소스 상세 문서

- **[Builds API](https://cloud.google.com/build/docs/api/reference/rest/v1/projects.builds)**: 빌드 리소스 API 명세
- **[Triggers API](https://cloud.google.com/build/docs/api/reference/rest/v1/projects.triggers)**: 트리거 리소스 API 명세
- **[WorkerPools API](https://cloud.google.com/build/docs/api/reference/rest/v1/projects.locations.workerPools)**: 워커풀 리소스 API 명세
- **[Connections API](https://cloud.google.com/build/docs/api/reference/rest/v2/projects.locations.connections)**: SCM 연결 API 명세 (v2)
- **[Repositories API](https://cloud.google.com/build/docs/api/reference/rest/v2/projects.locations.connections.repositories)**: 저장소 API 명세 (v2)

---

## 🎯 수집 대상 리소스

현재 플러그인의 커넥터(`cloud_build_v1.py`, `cloud_build_v2.py`)는 아래 리소스의 수집 기능을 제공한다.

### 2.1. Build (빌드 내역)

- **API (v1)**:
  - `projects.builds.list`: Global 리전의 빌드 내역을 조회한다.
  - `projects.locations.builds.list`: 특정 리전(regional)의 빌드 내역을 조회한다.
- **수집 목적**: 빌드 상태, 실행 시간, 사용 환경(머신 타입) 등의 데이터를 수집하여 빌드 현황을 파악한다.
- **리소스 구조**: [Build 리소스 스키마](https://cloud.google.com/build/docs/api/reference/rest/v1/projects.builds#Build)

### 2.2. Trigger (빌드 트리거)

- **API (v1)**:
  - `projects.triggers.list`: Global 리전의 트리거 목록을 조회한다.
  - `projects.locations.triggers.list`: 특정 리전의 트리거 목록을 조회한다.
- **수집 목적**: 자동화된 빌드의 구성 정보를 파악하고, 1세대(Gen 1) 방식으로 연동된 GitHub 저장소 정보를 간접적으로 수집한다.
- **리소스 구조**: [BuildTrigger 리소스 스키마](https://cloud.google.com/build/docs/api/reference/rest/v1/projects.triggers#BuildTrigger)

### 2.3. Worker Pool (워커풀)

- **API (v1)**:
  - `projects.locations.workerPools.list`: 특정 리전의 비공개 워커풀(Private Pool) 목록을 조회한다.
- **수집 목적**: 비공개 풀의 구성(머신 타입, 네트워크) 정보를 수집하여 빌드 환경을 파악한다.
- **리소스 구조**: [WorkerPool 리소스 스키마](https://cloud.google.com/build/docs/api/reference/rest/v1/projects.locations.workerPools#WorkerPool)

### 2.4. Location (리전 정보)

- **API (v2)**:
  - `projects.locations.list`: Cloud Build 서비스를 지원하는 전체 위치(리전) 목록을 조회한다.
- **수집 목적**: 다른 리소스들을 조회할 리전 목록을 동적으로 생성하는 데 사용된다.
- **리소스 구조**: [Location 리소스 스키마](https://cloud.google.com/build/docs/api/reference/rest/v2/projects.locations#Location)

### 2.5. SCM Connection & Repository (2세대 연동 정보)

- **API (v2)**:
  - `projects.locations.connections.list`: 특정 리전의 SCM 연결(Connection) 목록을 조회한다.
  - `projects.locations.connections.repositories.list`: 특정 SCM 연결을 통해 접근 가능한 저장소(Repository) 목록을 조회한다.
- **수집 목적**: 2세대(Gen 2) 방식으로 연동된 소스 저장소의 구성 정보를 파악한다.
- **리소스 구조**:
  - [Connection 리소스 스키마](https://cloud.google.com/build/docs/api/reference/rest/v2/projects.locations.connections#Connection)
  - [Repository 리소스 스키마](https://cloud.google.com/build/docs/api/reference/rest/v2/projects.locations.connections.repositories#Repository)

---

## 📊 핵심 메트릭 정의 (단순 개수 수집 방식)

### 3.1. 메트릭 수집 방식

다른 Google Cloud 도메인과의 일관성을 위해 Cloud Build도 **단순 개수 수집 방식**을 사용한다. 이는 대시보드에서 리소스의 전체적인 현황을 파악하고 관리하는 데 초점을 맞춘다.

### 3.2. 구현된 메트릭 목록

| 메트릭 파일                         | 메트릭 이름           | 방식              | 분석 가능 요소                                 |
| :---------------------------------- | :-------------------- | :---------------- | :--------------------------------------------- |
| `Build/build_count.yaml`            | Build Count           | `operator: count` | 상태별, 트리거별, 리전별, 저장소별 빌드 수     |
| `Build/build_count_by_status.yaml`  | Build Count by Status | `operator: count` | 빌드 상태별 대시보드 시각화 (성공/실패/진행중) |
| `Trigger/trigger_count.yaml`        | Trigger Count         | `operator: count` | 트리거 수 및 설정 현황                         |
| `Trigger/trigger_status.yaml`       | Active Trigger Count  | `operator: count` | 활성/비활성 트리거 수                          |
| `Connection/connection_count.yaml`  | Connection Count      | `operator: count` | SCM 연결 수 (2세대)                            |
| `Repository/repository_count.yaml`  | Repository Count      | `operator: count` | 연결된 저장소 수 (2세대)                       |
| `WorkerPool/worker_pool_count.yaml` | WorkerPool Count      | `operator: count` | 비공개 워커풀 수                               |

### 3.3. 메트릭 활용 방안

단순 개수 수집 방식으로도 다양한 대시보드 분석이 가능하다:

- **빌드 현황 모니터링**: 전체 빌드 수, 상태별 분포
- **트리거 관리**: 활성/비활성 트리거 현황
- **리소스 현황**: 워커풀, 연결, 저장소 수
- **리전별 분석**: 지역별 리소스 분포
- **프로젝트별 분석**: 프로젝트 간 비교 분석

**장점:**

- 다른 Google Cloud 도메인과 일관된 메트릭 방식
- 단순하고 안정적인 메트릭 수집
- 대시보드에서 직관적인 리소스 현황 파악

---

## 🏗️ 현재 구현 상세 분석

### 4.1. 수집 대상 리소스별 현재 구현 (Manager 및 Connector)

- **사용 라이브러리**: `google-api-python-client`를 기반으로 한 `GoogleCloudConnector`를 사용한다.
- **리소스 조회 방식**: `global` API와 `regional` API를 모두 호출하는 방식을 사용한다. 전체 리소스 수집을 위해서는 아래 두 단계를 모두 수행해야 한다.
  1. Global API 호출: `projects.builds.list`, `projects.triggers.list`를 각각 호출하여 `global` 리전의 리소스를 수집한다.
  2. Regional API 호출: `projects.locations.list` (v2)를 통해 전체 리전 목록을 가져온 후, 각 리전을 순회하며 `projects.locations.builds.list`, `projects.locations.triggers.list` 등을 호출하여 각 리전의 리소스를 수집한다.
- **페이지네이션 처리**: 각 커넥터 메소드 내부에 `while request is not None` 루프와 `list_next(request, response)`를 사용하여, 모든 페이지의 결과를 수집하도록 구현되어 있다.
- **SCM 연동 방식 처리**: 1세대와 2세대 저장소를 모두 수집할 수 있도록 v1과 v2 커넥터에 필요한 메소드가 각각 구현되어 있다.
  1. **1세대(Gen 1)**: `cloud_build_v1.py`의 `list_triggers` 또는 `list_location_triggers`를 통해 수집된 정보에서 `github` 필드를 분석한다.
  2. **2세대(Gen 2)**: `cloud_build_v2.py`의 `list_connections`와 `list_repositories`를 순차적으로 호출하여 수집한다.

#### Build (빌드 내역)

- **Manager**: `CloudBuildBuildManager`
- **Connector**: `CloudBuildV1Connector`
- **수집 방식**: Global API + Regional API 순차 호출
- **데이터 모델**: 충분한 필드 보유 (시간 정보, 상태, 트리거 ID 등)
- **메트릭 구현**: `build_count.yaml`, `build_count_by_status.yaml` (상태별 카운트)

#### Trigger (빌드 트리거)

- **Manager**: `CloudBuildTriggerManager`
- **Connector**: `CloudBuildV1Connector`
- **수집 방식**: Global API + Regional API 순차 호출
- **데이터 모델**: 트리거 설정 정보, 활성화 상태 등 보유
- **메트릭 구현**: `trigger_count.yaml`, `trigger_status.yaml`

#### Worker Pool (워커풀)

- **Manager**: `CloudBuildWorkerPoolManager`
- **Connector**: `CloudBuildV1Connector`
- **수집 방식**: Regional API만 호출 (Global 없음)
- **데이터 모델**: 워커풀 구성 정보
- **메트릭 구현**: `worker_pool_count.yaml`

#### Connection & Repository (2세대 연동)

- **Manager**: `CloudBuildConnectionManager`, `CloudBuildRepositoryManager`
- **Connector**: `CloudBuildV2Connector`
- **수집 방식**: 리전별 Connection 조회 → 각 Connection별 Repository 조회
- **데이터 모델**: SCM 연결 정보 및 저장소 목록
- **메트릭 구현**: `connection_count.yaml`, `repository_count.yaml`

### 4.2. 메트릭 구현 현황

#### 현재 상태

- **모든 메트릭**: 단순 개수 카운트 방식으로 일관되게 구현
- **데이터 수집**: 모든 필요 리소스 정보가 완전히 수집됨
- **대시보드 활용**: 다양한 그룹화 옵션으로 세분화된 분석 가능

#### 장점

- **일관성**: 다른 Google Cloud 도메인과 동일한 메트릭 방식
- **안정성**: 단순한 카운트 방식으로 오류 가능성 최소화
- **유지보수성**: 메트릭 정의가 단순하여 유지보수 용이

---

## 🚀 개선 권장사항

### 6.1. 수정 완료 사항

1. **모든 메트릭 검증 완료**
   - 7개 메트릭 모두 `operator: count` 방식 사용
   - 다른 Google Cloud 도메인과 일관된 패턴

### 6.2. 메트릭 활용 가이드

1. **대시보드 구성**

   - 상태별 빌드 수 차트 (성공/실패/진행중)
   - 리전별 리소스 분포 지도
   - 트리거 활성화 현황 표

2. **모니터링 지표**
   - 전체 빌드 수 추이
   - 프로젝트별 빌드 비중
   - 워커풀 사용 현황

### 6.3. 현재 상태 요약

- **수집 기능**: ✅ 완전 구현 (모든 필요 데이터 수집 중)
- **데이터 모델**: ✅ 충분 (모든 리소스 정보 완전 수집)
- **메트릭 구현**: ✅ 완료 (단순 개수 수집 방식으로 일관되게 구현)
- **대시보드 활용도**: ✅ 높음 (다양한 그룹화 옵션으로 세분화된 분석 가능)

**결론**: 단순 개수 수집 방식으로 다른 Google Cloud 도메인과 일관된 메트릭 체계를 구축하여 안정적이고 유지보수 가능한 모니터링 시스템을 제공한다.

---

## 📋 관련 리소스

- **플러그인 설정**: `src/spaceone/inventory/conf/cloud_service_conf.py`
- **데이터 모델**: `src/spaceone/inventory/model/cloud_build/`
- **커넥터**: `src/spaceone/inventory/connector/cloud_build/`
- **매니저**: `src/spaceone/inventory/manager/cloud_build/`
- **메트릭**: `src/spaceone/inventory/metrics/CloudBuild/`
