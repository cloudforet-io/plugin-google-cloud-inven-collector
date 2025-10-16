# Google Cloud Storage 인벤토리 수집 제품 요구사항 정의서 (PRD)

## 1. 비즈니스 요구사항 (Business Requirements)

### 1.1. 목적 (Purpose)
SpaceONE 인벤토리 플랫폼에서 Google Cloud Storage 리소스를 자동으로 수집, 분류, 모니터링하여 객체 스토리지 관리 효율성을 극대화합니다. 개발팀과 인프라 관리팀이 Cloud Storage 버킷, 객체, 접근 제어 등의 상태와 비용을 통합적으로 관리할 수 있도록 지원합니다.

### 1.2. 사용자 스토리 (User Stories)
- **인프라 관리자**: 모든 프로젝트의 Cloud Storage 버킷 현황을 한눈에 파악하고 스토리지 비용 최적화 포인트를 식별
- **개발자**: 애플리케이션에서 사용 중인 스토리지 버킷의 상태와 접근 권한을 모니터링하여 보안 이슈를 사전에 감지
- **팀 리더**: 팀별 Cloud Storage 리소스 사용량과 비용을 추적하여 예산 관리 최적화

### 1.3. 수용 기준 (Acceptance Criteria)
**P0 (필수)**:
- 모든 Cloud Storage 버킷 정보 수집 (100% 정확도)
- 버킷별 접근 제어, 암호화, 라이프사이클 정책 정보 연계
- 실시간 상태 모니터링 (5분 이내 갱신)

**P1 (중요)**:
- 버킷 메타데이터 및 라벨 정보 수집
- 버전 관리 및 CORS 설정 정보
- 다중 프로젝트 병렬 수집

**P2 (선택)**:
- 객체 수준 메타데이터 수집
- 스토리지 사용량 분석

## 2. API 인터페이스 (API Interface)

### 2.1. 수집 엔드포인트 (Collection Endpoints)

#### 2.1.1. Cloud Storage 리소스 수집 API
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
      "bucket_filter": "optional array"
    }
  }
  ```

## 3. 데이터 & 아키텍처 (Data & Architecture)

### 3.1. 데이터 모델 (Data Models)

#### 3.1.1. 주요 엔터티
- **CloudStorageBucket**: 버킷 메인 엔터티
  - `bucket_id`: 버킷 식별자
  - `name`: 버킷 이름
  - `location`: 위치 (리전 또는 멀티 리전)
  - `location_type`: 위치 타입 (region, dual-region, multi-region)
  - `storage_class`: 스토리지 클래스 (STANDARD, NEARLINE, COLDLINE, ARCHIVE)
  - `versioning`: 버전 관리 설정
  - `lifecycle`: 라이프사이클 정책
  - `iam_policy`: IAM 정책
  - `acl`: 접근 제어 목록
  - `encryption`: 암호화 설정
  - `cors`: CORS 설정
  - `website`: 웹사이트 설정
  - `logging`: 로깅 설정
  - `labels`: 라벨 정보
  - `creation_time`: 생성 시간
  - `updated_time`: 업데이트 시간

- **BucketVersioning**: 버전 관리 설정
  - `enabled`: 버전 관리 활성화 여부

- **LifecycleConfiguration**: 라이프사이클 정책
  - `rules`: 라이프사이클 규칙 목록
    - `action`: 액션 (Delete, SetStorageClass)
    - `condition`: 조건 (age, createdBefore, matchesStorageClass 등)

- **BucketEncryption**: 암호화 설정
  - `default_kms_key_name`: 기본 KMS 키 이름

- **CorsConfiguration**: CORS 설정
  - `cors_rules`: CORS 규칙 목록
    - `origin`: 허용된 오리진
    - `method`: 허용된 HTTP 메서드
    - `response_header`: 응답 헤더
    - `max_age_seconds`: 최대 캐시 시간

- **WebsiteConfiguration**: 웹사이트 설정
  - `main_page_suffix`: 메인 페이지 접미사
  - `not_found_page`: 404 페이지

- **LoggingConfiguration**: 로깅 설정
  - `log_bucket`: 로그 버킷
  - `log_object_prefix`: 로그 객체 접두사

## 4. 비즈니스 로직 플로우 (Business Logic Flow)

### 4.1. 정상 플로우
1. **인증 검증**: Service Account 크리덴셜 유효성 확인
2. **버킷 목록 조회**: 프로젝트 내 모든 Cloud Storage 버킷 수집
3. **버킷 상세 정보 수집**: 각 버킷의 메타데이터, 설정 정보 수집
4. **접근 제어 정보 수집**: IAM 정책 및 ACL 정보 수집
5. **암호화 설정 수집**: 기본 암호화 및 KMS 키 정보 수집
6. **라이프사이클 정책 수집**: 객체 생명주기 관리 정책 수집
7. **CORS 및 웹사이트 설정 수집**: 웹 관련 설정 정보 수집
8. **로깅 설정 수집**: 액세스 로그 설정 정보 수집
9. **데이터 변환**: SpaceONE 표준 모델로 변환
10. **응답 생성**: CloudStorageResponse 객체 생성

### 4.2. 예외 플로우
- **인증 실패**: 즉시 실패 반환, 재시도 없음
- **API 할당량 초과**: 지수 백오프로 재시도 (최대 3회)
- **네트워크 오류**: 연결 실패, 타임아웃에 대한 재시도 로직
- **개별 버킷 실패**: 로그 기록 후 다음 버킷 진행
- **데이터 파싱 실패**: 에러 응답 생성, 수집 계속

## 5. 외부 연동 (External Integration)

### 5.1. Google Cloud Storage API
- **의존 서비스**: Google Cloud Storage JSON API v1
- **엔드포인트**: `https://storage.googleapis.com`
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
  - `storage.buckets.list`
  - `storage.buckets.get`
  - `storage.buckets.getIamPolicy`
  - `storage.objects.list` (선택적)
- **권한 범위**: 프로젝트 수준 읽기 전용 권한

## 7. 운영 & 모니터링 (Operations & Monitoring)

### 7.1. 성능 메트릭
- **수집 성능**: 프로젝트당 평균 10초 이내 수집 완료
- **처리량**: 동시 10개 프로젝트 병렬 처리 지원
- **오류율**: 5% 미만 유지 목표
- **메트릭 수집**: 
  - `bucket_count`: 프로젝트별 버킷 개수
  - `total_size_bytes`: 총 스토리지 사용량 (바이트)
  - `object_count`: 총 객체 개수

## 8. 현재 구현 상태 (Implementation Status)

### 8.1. 구현 완료 기능
- ✅ **StorageManager**: Cloud Storage 버킷 수집 및 상세 정보
- ✅ **버킷 설정 수집**: 스토리지 클래스, 위치, 버전 관리 설정
- ✅ **보안 정보 수집**: IAM 정책, ACL, 암호화 설정
- ✅ **정책 정보 수집**: 라이프사이클 정책, CORS 설정
- ✅ **메타데이터**: SpaceONE 콘솔 UI 레이아웃, 위젯

### 8.2. 주요 구현 특징
- **전체 버킷 수집**: 프로젝트 내 모든 Cloud Storage 버킷 및 관련 설정 수집
- **상세 설정 정보**: 각 버킷의 세부 설정 및 보안 구성 정보 포함
- **SpaceONE 모델 변환**: 수집된 모든 원시 데이터를 SpaceONE Cloud Service 모델 형식으로 변환
- **동적 UI 레이아웃**: 사용자가 수집된 리소스 정보를 쉽게 파악할 수 있는 UI 제공

### 8.3. 파일 구조
```
src/spaceone/inventory/
├── connector/cloud_storage/
│   ├── __init__.py
│   └── storage_v1.py               # Google Cloud Storage API 연동
├── manager/cloud_storage/
│   ├── __init__.py
│   └── storage_manager.py          # 비즈니스 로직, 데이터 변환
├── model/cloud_storage/
│   ├── __init__.py
│   ├── data.py                     # CloudStorageBucket 등 데이터 모델
│   ├── cloud_service.py            # CloudStorageResource/Response 모델
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
  - google-cloud-storage (Storage 클라이언트)
- **테스트**: unittest, unittest.mock (Google Cloud API 모킹)
- **품질 관리**: ruff (린팅/포맷팅), pytest-cov (커버리지)

## 참고 자료

- [Google Cloud Storage API 문서](https://cloud.google.com/storage/docs/json_api)
- [SpaceONE 플러그인 개발 가이드](https://cloudforet.io/docs/)
- [현재 구현 소스 코드](../../../../src/spaceone/inventory/)
