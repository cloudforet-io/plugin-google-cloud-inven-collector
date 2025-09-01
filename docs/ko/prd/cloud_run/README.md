# Google Cloud Run 리소스 수집기 요구사항 정의서 (플러그인 기반)

본 문서는 현재 `plugin-google-cloud-inven-collector` 플러그인에 구현된 Cloud Run 수집 기능의 요구사항을 명세한다. 수집된 데이터는 시스템의 인벤토리 정보로 활용되며, 단순 개수 수집 방식을 통해 대시보드에서 리소스 현황을 시각화하는 것을 목표로 한다.

✅ **현재 상태**: 단순 개수 수집 방식으로 다른 Google Cloud 도메인과 일관된 메트릭 체계를 구축하여 안정적이고 유지보수 가능한 모니터링 시스템을 제공한다.

---

## 📚 참고 문서

### Google Cloud Run 공식 문서

- **[Cloud Run 개요](https://cloud.google.com/run/docs/overview/what-is-cloud-run)**: Cloud Run 서비스의 전반적인 개념과 기능 설명
- **[Cloud Run APIs](https://cloud.google.com/run/docs/apis)**: Cloud Run API 개요 및 사용 가이드
- **[Cloud Run API Reference](https://cloud.google.com/run/docs/reference/rest)**: REST API 상세 명세 및 리소스 구조
- **[API 버전 정보](https://cloud.google.com/run/docs/reference/about-api-versions)**: v1과 v2 API 차이점 및 사용 권장사항
- **[서비스 배포 가이드](https://cloud.google.com/run/docs/deploying)**: Cloud Run 서비스 배포 및 관리
- **[작업(Job) 실행 가이드](https://cloud.google.com/run/docs/create-jobs)**: Cloud Run 배치 작업 생성 및 실행

### API 리소스 상세 문서

#### v1 API 리소스

- **[Locations API (v1)](https://cloud.google.com/run/docs/reference/rest/v1/projects.locations)**: 리전 정보 API 명세
- **[DomainMappings API (v1)](https://cloud.google.com/run/docs/reference/rest/v1/namespaces.domainmappings)**: 도메인 매핑 API 명세

#### v2 API 리소스

- **[Services API (v2)](https://cloud.google.com/run/docs/reference/rest/v2/projects.locations.services)**: 서비스 리소스 API 명세
- **[Revisions API (v2)](https://cloud.google.com/run/docs/reference/rest/v2/projects.locations.services.revisions)**: 리비전 리소스 API 명세
- **[Jobs API (v2)](https://cloud.google.com/run/docs/reference/rest/v2/projects.locations.jobs)**: 작업 리소스 API 명세
- **[Executions API (v2)](https://cloud.google.com/run/docs/reference/rest/v2/projects.locations.jobs.executions)**: 실행 리소스 API 명세
- **[Tasks API (v2)](https://cloud.google.com/run/docs/reference/rest/v2/projects.locations.jobs.executions.tasks)**: 태스크 리소스 API 명세
- **[WorkerPools API (v2)](https://cloud.google.com/run/docs/reference/rest/v2/projects.locations.workerPools)**: 워커풀 리소스 API 명세

---

## 🎯 수집 대상 리소스

현재 플러그인의 커넥터(`cloud_run_v1.py`, `cloud_run_v2.py`)는 아래 리소스의 수집 기능을 제공한다.

### 2.1. Location (리전 정보)

- **API (v1)**: `projects.locations.list`
- **수집 목적**: Cloud Run 서비스를 지원하는 전체 위치(리전) 목록을 조회하여, 다른 리소스들을 조회할 리전 목록을 동적으로 생성하는 데 사용된다.
- **리소스 구조**: [Location 리소스 스키마](https://cloud.google.com/run/docs/reference/rest/v1/projects.locations#Location)

### 2.2. Domain Mapping (도메인 매핑)

- **API (v1)**: `namespaces.domainmappings.list`
- **수집 목적**: 커스텀 도메인과 연결된 Cloud Run 서비스 정보를 수집한다. v1 API를 통해서만 조회가 가능하다.
- **리소스 구조**: [DomainMapping 리소스 스키마](https://cloud.google.com/run/docs/reference/rest/v1/namespaces.domainmappings#DomainMapping)

### 2.3. Service (서비스)

- **API (v2)**: `projects.locations.services.list`
- **수집 목적**: Cloud Run의 핵심 워크로드인 서비스의 기본 구성 정보를 수집한다.
- **리소스 구조**: [Service 리소스 스키마](https://cloud.google.com/run/docs/reference/rest/v2/projects.locations.services#Service)

### 2.4. Revision (리비전)

- **API (v2)**: `projects.locations.services.revisions.list`
- **수집 목적**: 각 서비스에 속한 불변 스냅샷인 리비전의 상세 구성(컨테이너, 리소스 할당량 등)을 수집한다.
- **리소스 구조**: [Revision 리소스 스키마](https://cloud.google.com/run/docs/reference/rest/v2/projects.locations.services.revisions#Revision)

### 2.5. Job (작업)

- **API (v2)**: `projects.locations.jobs.list`
- **수집 목적**: 배치 또는 스케줄링된 작업(Job)의 기본 구성 정보를 수집한다.
- **리소스 구조**: [Job 리소스 스키마](https://cloud.google.com/run/docs/reference/rest/v2/projects.locations.jobs#Job)

### 2.6. Execution (실행)

- **API (v2)**: `projects.locations.jobs.executions.list`
- **수집 목적**: 각 작업(Job)의 실행 기록을 수집하여 성공/실패 여부 및 라이프사이클을 추적한다.
- **리소스 구조**: [Execution 리소스 스키마](https://cloud.google.com/run/docs/reference/rest/v2/projects.locations.jobs.executions#Execution)

### 2.7. Task (태스크)

- **API (v2)**: `projects.locations.jobs.executions.tasks.list`
- **수집 목적**: 각 실행(Execution)을 구성하는 개별 태스크의 상세 정보를 수집하여 세분화된 작업 상태를 파악한다.
- **리소스 구조**: [Task 리소스 스키마](https://cloud.google.com/run/docs/reference/rest/v2/projects.locations.jobs.executions.tasks#Task)

### 2.8. Worker Pool (워커풀)

- **API (v2)**: `projects.locations.workerPools.list`
- **수집 목적**: Cloud Run 작업 실행을 위한 워커풀 구성 정보를 수집한다.
- **리소스 구조**: [WorkerPool 리소스 스키마](https://cloud.google.com/run/docs/reference/rest/v2/projects.locations.workerPools#WorkerPool)

### 2.9. Worker Pool Revision (워커풀 리비전)

- **API (v2)**: `projects.locations.workerPools.revisions.list`
- **수집 목적**: 워커풀의 리비전 정보를 수집하여 구성 변경 이력을 추적한다.

---

## 📊 핵심 메트릭 정의 (단순 개수 수집 방식)

### 3.1. 메트릭 수집 방식

다른 Google Cloud 도메인과의 일관성을 위해 Cloud Run도 **단순 개수 수집 방식**을 사용한다. 이는 대시보드에서 리소스의 전체적인 현황을 파악하고 관리하는 데 초점을 맞춘다.

### 3.2. 구현된 메트릭 목록

| 메트릭 파일                               | 메트릭 이름          | 방식              | 분석 가능 요소                                        |
| :---------------------------------------- | :------------------- | :---------------- | :---------------------------------------------------- |
| `Service/service_count.yaml`              | Service Count        | `operator: count` | 리전별, 프로젝트별, 상태별, 트래픽 리비전별 서비스 수 |
| `Job/job_count.yaml`                      | Job Count            | `operator: count` | 리전별, 프로젝트별, 상태별, 병렬성별 작업 수          |
| `DomainMapping/domain_mapping_count.yaml` | Domain Mapping Count | `operator: count` | 커스텀 도메인 매핑 수                                 |
| `WorkerPool/worker_pool_count.yaml`       | WorkerPool Count     | `operator: count` | Cloud Run 워커풀 수                                   |

### 3.3. 메트릭 활용 방안

단순 개수 수집 방식으로도 다양한 대시보드 분석이 가능하다:

- **서비스 현황 모니터링**: 전체 서비스 수, 상태별 분포
- **작업 관리**: 배치 작업 수 및 병렬성 현황
- **도메인 매핑**: 커스텀 도메인 연결 현황
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
- **API 버전 분리**: v1과 v2 API의 역할이 명확히 구분되어 있다.
  - **v1**: `Locations`, `Domain Mappings` 조회에 사용된다.
  - **v2**: `Services`, `Revisions`, `Jobs`, `Executions`, `Tasks`, `Worker Pools` 등 핵심 워크로드 조회에 사용된다.
- **리소스 조회 방식**: `v1.projects.locations.list`를 통해 전체 리전 목록을 가져온 후, 각 리전을 순회하며 v2 API들을 호출하여 리소스를 수집하는 방식을 사용한다.
- **페이지네이션 처리**: 각 커넥터 메소드 내부에 `while` 루프와 `list_next(request, response)` 또는 `continue` 토큰을 확인하는 로직을 사용하여, 모든 페이지의 결과를 수집하도록 구현되어 있다.

#### Service (서비스)

- **Manager**: `CloudRunServiceManager`
- **Connector**: `CloudRunV1Connector` (locations 조회용), `CloudRunV2Connector`
- **API 호출 순서**:
  1. `cloud_run_v1_conn.list_locations()`: 전체 리전 목록 조회
  2. 각 리전(`location_id`)을 순회하며 `cloud_run_v2_conn.list_services(parent=f"projects/{project_id}/locations/{location_id}")` 호출
  3. 각 `service`에 대해 `cloud_run_v2_conn.list_revisions(parent=service_name)` 호출
- **데이터 모델**: `traffic` (트래픽 할당 정보), `revisions` (리비전 목록) 필드 존재
- **메트릭 구현**: `service_count.yaml`

#### Job (작업)

- **Manager**: `CloudRunJobManager`
- **Connector**: `CloudRunV1Connector` (locations 조회용), `CloudRunV2Connector`
- **API 호출 순서**:
  1. `cloud_run_v1_conn.list_locations()`: 전체 리전 목록 조회
  2. 각 리전(`location_id`)을 순회하며 `cloud_run_v2_conn.list_jobs(parent=f"projects/{project_id}/locations/{location_id}")` 호출
  3. 각 `job`에 대해 `cloud_run_v2_conn.list_executions(parent=job_name)` 호출
  4. 각 `execution`에 대해 `cloud_run_v2_conn.list_tasks(parent=execution_name)` 호출
- **데이터 모델**: `latest_created_execution` (create_time, completion_time, completion_status) 필드 존재
- **메트릭 구현**: `job_count.yaml`

#### Domain Mapping (도메인 매핑)

- **Manager**: `CloudRunDomainMappingManager`
- **Connector**: `CloudRunV1Connector` (v1 API만 지원)
- **API 호출 순서**:
  1. `cloud_run_v1_conn.list_domain_mappings(parent=f"namespaces/{project_id}")` 호출
- **데이터 모델**: 도메인 매핑 구성 정보
- **메트릭 구현**: `domain_mapping_count.yaml`

#### Worker Pool (워커풀)

- **Manager**: `CloudRunWorkerPoolManager`
- **Connector**: `CloudRunV1Connector` (locations 조회용), `CloudRunV2Connector`
- **API 호출 순서**:
  1. `cloud_run_v1_conn.list_locations()`: 전체 리전 목록 조회
  2. 각 리전(`location_id`)을 순회하며 `cloud_run_v2_conn.list_worker_pools(parent=f"projects/{project_id}/locations/{location_id}")` 호출
  3. 각 `worker_pool`에 대해 `cloud_run_v2_conn.list_worker_pool_revisions(parent=worker_pool_name)` 호출
- **데이터 모델**: 워커풀 구성 및 리비전 정보
- **메트릭 구현**: `worker_pool_count.yaml`

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

### 6.1. 메트릭 활용 가이드

1. **대시보드 구성**

   - 서비스 수 전체 개요 차트
   - 리전별 리소스 분포 지도
   - 작업 수행 현황 대시보드
   - 도메인 매핑 현황 표

2. **모니터링 지표**
   - 전체 Cloud Run 서비스 수 추이
   - 프로젝트별 리소스 비중
   - 작업 실행 빈도 및 병렬성 현황

### 6.2. 현재 상태 요약

- **수집 기능**: ✅ 완전 구현 (모든 필요 리소스 수집 중)
- **데이터 모델**: ✅ 충분 (모든 리소스 정보 완전 수집)
- **메트릭 구현**: ✅ 완료 (단순 개수 수집 방식으로 일관되게 구현)
- **대시보드 활용도**: ✅ 높음 (다양한 그룹화 옵션으로 세분화된 분석 가능)

**결론**: 단순 개수 수집 방식으로 다른 Google Cloud 도메인과 일관된 메트릭 체계를 구축하여 안정적이고 유지보수 가능한 모니터링 시스템을 제공한다.

---

## 📋 관련 리소스

- **플러그인 설정**: `src/spaceone/inventory/conf/cloud_service_conf.py`
- **데이터 모델**: `src/spaceone/inventory/model/cloud_run/`
- **커넥터**: `src/spaceone/inventory/connector/cloud_run/`
- **매니저**: `src/spaceone/inventory/manager/cloud_run/`
- **메트릭**: `src/spaceone/inventory/metrics/CloudRun/`
