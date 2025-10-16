# Google Cloud Functions 인벤토리 수집 제품 요구사항 정의서 (PRD)

## 1. 비즈니스 요구사항 (Business Requirements)

### 1.1. 목적 (Purpose)
SpaceONE 인벤토리 플랫폼에서 Google Cloud Functions 리소스를 자동으로 수집, 분류, 모니터링하여 서버리스 함수 관리 효율성을 극대화합니다. 개발팀과 DevOps팀이 Cloud Functions(1세대, 2세대) 함수의 상태, 성능, 비용을 통합적으로 관리할 수 있도록 지원합니다.

### 1.2. 사용자 스토리 (User Stories)
- **개발자**: 모든 프로젝트의 Cloud Functions 현황을 한눈에 파악하고 함수별 성능 및 비용을 최적화
- **DevOps 엔지니어**: 함수의 트리거 설정과 실행 환경을 모니터링하여 운영 효율성을 향상
- **팀 리더**: 팀별 Cloud Functions 사용량과 실행 비용을 추적하여 예산 관리 최적화

### 1.3. 수용 기준 (Acceptance Criteria)
**P0 (필수)**:
- 모든 Cloud Functions (1세대, 2세대) 정보 수집 (100% 정확도)
- 함수별 트리거, 환경 변수, 런타임 설정 정보 연계
- 실시간 상태 모니터링 (5분 이내 갱신)

**P1 (중요)**:
- 함수 소스 코드 위치 및 배포 정보
- 보안 설정 및 IAM 권한 정보
- 다중 프로젝트 및 리전 병렬 수집

**P2 (선택)**:
- 함수 실행 성능 메트릭 연계
- 비용 분석 및 최적화 권장사항

## 2. API 인터페이스 (API Interface)

### 2.1. 수집 엔드포인트 (Collection Endpoints)

#### 2.1.1. Cloud Functions 리소스 수집 API
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
- **CloudFunction**: Cloud Functions 메인 엔터티
  - `function_id`: 함수 식별자
  - `name`: 함수 이름
  - `description`: 설명
  - `status`: 함수 상태 (ACTIVE, OFFLINE, DEPLOY_IN_PROGRESS 등)
  - `entry_point`: 진입점
  - `runtime`: 런타임 (python39, nodejs16, go119 등)
  - `timeout`: 타임아웃 설정
  - `available_memory_mb`: 사용 가능한 메모리 (MB)
  - `service_account_email`: 서비스 계정 이메일
  - `update_time`: 업데이트 시간
  - `version_id`: 버전 ID
  - `labels`: 라벨 정보
  - `environment_variables`: 환경 변수
  - `build_environment_variables`: 빌드 환경 변수
  - `network`: 네트워크 설정
  - `max_instances`: 최대 인스턴스 수
  - `min_instances`: 최소 인스턴스 수
  - `vpc_connector`: VPC 커넥터
  - `vpc_connector_egress_settings`: VPC 커넥터 이그레스 설정
  - `ingress_settings`: 인그레스 설정
  - `kms_key_name`: KMS 키 이름
  - `build_worker_pool`: 빌드 워커 풀
  - `build_id`: 빌드 ID
  - `source_archive_url`: 소스 아카이브 URL
  - `source_repository`: 소스 저장소
  - `source_upload_url`: 소스 업로드 URL

- **EventTrigger**: 이벤트 트리거 정보 (1세대)
  - `event_type`: 이벤트 타입
  - `resource`: 리소스
  - `service`: 서비스
  - `failure_policy`: 실패 정책

- **HttpsTrigger**: HTTPS 트리거 정보 (1세대)
  - `url`: 트리거 URL
  - `security_level`: 보안 레벨

- **Gen2EventTrigger**: 이벤트 트리거 정보 (2세대)
  - `trigger`: 트리거 설정
  - `event_type`: 이벤트 타입
  - `event_filters`: 이벤트 필터
  - `pubsub_topic`: Pub/Sub 토픽
  - `service_account_email`: 서비스 계정 이메일

- **SourceRepository**: 소스 저장소 정보
  - `url`: 저장소 URL
  - `deployed_url`: 배포된 URL

- **SecretEnvironmentVariable**: 시크릿 환경 변수
  - `key`: 키
  - `project_id`: 프로젝트 ID
  - `secret`: 시크릿 이름
  - `version`: 버전

- **SecretVolume**: 시크릿 볼륨
  - `mount_path`: 마운트 경로
  - `project_id`: 프로젝트 ID
  - `secret`: 시크릿 이름
  - `versions`: 버전 목록

## 4. 비즈니스 로직 플로우 (Business Logic Flow)

### 4.1. 정상 플로우
1. **인증 검증**: Service Account 크리덴셜 유효성 확인
2. **리전 목록 조회**: 사용 가능한 리전 목록 수집
3. **1세대 함수 수집**: 각 리전별 Cloud Functions 1세대 함수 목록 및 상세 정보 수집
4. **2세대 함수 수집**: 각 리전별 Cloud Functions 2세대 함수 목록 및 상세 정보 수집
5. **트리거 정보 수집**: 각 함수의 트리거 설정 (HTTP, 이벤트) 정보 수집
6. **환경 설정 수집**: 환경 변수, 런타임 설정, 네트워크 구성 수집
7. **보안 설정 수집**: IAM 권한, KMS 키, VPC 설정 수집
8. **데이터 변환**: SpaceONE 표준 모델로 변환
9. **응답 생성**: 각 세대별 Response 객체 생성

### 4.2. 예외 플로우
- **인증 실패**: 즉시 실패 반환, 재시도 없음
- **API 할당량 초과**: 지수 백오프로 재시도 (최대 3회)
- **네트워크 오류**: 연결 실패, 타임아웃에 대한 재시도 로직
- **개별 함수 실패**: 로그 기록 후 다음 함수 진행
- **데이터 파싱 실패**: 에러 응답 생성, 수집 계속

## 5. 외부 연동 (External Integration)

### 5.1. Google Cloud Functions API
- **의존 서비스**: 
  - Google Cloud Functions API v1 (1세대)
  - Google Cloud Functions API v2 (2세대)
- **엔드포인트**: 
  - `https://cloudfunctions.googleapis.com` (v1)
  - `https://cloudfunctions.googleapis.com` (v2)
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
  - `cloudfunctions.functions.list`
  - `cloudfunctions.functions.get`
  - `cloudfunctions.functions.getIamPolicy`
  - `cloudfunctions.locations.list`
- **권한 범위**: 프로젝트 수준 읽기 전용 권한

## 7. 운영 & 모니터링 (Operations & Monitoring)

### 7.1. 성능 메트릭
- **수집 성능**: 프로젝트당 평균 20초 이내 수집 완료
- **처리량**: 동시 5개 프로젝트 병렬 처리 지원
- **오류율**: 5% 미만 유지 목표
- **메트릭 수집**: 
  - `function_gen1_count`: 프로젝트별 1세대 함수 개수
  - `function_gen2_count`: 프로젝트별 2세대 함수 개수
  - `total_memory_mb`: 총 할당된 메모리 (MB)

## 8. 현재 구현 상태 (Implementation Status)

### 8.1. 구현 완료 기능
- ✅ **FunctionGen1Manager**: Cloud Functions 1세대 함수 수집 및 상세 정보
- ✅ **FunctionGen2Manager**: Cloud Functions 2세대 함수 수집 및 상세 정보
- ✅ **트리거 정보 수집**: HTTP 트리거, 이벤트 트리거 설정 정보
- ✅ **환경 설정 수집**: 런타임, 환경 변수, 네트워크 설정
- ✅ **보안 설정 수집**: IAM 권한, KMS 키, VPC 설정
- ✅ **메타데이터**: SpaceONE 콘솔 UI 레이아웃, 위젯

### 8.2. 주요 구현 특징
- **1세대/2세대 분리 수집**: 각 세대별 API 및 데이터 모델 완전 분리
- **상세 설정 정보**: 각 함수의 세부 설정 및 보안 구성 정보 포함
- **SpaceONE 모델 변환**: 수집된 모든 원시 데이터를 SpaceONE Cloud Service 모델 형식으로 변환
- **동적 UI 레이아웃**: 사용자가 수집된 리소스 정보를 쉽게 파악할 수 있는 UI 제공

### 8.3. 파일 구조
```
src/spaceone/inventory/
├── connector/cloud_functions/
│   ├── __init__.py
│   ├── cloud_functions_v1.py       # Google Cloud Functions API v1 연동
│   └── cloud_functions_v2.py       # Google Cloud Functions API v2 연동
├── manager/cloud_functions/
│   ├── __init__.py
│   ├── function_gen1_manager.py    # 1세대 함수 비즈니스 로직
│   └── function_gen2_manager.py    # 2세대 함수 비즈니스 로직
├── model/cloud_functions/
│   ├── function_gen1/              # 1세대 함수 모델
│   └── function_gen2/              # 2세대 함수 모델
└── service/
    └── collector_service.py        # 플러그인 엔트리포인트
```

### 8.4. 기술 스택
- **언어**: Python 3.8+
- **프레임워크**: SpaceONE Core 2.0+, SpaceONE Inventory, Schematics
- **Google Cloud SDK**: 
  - google-oauth2 (Service Account 인증)
  - googleapiclient (Discovery API 클라이언트)
  - google-cloud-functions (Functions 클라이언트)
- **테스트**: unittest, unittest.mock (Google Cloud API 모킹)
- **품질 관리**: ruff (린팅/포맷팅), pytest-cov (커버리지)

## 참고 자료

- [Google Cloud Functions API v1 문서](https://cloud.google.com/functions/docs/reference/rest/v1)
- [Google Cloud Functions API v2 문서](https://cloud.google.com/functions/docs/reference/rest/v2)
- [SpaceONE 플러그인 개발 가이드](https://cloudforet.io/docs/)
- [현재 구현 소스 코드](../../../../src/spaceone/inventory/)
