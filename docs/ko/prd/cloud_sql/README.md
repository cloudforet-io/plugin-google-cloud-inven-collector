# Google Cloud SQL 인벤토리 수집 제품 요구사항 정의서 (PRD)

## 1. 비즈니스 요구사항 (Business Requirements)

### 1.1. 목적 (Purpose)
SpaceONE 인벤토리 플랫폼에서 Google Cloud SQL 리소스를 자동으로 수집, 분류, 모니터링하여 관리형 데이터베이스 인프라 관리 효율성을 극대화합니다. 데이터베이스 관리팀과 개발팀이 Cloud SQL 인스턴스, 백업, 사용자 등의 상태와 비용을 통합적으로 관리할 수 있도록 지원합니다.

### 1.2. 사용자 스토리 (User Stories)
- **데이터베이스 관리자**: 모든 프로젝트의 Cloud SQL 인스턴스 현황을 한눈에 파악하고 성능 및 비용 최적화 포인트를 식별
- **개발자**: 애플리케이션에서 사용 중인 데이터베이스 상태를 모니터링하여 성능 이슈를 사전에 감지
- **팀 리더**: 팀별 Cloud SQL 리소스 사용량과 비용을 추적하여 예산 관리 최적화

### 1.3. 수용 기준 (Acceptance Criteria)
**P0 (필수)**:
- 모든 활성 Cloud SQL 인스턴스 정보 수집 (100% 정확도)
- 인스턴스별 백업, 사용자, 데이터베이스 정보 연계
- 실시간 상태 모니터링 (5분 이내 갱신)

**P1 (중요)**:
- 네트워크 및 보안 설정 정보 수집
- SSL 인증서 및 접근 제어 정보
- 다중 프로젝트 병렬 수집

**P2 (선택)**:
- 성능 메트릭 연계
- 예측적 알림 기능

## 2. API 인터페이스 (API Interface)

### 2.1. 수집 엔드포인트 (Collection Endpoints)

#### 2.1.1. Cloud SQL 리소스 수집 API
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
      "region_filter": "optional array"
    }
  }
  ```

## 3. 데이터 & 아키텍처 (Data & Architecture)

### 3.1. 데이터 모델 (Data Models)

#### 3.1.1. 주요 엔터티
- **CloudSQLInstance**: Cloud SQL 인스턴스 메인 엔터티
  - `instance_id`: 인스턴스 식별자
  - `name`: 인스턴스 이름
  - `state`: 인스턴스 상태 (RUNNABLE, SUSPENDED, PENDING_DELETE 등)
  - `database_version`: 데이터베이스 버전 (MYSQL_8_0, POSTGRES_13 등)
  - `region`: 리전
  - `tier`: 머신 타입
  - `settings`: 인스턴스 설정
  - `ip_addresses`: IP 주소 목록
  - `server_ca_cert`: 서버 CA 인증서
  - `backend_type`: 백엔드 타입 (FIRST_GEN, SECOND_GEN)

- **DatabaseSettings**: 데이터베이스 설정 정보
  - `tier`: 머신 타입
  - `pricing_plan`: 가격 계획
  - `replication_type`: 복제 타입
  - `activation_policy`: 활성화 정책
  - `authorized_gae_applications`: 승인된 GAE 애플리케이션
  - `backup_configuration`: 백업 구성
  - `ip_configuration`: IP 구성
  - `location_preference`: 위치 선호도
  - `database_flags`: 데이터베이스 플래그

- **BackupConfiguration**: 백업 구성 정보
  - `enabled`: 백업 활성화 여부
  - `start_time`: 백업 시작 시간
  - `location`: 백업 위치
  - `point_in_time_recovery_enabled`: 특정 시점 복구 활성화 여부
  - `transaction_log_retention_days`: 트랜잭션 로그 보존 일수
  - `backup_retention_settings`: 백업 보존 설정

- **IpConfiguration**: IP 구성 정보
  - `ipv4_enabled`: IPv4 활성화 여부
  - `private_network`: 프라이빗 네트워크
  - `require_ssl`: SSL 필수 여부
  - `authorized_networks`: 승인된 네트워크 목록

## 4. 비즈니스 로직 플로우 (Business Logic Flow)

### 4.1. 정상 플로우
1. **인증 검증**: Service Account 크리덴셜 유효성 확인
2. **Cloud SQL 인스턴스 목록 조회**: 프로젝트 내 모든 Cloud SQL 인스턴스 수집
3. **인스턴스 상세 정보 수집**: 각 인스턴스의 설정, 네트워크, 백업 정보 수집
4. **데이터베이스 목록 수집**: 각 인스턴스의 데이터베이스 목록 수집
5. **사용자 목록 수집**: 각 인스턴스의 사용자 계정 정보 수집
6. **백업 정보 수집**: 각 인스턴스의 백업 목록 및 설정 수집
7. **SSL 인증서 정보 수집**: 서버 및 클라이언트 인증서 정보 수집
8. **데이터 변환**: SpaceONE 표준 모델로 변환
9. **응답 생성**: CloudSQLResponse 객체 생성

### 4.2. 예외 플로우
- **인증 실패**: 즉시 실패 반환, 재시도 없음
- **API 할당량 초과**: 지수 백오프로 재시도 (최대 3회)
- **네트워크 오류**: 연결 실패, 타임아웃에 대한 재시도 로직
- **개별 인스턴스 실패**: 로그 기록 후 다음 인스턴스 진행
- **데이터 파싱 실패**: 에러 응답 생성, 수집 계속

## 5. 외부 연동 (External Integration)

### 5.1. Google Cloud SQL Admin API
- **의존 서비스**: Google Cloud SQL Admin API v1
- **엔드포인트**: `https://sqladmin.googleapis.com`
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
  - `cloudsql.instances.list`
  - `cloudsql.instances.get`
  - `cloudsql.databases.list`
  - `cloudsql.users.list`
  - `cloudsql.backupRuns.list`
  - `cloudsql.sslCerts.list`
- **권한 범위**: 프로젝트 수준 읽기 전용 권한

## 7. 운영 & 모니터링 (Operations & Monitoring)

### 7.1. 성능 메트릭
- **수집 성능**: 프로젝트당 평균 15초 이내 수집 완료
- **처리량**: 동시 5개 프로젝트 병렬 처리 지원
- **오류율**: 5% 미만 유지 목표
- **메트릭 수집**: 
  - `instance_count`: 프로젝트별 Cloud SQL 인스턴스 개수
  - `database_count`: 총 데이터베이스 개수
  - `backup_count`: 총 백업 개수

## 8. 현재 구현 상태 (Implementation Status)

### 8.1. 구현 완료 기능
- ✅ **CloudSQLManager**: Cloud SQL 인스턴스 수집 및 상세 정보
- ✅ **인스턴스 설정 수집**: 머신 타입, 데이터베이스 버전, 네트워크 설정
- ✅ **백업 정보 수집**: 백업 구성 및 백업 실행 내역
- ✅ **보안 정보 수집**: SSL 인증서, IP 구성, 승인된 네트워크
- ✅ **메타데이터**: SpaceONE 콘솔 UI 레이아웃, 위젯

### 8.2. 주요 구현 특징
- **전체 인스턴스 수집**: 프로젝트 내 모든 Cloud SQL 인스턴스 및 관련 리소스 수집
- **상세 설정 정보**: 각 인스턴스의 세부 설정 및 보안 구성 정보 포함
- **SpaceONE 모델 변환**: 수집된 모든 원시 데이터를 SpaceONE Cloud Service 모델 형식으로 변환
- **동적 UI 레이아웃**: 사용자가 수집된 리소스 정보를 쉽게 파악할 수 있는 UI 제공

### 8.3. 파일 구조
```
src/spaceone/inventory/
├── connector/cloud_sql/
│   ├── __init__.py
│   └── cloud_sql_v1.py             # Google Cloud SQL API 연동
├── manager/cloud_sql/
│   ├── __init__.py
│   └── cloud_sql_manager.py        # 비즈니스 로직, 데이터 변환
├── model/cloud_sql/
│   ├── __init__.py
│   ├── data.py                     # CloudSQLInstance, DatabaseSettings 등 데이터 모델
│   ├── cloud_service.py            # CloudSQLResource/Response 모델
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
- **테스트**: unittest, unittest.mock (Google Cloud API 모킹)
- **품질 관리**: ruff (린팅/포맷팅), pytest-cov (커버리지)

## 참고 자료

- [Google Cloud SQL API 문서](https://cloud.google.com/sql/docs/mysql/admin-api)
- [SpaceONE 플러그인 개발 가이드](https://cloudforet.io/docs/)
- [현재 구현 소스 코드](../../../../src/spaceone/inventory/)
