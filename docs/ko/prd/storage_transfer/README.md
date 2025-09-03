# Google Cloud Storage Transfer 인벤토리 수집 제품 요구사항 정의서 (PRD)

## 1. 비즈니스 요구사항 (Business Requirements)

### 1.1. 목적 (Purpose)
SpaceONE 인벤토리 플랫폼에서 Google Cloud Storage Transfer Service 리소스를 자동으로 수집, 분류, 모니터링하여 데이터 전송 작업 관리 효율성을 극대화합니다. 데이터 엔지니어링팀과 인프라 관리팀이 Storage Transfer 작업의 상태, 성능, 비용을 통합적으로 관리할 수 있도록 지원합니다.

### 1.2. 사용자 스토리 (User Stories)
- **데이터 엔지니어**: 모든 프로젝트의 Storage Transfer 작업 현황을 한눈에 파악하고 데이터 파이프라인 최적화 포인트를 식별
- **인프라 관리자**: 전송 작업의 성능과 비용을 모니터링하여 리소스 사용량을 최적화
- **팀 리더**: 팀별 데이터 전송 작업 사용량과 성과를 추적하여 데이터 마이그레이션 전략 수립

### 1.3. 수용 기준 (Acceptance Criteria)
**P0 (필수)**:
- 모든 활성 Transfer Job 정보 수집 (100% 정확도)
- 작업별 실행 기록(Transfer Operation) 정보 연계
- 서비스 계정 및 에이전트 풀 정보 수집

**P1 (중요)**:
- 전송 성능 메트릭 수집 (처리량, 객체 수 등)
- 전송 작업 스케줄 및 상태 정보
- 다중 프로젝트 병렬 수집

**P2 (선택)**:
- 비용 분석 및 최적화 제안
- 예측적 알림 기능

## 2. API 인터페이스 (API Interface)

### 2.1. 수집 엔드포인트 (Collection Endpoints)

#### 2.1.1. Storage Transfer 리소스 수집 API
- **경로**: Internal API (플러그인 인터페이스)
- **메서드**: `collect_cloud_service()`
- **인증**: Google Cloud Service Account 키 기반
- **Rate Limit**: Google Cloud API 할당량 (분당 1000 요청)
- **Request 스키마**:
  ```json
  {
    "secret_data": {
      "project_id": "string",
      "type": "service_account",
      "private_key": "string",
      "client_email": "string"
    },
    "options": {
      "job_filter": "optional array"
    }
  }
  ```
- **Response 스키마**:
  ```json
  {
    "resources": [
      {
        "name": "transfer_job_name",
        "data": "TransferJob/Operation/AgentPool 모델",
        "reference": {
          "resource_id": "job_name",
          "external_link": "console_url"
        },
        "region_code": "global",
        "account": "project_id"
      }
    ],
    "errors": []
  }
  ```
- **상태 코드**: Success(200), Authentication Error(401), API Quota Exceeded(429)

## 3. 데이터 & 아키텍처 (Data & Architecture)

### 3.1. 데이터 모델 (Data Models)

#### 3.1.1. 주요 엔터티
- **TransferJob**: 전송 작업 메인 엔터티
  - `job_name`: 전송 작업 이름
  - `project_id`: 프로젝트 식별자
  - `status`: 작업 상태 (ENABLED, DISABLED, DELETED)
  - `description`: 작업 설명
  - `transfer_spec`: 전송 사양 (소스, 싱크, 옵션)
  - `schedule`: 스케줄 정보
  - `notification_config`: 알림 구성
  - `creation_time`: 생성 시간
  - `last_modification_time`: 마지막 수정 시간

- **TransferOperation**: 전송 작업 실행 엔터티
  - `operation_name`: 작업 실행 이름
  - `transfer_job_name`: 소속된 전송 작업 이름
  - `status`: 실행 상태 (IN_PROGRESS, SUCCESS, FAILED)
  - `counters`: 성능 카운터 (전송된 파일/바이트 수 등)
  - `start_time`: 시작 시간
  - `end_time`: 종료 시간
  - `error_breakdowns`: 오류 요약

- **AgentPool**: 에이전트 풀 엔터티
  - `name`: 에이전트 풀 이름
  - `display_name`: 표시 이름
  - `state`: 상태 (CREATED, CONNECTED)
  - `bandwidth_limit`: 대역폭 제한

- **ServiceAccount**: 서비스 계정 엔터티
  - `account_email`: 서비스 계정 이메일
  - `subject_id`: 고유 식별자

#### 3.1.2. 트랜잭션 바운더리
- **읽기 전용 수집**: 모든 API 호출은 READ COMMITTED 격리 수준
- **프로젝트 단위 수집**: 프로젝트별로 모든 관련 리소스를 일괄 수집
- **실패 처리**: 개별 리소스 수집 실패가 전체 수집에 영향 없음

#### 3.1.3. 캐싱 전략
- **API 응답 캐시**: 없음 (실시간 상태 반영 필요)
- **메타데이터 캐시**: 5분 TTL로 Cloud Service Type 정보 캐싱

## 4. 비즈니스 로직 플로우 (Business Logic Flow)

### 4.1. 정상 플로우
1. **인증 검증**: Service Account 크리덴셜 유효성 확인
2. **서비스 계정 조회**: `googleServiceAccounts.get` API를 통한 프로젝트 전용 서비스 계정 정보 수집
3. **에이전트 풀 조회**: `projects.agentPools.list` API를 통한 모든 에이전트 풀 수집
4. **전송 작업 조회**: `transferJobs.list` API를 통한 모든 전송 작업 수집
5. **작업별 실행 내역 수집**: 각 전송 작업에 대해 `transferOperations.list` API 호출
6. **데이터 변환**: SpaceONE 표준 모델로 변환
7. **응답 생성**: 각 리소스 타입별 Response 객체 생성

### 4.2. 예외 플로우
- **인증 실패**: 즉시 실패 반환, 재시도 없음
- **API 할당량 초과**: 지수 백오프로 재시도 (최대 3회)
- **네트워크 오류**: 연결 실패, 타임아웃에 대한 재시도 로직
- **개별 작업 실패**: 로그 기록 후 다음 작업 진행
- **데이터 파싱 실패**: 에러 응답 생성, 수집 계속

### 4.3. 복구 전략
- **부분 실패 허용**: 일부 리소스 수집 실패 시에도 성공한 데이터 반환
- **재시도 로직**: 네트워크 오류에 대해서만 제한적 재시도
- **장애 격리**: 리소스별 독립적 처리로 장애 전파 방지

## 5. 외부 연동 (External Integration)

### 5.1. Google Cloud Storage Transfer API
- **의존 서비스**: Google Cloud Storage Transfer API v1
- **엔드포인트**: `https://storagetransfer.googleapis.com`
- **인증 방식**: Service Account 키 파일 기반 OAuth 2.0
- **API 할당량**: 프로젝트당 분당 1000 요청
- **장애 대응**: 
  - HTTP 429 (할당량 초과): 지수 백오프 재시도
  - HTTP 404 (리소스 없음): 정상 처리 (빈 결과 반환)
  - 기타 HTTP 오류: 로그 기록 후 다음 리소스 진행

### 5.2. SpaceONE 플랫폼 연동
- **플러그인 인터페이스**: SpaceONE Inventory Collector Protocol
- **데이터 포맷**: CloudServiceResponse 표준 모델
- **메타데이터**: DynamicLayout 기반 UI 구성
- **위젯**: 차트 및 테이블 형태 대시보드 제공

## 6. 보안 & 컴플라이언스 (Security & Compliance)

### 6.1. 인증 및 인가
- **Google Cloud 인증**: Service Account 키 파일 기반 OAuth 2.0
- **필수 IAM 권한**:
  - `storagetransfer.jobs.list`
  - `storagetransfer.jobs.get`
  - `storagetransfer.operations.list`
  - `storagetransfer.agentPools.list`
- **권한 범위**: 프로젝트 수준 읽기 전용 권한

### 6.2. 데이터 보호
- **전송 중 암호화**: HTTPS/TLS 1.2 이상 사용
- **저장 시 암호화**: SpaceONE 플랫폼 표준 암호화 적용
- **민감 정보 처리**: Service Account 키는 메모리에서만 처리, 로그 미기록

### 6.3. 감사 로그
- **수집 이벤트**: 성공/실패 로그 기록
- **민감 정보 제외**: 인증 키, 개인 식별 정보 로깅 금지
- **구조화 로그**: JSON 형태로 표준화된 로그 메시지

## 7. 운영 & 모니터링 (Operations & Monitoring)

### 7.1. 로깅 정책
- **로그 레벨**: INFO (정상 동작), ERROR (오류 상황), DEBUG (개발용)
- **민감 정보 제외 원칙**: 인증 토큰, 개인정보, 비밀번호 로깅 금지
- **구조화 로그**: 파싱 가능한 JSON 형태 메시지

### 7.2. 성능 메트릭
- **수집 성능**: 프로젝트당 평균 12초 이내 수집 완료
- **처리량**: 동시 5개 프로젝트 병렬 처리 지원
- **오류율**: 5% 미만 유지 목표
- **메트릭 수집**: 
  - `transfer_throughput`: 전송 작업의 평균 데이터 처리량 (바이트/초)
  - `objects_transferred`: 성공적으로 전송된 객체(파일)의 총 개수
  - `objects_failed`: 전송에 실패한 객체의 수

### 7.3. 알림 설정
- **임계치 초과**: API 할당량 80% 도달 시 경고
- **장애 감지**: 연속 3회 수집 실패 시 알림
- **성능 저하**: 수집 시간 30초 초과 시 모니터링

## 8. AI 개발 지시사항 (AI Development Guidelines)

### 8.1. 개발 우선순위
1. **P0**: 기본 Transfer Job 수집 기능 완성
2. **P1**: Transfer Operation 및 성능 메트릭 연계
3. **P2**: 에이전트 풀 및 서비스 계정 정보 수집

### 8.2. 검증 체크리스트
- **정확성**: 실제 GCP 콘솔과 수집 데이터 일치 확인
- **트랜잭션**: 부분 실패 시에도 성공한 데이터 반환 검증
- **보안**: 민감 정보 로깅 방지 및 인증 처리 검증  
- **성능**: 대용량 프로젝트(100+ 전송 작업) 수집 성능 검증
- **에러**: 모든 예외 상황에 대한 적절한 처리 및 복구 검증

### 8.3. 참고 자료
- [Google Cloud Storage Transfer API 문서](https://cloud.google.com/storage-transfer/docs/reference/rest)
- [SpaceONE 플러그인 개발 가이드](https://cloudforet.io/docs/)
- [현재 구현 소스 코드](../../../../src/spaceone/inventory/)

---

## 부록: 현재 구현 상태 (Implementation Status)

### A.1. 구현 완료 기능
- ✅ **StorageTransferConnector**: Google Cloud Storage Transfer API 연동, Service Account 인증
- ✅ **다중 매니저 구조**: TransferJob, TransferOperation, AgentPool 별도 매니저
- ✅ **전체 리소스 조회**: 서비스 계정, 에이전트 풀, 전송 작업, 작업 실행 내역 수집
- ✅ **데이터 모델**: TransferJob, TransferOperation, AgentPool, ServiceAccount 완전한 모델
- ✅ **메타데이터**: SpaceONE 콘솔 UI 레이아웃, 위젯

### A.2. 주요 구현 특징
- **전체 리소스 조회**: 프로젝트를 기준으로 관련된 모든 하위 리소스를 수집
- **작업별 실행 내역**: 각 전송 작업에 대해 상세 실행 기록을 수집하여 성능 추적
- **SpaceONE 모델 변환**: 수집된 모든 원시 데이터를 SpaceONE Cloud Service 모델 형식으로 변환
- **동적 UI 레이아웃**: 사용자가 수집된 리소스 정보를 쉽게 파악할 수 있는 UI 제공

### A.3. 수집 플로우
1. **서비스 계정 조회**: `googleServiceAccounts.get` API 호출
2. **에이전트 풀 조회**: `projects.agentPools.list` API 호출
3. **전송 작업 조회**: `transferJobs.list` API 호출
4. **작업별 실행 내역**: 각 전송 작업에 대해 `transferOperations.list` API 호출
5. **리소스별 응답 생성**: 각 리소스 타입별로 별도의 Response 객체 생성

### A.4. 파일 구조
```
src/spaceone/inventory/
├── connector/storage_transfer/
│   ├── __init__.py
│   └── storage_transfer_v1.py             # Google Cloud Storage Transfer API 연동
├── manager/storage_transfer/
│   ├── __init__.py
│   ├── transfer_job_manager.py     # 전송 작업 비즈니스 로직
│   ├── transfer_operation_manager.py # 전송 작업 실행 비즈니스 로직
│   ├── agent_pool_manager.py       # 에이전트 풀 비즈니스 로직
│   └── service_account_manager.py  # 서비스 계정 비즈니스 로직
├── model/storage_transfer/
│   ├── transfer_job/               # 전송 작업 모델
│   ├── transfer_operation/         # 전송 작업 실행 모델
│   ├── agent_pool/                 # 에이전트 풀 모델
│   └── service_account/            # 서비스 계정 모델
└── service/
    └── collector_service.py        # 플러그인 엔트리포인트
```

### A.5. 기술 스택
- **언어**: Python 3.8+
- **프레임워크**: SpaceONE Core 2.0+, SpaceONE Inventory, Schematics
- **Google Cloud SDK**: 
  - google-oauth2 (Service Account 인증)
  - googleapiclient (Discovery API 클라이언트)
- **테스트**: unittest, unittest.mock (Google Cloud API 모킹)
- **품질 관리**: ruff (린팅/포맷팅), pytest-cov (커버리지)
