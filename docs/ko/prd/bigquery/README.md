# Google BigQuery 인벤토리 수집 제품 요구사항 정의서 (PRD)

## 1. 비즈니스 요구사항 (Business Requirements)

### 1.1. 목적 (Purpose)
SpaceONE 인벤토리 플랫폼에서 Google BigQuery 리소스를 자동으로 수집, 분류, 모니터링하여 데이터 웨어하우스 관리 효율성을 극대화합니다. 데이터 엔지니어링팀과 분석팀이 BigQuery 데이터셋, 테이블, 작업 등의 상태와 비용을 통합적으로 관리할 수 있도록 지원합니다.

### 1.2. 사용자 스토리 (User Stories)
- **데이터 엔지니어**: 모든 프로젝트의 BigQuery 데이터셋과 테이블 현황을 한눈에 파악하고 스토리지 및 쿼리 비용 최적화 포인트를 식별
- **데이터 분석가**: 사용 중인 데이터셋과 테이블의 스키마 및 메타데이터를 모니터링하여 데이터 품질 관리
- **팀 리더**: 팀별 BigQuery 리소스 사용량과 쿼리 비용을 추적하여 예산 관리 최적화

### 1.3. 수용 기준 (Acceptance Criteria)
**P0 (필수)**:
- 모든 BigQuery 데이터셋 정보 수집 (100% 정확도)
- 데이터셋별 테이블, 뷰, 루틴 정보 연계
- 테이블 스키마 및 메타데이터 수집

**P1 (중요)**:
- 작업(Job) 실행 내역 및 통계 정보
- 접근 제어 및 보안 설정 정보
- 다중 프로젝트 병렬 수집

**P2 (선택)**:
- 쿼리 성능 메트릭 연계
- 데이터 사용량 분석

## 2. API 인터페이스 (API Interface)

### 2.1. 수집 엔드포인트 (Collection Endpoints)

#### 2.1.1. BigQuery 리소스 수집 API
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
      "dataset_filter": "optional array"
    }
  }
  ```

## 3. 데이터 & 아키텍처 (Data & Architecture)

### 3.1. 데이터 모델 (Data Models)

#### 3.1.1. 주요 엔터티
- **BigQueryDataset**: 데이터셋 메인 엔터티
  - `dataset_id`: 데이터셋 식별자
  - `friendly_name`: 친숙한 이름
  - `description`: 설명
  - `location`: 위치
  - `default_table_expiration_ms`: 기본 테이블 만료 시간
  - `default_partition_expiration_ms`: 기본 파티션 만료 시간
  - `labels`: 라벨 정보
  - `access`: 접근 제어 목록
  - `creation_time`: 생성 시간
  - `last_modified_time`: 마지막 수정 시간

- **BigQueryTable**: 테이블 엔터티
  - `table_id`: 테이블 식별자
  - `friendly_name`: 친숙한 이름
  - `description`: 설명
  - `type`: 테이블 타입 (TABLE, VIEW, EXTERNAL)
  - `schema`: 테이블 스키마
  - `num_bytes`: 바이트 수
  - `num_long_term_bytes`: 장기 저장 바이트 수
  - `num_rows`: 행 수
  - `creation_time`: 생성 시간
  - `expiration_time`: 만료 시간
  - `last_modified_time`: 마지막 수정 시간

- **TableSchema**: 테이블 스키마 정보
  - `fields`: 필드 목록
    - `name`: 필드 이름
    - `type`: 데이터 타입
    - `mode`: 모드 (NULLABLE, REQUIRED, REPEATED)
    - `description`: 필드 설명
    - `fields`: 중첩 필드 (RECORD 타입의 경우)

- **BigQueryJob**: 작업 엔터티
  - `job_id`: 작업 식별자
  - `state`: 작업 상태 (PENDING, RUNNING, DONE)
  - `configuration`: 작업 구성
  - `statistics`: 작업 통계
  - `status`: 작업 상태 정보
  - `user_email`: 사용자 이메일
  - `creation_time`: 생성 시간
  - `start_time`: 시작 시간
  - `end_time`: 종료 시간

## 4. 비즈니스 로직 플로우 (Business Logic Flow)

### 4.1. 정상 플로우
1. **인증 검증**: Service Account 크리덴셜 유효성 확인
2. **데이터셋 목록 조회**: 프로젝트 내 모든 BigQuery 데이터셋 수집
3. **데이터셋 상세 정보 수집**: 각 데이터셋의 메타데이터, 접근 제어 정보 수집
4. **테이블 목록 수집**: 각 데이터셋의 테이블, 뷰, 루틴 목록 수집
5. **테이블 상세 정보 수집**: 각 테이블의 스키마, 통계 정보 수집
6. **작업 내역 수집**: 최근 실행된 BigQuery 작업 정보 수집 (선택적)
7. **데이터 변환**: SpaceONE 표준 모델로 변환
8. **응답 생성**: 각 리소스 타입별 Response 객체 생성

### 4.2. 예외 플로우
- **인증 실패**: 즉시 실패 반환, 재시도 없음
- **API 할당량 초과**: 지수 백오프로 재시도 (최대 3회)
- **네트워크 오류**: 연결 실패, 타임아웃에 대한 재시도 로직
- **개별 데이터셋 실패**: 로그 기록 후 다음 데이터셋 진행
- **데이터 파싱 실패**: 에러 응답 생성, 수집 계속

## 5. 외부 연동 (External Integration)

### 5.1. Google BigQuery API
- **의존 서비스**: Google BigQuery API v2
- **엔드포인트**: `https://bigquery.googleapis.com`
- **인증 방식**: Service Account 키 파일 기반 OAuth 2.0
- **API 할당량**: 프로젝트당 분당 1000 요청
- **장애 대응**: 
  - HTTP 429 (할당량 초과): 지수 백오프 재시도
  - HTTP 404 (리소스 없음): 정상 처리 (빈 결과 반환)
  - 기타 HTTP 오류: 로그 기록 후 다음 리소스 진행

## 6. 보안 & 컴플라이언스 (Security & Compliance)

### 6.1. 인증 및 인가
- **Google Cloud 인증**: Service Account 키 파일 기반 OAuth 2.0
- **필수 IAM 권한**:
  - `bigquery.datasets.get`
  - `bigquery.tables.list`
  - `bigquery.tables.get`
  - `bigquery.jobs.list`
  - `bigquery.routines.list`
- **권한 범위**: 프로젝트 수준 읽기 전용 권한

## 7. 운영 & 모니터링 (Operations & Monitoring)

### 7.1. 성능 메트릭
- **수집 성능**: 프로젝트당 평균 20초 이내 수집 완료
- **처리량**: 동시 3개 프로젝트 병렬 처리 지원
- **오류율**: 5% 미만 유지 목표
- **메트릭 수집**: 
  - `dataset_count`: 프로젝트별 데이터셋 개수
  - `table_count`: 총 테이블 개수
  - `total_bytes`: 총 저장 용량 (바이트)

## 8. 현재 구현 상태 (Implementation Status)

### 8.1. 구현 완료 기능
- ✅ **SQLWorkspaceManager**: BigQuery 데이터셋 및 테이블 수집
- ✅ **데이터셋 정보 수집**: 메타데이터, 접근 제어, 라벨 정보
- ✅ **테이블 정보 수집**: 스키마, 통계, 파티션 정보
- ✅ **뷰 및 루틴 수집**: 뷰 정의 및 저장 프로시저 정보
- ✅ **메타데이터**: SpaceONE 콘솔 UI 레이아웃, 위젯

### 8.2. 주요 구현 특징
- **전체 데이터셋 수집**: 프로젝트 내 모든 BigQuery 데이터셋 및 관련 리소스 수집
- **스키마 정보 수집**: 각 테이블의 상세 스키마 및 필드 정보 포함
- **SpaceONE 모델 변환**: 수집된 모든 원시 데이터를 SpaceONE Cloud Service 모델 형식으로 변환
- **동적 UI 레이아웃**: 사용자가 수집된 리소스 정보를 쉽게 파악할 수 있는 UI 제공

### 8.3. 파일 구조
```
src/spaceone/inventory/
├── connector/bigquery/
│   ├── __init__.py
│   └── bigquery_v2.py              # Google BigQuery API 연동
├── manager/bigquery/
│   ├── __init__.py
│   └── sql_workspace_manager.py    # 비즈니스 로직, 데이터 변환
├── model/bigquery/
│   ├── __init__.py
│   ├── data.py                     # BigQueryDataset, BigQueryTable 등 데이터 모델
│   ├── cloud_service.py            # BigQueryResource/Response 모델
│   ├── cloud_service_type.py       # CloudServiceType 정의
│   └── widget/                     # SpaceONE 콘솔 위젯 설정
└── service/
    └── collector_service.py        # 플러그인 엔트리포인트
```

### 8.4. 기술 스택
- **언어**: Python 3.8+
- **프레임워크**: SpaceONE Core 2.0+, SpaceONE Inventory, Schematics
- **Google Cloud SDK**: 
  - google-oauth2 (Service Account 인증)
  - googleapiclient (Discovery API 클라이언트)
  - google-cloud-bigquery (BigQuery 클라이언트)
- **테스트**: unittest, unittest.mock (Google Cloud API 모킹)
- **품질 관리**: ruff (린팅/포맷팅), pytest-cov (커버리지)

## 참고 자료

- [Google BigQuery API 문서](https://cloud.google.com/bigquery/docs/reference/rest)
- [SpaceONE 플러그인 개발 가이드](https://cloudforet.io/docs/)
- [현재 구현 소스 코드](../../../../src/spaceone/inventory/)
