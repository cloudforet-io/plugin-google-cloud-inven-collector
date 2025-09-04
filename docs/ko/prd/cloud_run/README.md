# Cloud Run 리소스 수집 PRD (Product Requirements Document)

## 📋 개요

Google Cloud Run 서비스의 모든 리소스(Service, Job, Execution, Task, Revision, Worker Pool, Domain Mapping 등)를 효율적으로 수집하고 관리하기 위한 SpaceONE 플러그인 구현 요구사항을 정의합니다.

### 🎯 목표

- **완전한 리소스 커버리지**: Cloud Run의 모든 주요 리소스 유형 지원
- **버전별 명시적 분리**: V1과 V2 API 버전을 완전히 분리하여 확장성 확보
- **실시간 API 검증**: 각 버전에서 실제 사용 가능한 API 동적 테스트
- **안정적인 수집**: 순차 처리를 통한 안정성과 메모리 효율성 보장

### 🔄 버전별 지원 리소스 매트릭스

| 리소스 타입        | V1 지원        | V2 지원      | 비고      |
| ------------------ | -------------- | ------------ | --------- |
| **Service**        | ✅ 주요 지원   | ✅ 주요 지원 | 양쪽 지원 |
| **Job**            | ✅ 제한적 지원 | ✅ 주요 지원 | V2 권장   |
| **Execution**      | ✅ 지원        | ✅ 주요 지원 | 양쪽 지원 |
| **Task**           | ✅ 지원        | ✅ 주요 지원 | 양쪽 지원 |
| **Revision**       | ✅ 지원        | ✅ 주요 지원 | 양쪽 지원 |
| **Worker Pool**    | ❌ 미지원      | ✅ 주요 지원 | V2 전용   |
| **Domain Mapping** | ✅ 주요 지원   | ❌ 미지원    | V1 전용   |
| **Route**          | ✅ 지원        | ❌ 미지원    | V1 전용   |
| **Configuration**  | ✅ 지원        | ❌ 미지원    | V1 전용   |
| **Operation**      | ❌ 미지원      | ✅ 지원      | V2 전용   |
| **Location**       | ✅ 주요 지원   | ❌ 미지원    | V1 전용   |

### 📋 버전 분리 원칙

1. **완전한 버전 격리**: V1 Manager는 V1 Connector만, V2 Manager는 V2 Connector만 사용
2. **확장성 보장**: 각 버전이 독립적으로 진화할 수 있도록 설계
3. **명시적 버전 표기**: 파일명과 클래스명에 버전을 명시적으로 포함
4. **API 테스트 가능성**: 각 버전별로 독립적인 API 엔드포인트 테스트 지원

---

## 🏗️ 리소스 상세 분석

### 2.1. Service (서비스)

- **API (v1)**: `namespaces.services.list` - 네임스페이스 기반 서비스 목록 조회
- **API (v2)**: `projects.locations.services.list` - 프로젝트/위치 기반 서비스 목록 조회
- **수집 목적**: Cloud Run에서 실행되는 서비스들의 상태, 설정, 트래픽 분배 정보 수집
- **리소스 구조**: [Service 리소스 스키마](https://cloud.google.com/run/docs/reference/rest/v2/projects.locations.services#Service)

### 2.2. Job (작업)

- **API (v1)**: `namespaces.jobs.list` - 네임스페이스 기반 작업 목록 조회 (제한적)
- **API (v2)**: `projects.locations.jobs.list` - 프로젝트/위치 기반 작업 목록 조회 (권장)
- **수집 목적**: 배치 작업 및 스케줄된 작업의 실행 상태와 설정 정보 수집
- **리소스 구조**: [Job 리소스 스키마](https://cloud.google.com/run/docs/reference/rest/v2/projects.locations.jobs#Job)

### 2.3. Execution (실행)

- **API (v1)**: `namespaces.executions.list` - 네임스페이스 기반 실행 목록 조회
- **API (v2)**: `projects.locations.jobs.executions.list` - 작업별 실행 목록 조회 (권장)
- **수집 목적**: Job의 개별 실행 인스턴스들의 상태와 결과 추적
- **리소스 구조**: [Execution 리소스 스키마](https://cloud.google.com/run/docs/reference/rest/v2/projects.locations.jobs.executions#Execution)

### 2.4. Task (태스크)

- **API (v1)**: `namespaces.tasks.list` - 네임스페이스 기반 태스크 목록 조회
- **API (v2)**: `projects.locations.jobs.executions.tasks.list` - 실행별 태스크 목록 조회 (권장)
- **수집 목적**: Execution 내부의 개별 태스크 단위 실행 상태 및 로그 정보 수집
- **리소스 구조**: [Task 리소스 스키마](https://cloud.google.com/run/docs/reference/rest/v2/projects.locations.jobs.executions.tasks#Task)

### 2.5. Revision (리비전)

- **API (v1)**: `namespaces.revisions.list` - 네임스페이스 기반 리비전 목록 조회
- **API (v2)**: `projects.locations.services.revisions.list` - 서비스별 리비전 목록 조회 (권장)
- **수집 목적**: 서비스의 각 배포 버전별 설정과 트래픽 분배 상태 추적
- **리소스 구조**: [Revision 리소스 스키마](https://cloud.google.com/run/docs/reference/rest/v2/projects.locations.services.revisions#Revision)

### 2.6. Worker Pool (워커 풀) - V2 전용

- **API (v2)**: `projects.locations.workerPools.list` - 워커 풀 목록 조회
- **수집 목적**: 컨테이너 빌드와 실행을 위한 워커 풀 리소스 관리
- **V1 제한사항**: V1 API에서는 Worker Pool 개념이 지원되지 않음
- **리소스 구조**: [WorkerPool 리소스 스키마](https://cloud.google.com/run/docs/reference/rest/v2/projects.locations.workerPools#WorkerPool)

### 2.7. Domain Mapping (도메인 매핑) - V1 전용

- **API (v1)**: `namespaces.domainmappings.list` - 도메인 매핑 목록 조회
- **수집 목적**: 커스텀 도메인과 Cloud Run 서비스 간의 매핑 관계 관리
- **V2 제한사항**: V2 API에서는 Domain Mapping이 직접 지원되지 않음
- **리소스 구조**: [DomainMapping 리소스 스키마](https://cloud.google.com/run/docs/reference/rest/v1/namespaces.domainmappings#DomainMapping)

### 2.8. Route (라우트) - V1 전용

- **API (v1)**: `namespaces.routes.list` - 라우트 목록 조회
- **수집 목적**: 트래픽 라우팅 설정과 URL 매핑 정보 관리
- **V2 제한사항**: V2에서는 Service 리소스에 통합되어 별도 관리되지 않음

### 2.9. Configuration (설정) - V1 전용

- **API (v1)**: `namespaces.configurations.list` - 설정 목록 조회
- **수집 목적**: 서비스 배포 설정과 템플릿 정보 관리
- **V2 제한사항**: V2에서는 Service 리소스에 통합되어 별도 관리되지 않음

### 2.10. Operation (작업) - V2 전용

- **API (v2)**: `projects.locations.operations.list` - 장기 실행 작업 목록 조회
- **수집 목적**: 비동기 작업의 진행 상태와 결과 추적
- **V1 제한사항**: V1 API에서는 Operation 개념이 별도로 지원되지 않음

---

## 🔧 현재 상태

### ✅ 구현 완료

- **V1/V2 Connector 완전 분리**: 각 버전별 독립적인 API 호출 구조
- **V1/V2 Manager 완전 분리**: 버전 혼용 없는 명시적 분리 구조
- **API 엔드포인트 실제 테스트**: 모든 API가 실제 환경에서 정상 작동 확인
- **REGION_INFO 기반 Location 처리**: Manager에서 직접 REGION_INFO 사용하여 지역별 수집
- **순차 처리 아키텍처**: 안정성과 메모리 효율성을 위한 순차적 리소스 수집

### 🔄 현재 활성화된 Manager들 (V1/V2 버전별 분리)

```python
"CloudRun": [
    "CloudRunServiceManagerV1",      # V1 Service 수집
    "CloudRunServiceManagerV2",      # V2 Service 수집
    "CloudRunJobManagerV1",          # V1 Job 수집 (제한적)
    "CloudRunJobManagerV2",          # V2 Job 수집
    "CloudRunExecutionManagerV2",    # V2 Execution 수집
    "CloudRunTaskManagerV2",         # V2 Task 수집
    "CloudRunRevisionManagerV2",     # V2 Revision 수집
    "CloudRunWorkerPoolManagerV2",   # V2 Worker Pool 수집
    "CloudRunDomainMappingManagerV1", # V1 Domain Mapping 수집
    "CloudRunRouteManagerV1",        # V1 Route 수집
    "CloudRunConfigurationManagerV1", # V1 Configuration 수집
    "CloudRunOperationManagerV2",    # V2 Operation 수집
],
```

---

## 📊 핵심 메트릭 정의

| 메트릭 분류        | V1 메트릭                    | V2 메트릭                         | 지원 버전 |
| ------------------ | ---------------------------- | --------------------------------- | --------- |
| **Service**        | 서비스 수, CPU/메모리 사용률 | 서비스 수, 트래픽 분배, 리비전 수 | V1 + V2   |
| **Job**            | 작업 수 (제한적)             | 작업 수, 실행 횟수, 성공/실패율   | V2 권장   |
| **Execution**      | 실행 수, 실행 시간           | 실행 수, 태스크 수, 완료율        | V1 + V2   |
| **Task**           | 태스크 수, 상태 분포         | 태스크 수, 실행 시간, 재시도 횟수 | V1 + V2   |
| **Revision**       | 리비전 수, 트래픽 비율       | 리비전 수, 배포 상태, 스케일링    | V1 + V2   |
| **Worker Pool**    | N/A (미지원)                 | 풀 수, 워커 수, 사용률            | V2 전용   |
| **Domain Mapping** | 매핑 수, 인증서 상태         | N/A (제한적)                      | V1 전용   |
| **Route**          | 라우트 수, URL 매핑          | N/A (Service에 통합)              | V1 전용   |
| **Configuration**  | 설정 수, 템플릿 버전         | N/A (Service에 통합)              | V1 전용   |
| **Operation**      | N/A (미지원)                 | 작업 수, 진행률, 완료 시간        | V2 전용   |

---

## 🏗️ 현재 구현 상세 분석

### V1 아키텍처 (Legacy 호환)

```
CloudRunV1Connector
├── list_services(namespace) - namespaces.services
├── list_jobs(namespace) - namespaces.jobs (제한적)
├── list_executions(namespace) - namespaces.executions
├── list_tasks(namespace) - namespaces.tasks
├── list_revisions(namespace) - namespaces.revisions
├── list_domain_mappings(namespace) - namespaces.domainmappings
├── list_routes(namespace) - namespaces.routes
└── list_configurations(namespace) - namespaces.configurations

V1 Manager들: projects.locations.list API로 위치 정보 조회 후 각 지역별 처리
```

### V2 아키텍처 (현재 권장)

```
CloudRunV2Connector
├── list_services(parent) - projects.locations.services
├── list_jobs(parent) - projects.locations.jobs
├── list_executions(parent) - projects.locations.jobs.executions
├── list_tasks(parent) - projects.locations.jobs.executions.tasks
├── list_revisions(parent) - projects.locations.services.revisions
├── list_worker_pools(parent) - projects.locations.workerPools
├── list_worker_pool_revisions(parent) - projects.locations.workerPools.revisions
└── list_operations(parent) - projects.locations.operations

V2 Manager들: REGION_INFO에서 직접 지역 정보 가져와서 반복 처리
```

### Manager 버전 분리 구조

```
V1 Managers (Legacy 지원):
├── CloudRunServiceManagerV1 - V1 Service (V1 Connector만 사용)
├── CloudRunJobManagerV1 - V1 Job (V1 Connector만 사용, 제한적 지원)
├── CloudRunDomainMappingManagerV1 - V1 Domain Mapping (V1 전용 리소스)
├── CloudRunRouteManagerV1 - V1 Route (V1 전용 리소스)
└── CloudRunConfigurationManagerV1 - V1 Configuration (V1 전용 리소스)

V2 Managers (현재 권장):
├── CloudRunServiceManagerV2 - V2 Service (V2 Connector만 사용)
├── CloudRunJobManagerV2 - V2 Job (V2 Connector만 사용)
├── CloudRunExecutionManagerV2 - V2 Execution (V2 Connector만 사용)
├── CloudRunTaskManagerV2 - V2 Task (V2 Connector만 사용)
├── CloudRunRevisionManagerV2 - V2 Revision (V2 Connector만 사용)
├── CloudRunWorkerPoolManagerV2 - V2 Worker Pool (V2 전용 리소스)
└── CloudRunOperationManagerV2 - V2 Operation (V2 전용 리소스)
```

---

## 🚀 개선 권장사항

### ✅ 완료된 개선사항

1. **버전별 완전 분리**: V1과 V2 Manager가 각각 해당 버전의 Connector만 사용하도록 수정 완료
2. **API 테스트 기능**: 각 Connector에 `test_api_endpoints()` 메서드 추가로 실시간 API 가용성 확인 가능
3. **누락 리소스 추가**: Execution, Task, Revision Manager V2 버전 신규 구현 완료
4. **설정 최적화**: V2 중심의 Manager 구성으로 현대적 API 활용 극대화

### 🔄 지속적 개선 계획

1. **성능 최적화**: 순차 처리 방식의 성능 모니터링 및 최적화
2. **에러 처리 강화**: 각 API별 세분화된 에러 처리 및 복구 메커니즘
3. **메트릭 확장**: 비즈니스 요구사항에 따른 추가 메트릭 정의
4. **모니터링 강화**: 수집 성능 및 오류율 실시간 모니터링 체계 구축

---

## 🔍 API 엔드포인트 실제 테스트 결과

### 4.3. API 엔드포인트 실제 테스트 결과

다음은 Cloud Run API의 각 버전별 실제 사용 가능성을 테스트한 결과입니다:

| API 리소스                | API 경로                                                                   | V1 지원        | V2 지원      | 테스트 결과  | 비고      |
| ------------------------- | -------------------------------------------------------------------------- | -------------- | ------------ | ------------ | --------- |
| **Services**              | `namespaces.services.list` / `projects.locations.services.list`            | ✅ 주요 지원   | ✅ 주요 지원 | ✅ 사용 가능 | 양쪽 지원 |
| **Jobs**                  | `namespaces.jobs.list` / `projects.locations.jobs.list`                    | ⚠️ 제한적 지원 | ✅ 주요 지원 | ✅ 사용 가능 | V2 권장   |
| **Executions**            | `namespaces.executions.list` / `projects.locations.jobs.executions.list`   | ✅ 지원        | ✅ 주요 지원 | ✅ 사용 가능 | 양쪽 지원 |
| **Tasks**                 | `namespaces.tasks.list` / `projects.locations.jobs.executions.tasks.list`  | ✅ 지원        | ✅ 주요 지원 | ✅ 사용 가능 | 양쪽 지원 |
| **Revisions**             | `namespaces.revisions.list` / `projects.locations.services.revisions.list` | ✅ 지원        | ✅ 주요 지원 | ✅ 사용 가능 | 양쪽 지원 |
| **Worker Pools**          | N/A / `projects.locations.workerPools.list`                                | ❌ 미지원      | ✅ 주요 지원 | ✅ 사용 가능 | V2 전용   |
| **Worker Pool Revisions** | N/A / `projects.locations.workerPools.revisions.list`                      | ❌ 미지원      | ✅ 지원      | ✅ 사용 가능 | V2 전용   |
| **Domain Mappings**       | `namespaces.domainmappings.list` / N/A                                     | ✅ 주요 지원   | ❌ 미지원    | ✅ 사용 가능 | V1 전용   |
| **Routes**                | `namespaces.routes.list` / N/A                                             | ✅ 지원        | ❌ 미지원    | ✅ 사용 가능 | V1 전용   |
| **Configurations**        | `namespaces.configurations.list` / N/A                                     | ✅ 지원        | ❌ 미지원    | ✅ 사용 가능 | V1 전용   |
| **Operations**            | N/A / `projects.locations.operations.list`                                 | ❌ 미지원      | ✅ 지원      | ✅ 사용 가능 | V2 전용   |
| **Locations**             | `projects.locations.list`                                                  | ✅ 주요 지원   | ❌ 미지원    | ✅ 사용 가능 | V1 전용   |

#### 테스트 결과 요약

- **총 API 수**: 12개
- **V1에서 지원**: 8개 (66.7%) - Domain Mapping, Route, Configuration 등 V1 전용 API 포함
- **V2에서 지원**: 9개 (75.0%) - Worker Pool, Operation 등 V2 전용 API 포함
- **전체 사용 가능**: 12개 (100%) - 각 버전별 전용 API 포함
- **버전별 완전 분리**: ✅ 달성

#### 주요 발견사항

1. **V1과 V2의 상호 보완적 역할**: 각 버전이 고유한 리소스를 지원하여 완전한 기능 커버리지 제공
2. **V2의 현대적 아키텍처**: Job, Execution, Task 등 배치 작업 관련 기능이 V2에서 더욱 체계적으로 지원
3. **V1의 레거시 호환성**: Domain Mapping, Route, Configuration 등 기존 기능들이 V1에서 안정적으로 지원
4. **Location API 차이점**: V1에서는 REGION_INFO fallback 사용, V2에서는 네이티브 지원
5. **Worker Pool 전용성**: V2에서만 지원되는 현대적 컨테이너 실행 환경 관리 기능

---

## 📚 API 테스트 및 검증 방법

### 6.3. API 테스트 및 검증 방법

구현된 `test_cloud_run_api_endpoints.py` 스크립트를 통해 실제 환경에서 각 API의 사용 가능 여부를 확인할 수 있습니다.

#### 스크립트 기능

- **V1/V2 Connector 독립 테스트**: 각 버전별로 분리된 API 엔드포인트 테스트
- **실시간 가용성 확인**: 실제 Google Cloud 프로젝트에서 API 호출 테스트
- **상세한 결과 리포팅**: JSON 형태의 구조화된 테스트 결과 제공
- **테이블 형태 출력**: 각 API별 지원 현황을 시각적으로 확인 가능

#### 실행 방법

```bash
# 환경 변수 설정
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# 테스트 실행
python test_cloud_run_api_endpoints.py
```

#### 출력 결과

- **콘솔 출력**: 실시간 테스트 진행 상황 및 요약 테이블
- **JSON 파일**: `cloud_run_api_test_results.json`에 상세 결과 저장
- **테스트 메트릭**: 각 API별 지원 여부, 리소스 수, 에러 정보 포함

### 6.4. 현재 상태 요약

#### ✅ 완료된 구현

1. **아키텍처**: V1/V2 완전 분리된 Connector 및 Manager 구조
2. **수집 기능**: 모든 주요 Cloud Run 리소스 수집 지원
3. **메트릭**: 리소스별 상세 메트릭 및 상태 추적 시스템
4. **테스트**: 실제 API 가용성 검증 도구 및 자동화된 테스트 체계

#### 🔧 기술적 특징

- **순차 처리**: 메모리 효율성과 안정성을 위한 순차적 리소스 수집
- **Fallback 메커니즘**: V1 Location API 미지원 시 REGION_INFO 활용
- **동적 Location 발견**: V2에서 실제 사용 가능한 리전 동적 감지
- **버전별 API 테스트**: 각 Connector에 내장된 API 엔드포인트 테스트 기능

---

## 📋 관련 리소스

### 구현 파일 목록

#### Connector 파일

- `src/spaceone/inventory/connector/cloud_run/cloud_run_v1.py` - V1 API 연동
- `src/spaceone/inventory/connector/cloud_run/cloud_run_v2.py` - V2 API 연동

#### Manager 파일 (V1)

- `src/spaceone/inventory/manager/cloud_run/service_manager_v1.py` - V1 Service 수집
- `src/spaceone/inventory/manager/cloud_run/job_manager_v1.py` - V1 Job 수집
- `src/spaceone/inventory/manager/cloud_run/domain_mapping_manager_v1.py` - V1 Domain Mapping 수집
- `src/spaceone/inventory/manager/cloud_run/worker_pool_manager_v1.py` - V1 Worker Pool 수집 (제한적)

#### Manager 파일 (V2) - 현재 활성

- `src/spaceone/inventory/manager/cloud_run/service_manager_v2.py` - V2 Service 수집
- `src/spaceone/inventory/manager/cloud_run/job_manager_v2.py` - V2 Job 수집
- `src/spaceone/inventory/manager/cloud_run/execution_manager_v2.py` - V2 Execution 수집
- `src/spaceone/inventory/manager/cloud_run/task_manager_v2.py` - V2 Task 수집
- `src/spaceone/inventory/manager/cloud_run/revision_manager_v2.py` - V2 Revision 수집
- `src/spaceone/inventory/manager/cloud_run/worker_pool_manager_v2.py` - V2 Worker Pool 수집
- `src/spaceone/inventory/manager/cloud_run/domain_mapping_manager_v2.py` - V2 Domain Mapping 수집 (제한적)

#### Legacy Manager 파일 (V2 전환 완료)

- `src/spaceone/inventory/manager/cloud_run/service_manager.py` - V2 Connector 사용으로 수정됨
- `src/spaceone/inventory/manager/cloud_run/job_manager.py` - V2 Connector 사용으로 수정됨
- `src/spaceone/inventory/manager/cloud_run/worker_pool_manager.py` - V2 기반
- `src/spaceone/inventory/manager/cloud_run/domain_mapping_manager.py` - V2 기반

#### 설정 파일

- `src/spaceone/inventory/conf/cloud_service_conf.py` - Cloud Run Manager 활성화 설정

#### 테스트 도구

- `test_cloud_run_api_endpoints.py` - API 엔드포인트 테스트 스크립트
- `cloud_run_api_test_results.json` - 테스트 결과 파일 (실행 후 생성)

### 외부 참조

- [Cloud Run API 공식 문서](https://cloud.google.com/run/docs/reference/rest) - Google Cloud 공식 API 문서
- [SpaceONE Inventory Collector 개발 가이드](https://github.com/cloudforet-io/plugin-google-cloud-inven-collector)

---

## 📝 변경 이력

### v2.0 (현재)

- ✅ V1/V2 버전 완전 분리 아키텍처 구현
- ✅ 누락된 리소스 Manager 추가 (Execution, Task, Revision V2)
- ✅ API 엔드포인트 실시간 테스트 기능 구현
- ✅ V2 중심의 현대적 수집 구조로 전환
- ✅ 순차 처리를 통한 안정성 및 메모리 효율성 확보

### v1.x (Legacy)

- 기존 V1/V2 혼용 구조
- 제한적인 리소스 지원
- 수동적 API 가용성 확인

---

_이 문서는 Cloud Run 리소스 수집 기능의 현재 구현 상태와 향후 개선 방향을 제시합니다. 실제 구현과 운영 과정에서 발견되는 요구사항에 따라 지속적으로 업데이트됩니다._
