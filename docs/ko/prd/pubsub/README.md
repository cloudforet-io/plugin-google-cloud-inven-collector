# Google Cloud Pub/Sub 인벤토리 수집 제품 요구사항 정의서 (PRD)

## 1. 비즈니스 요구사항 (Business Requirements)

### 1.1. 목적 (Purpose)
SpaceONE 인벤토리 플랫폼에서 Google Cloud Pub/Sub 리소스를 자동으로 수집, 분류, 모니터링하여 메시징 인프라 관리 효율성을 극대화합니다. 개발팀과 아키텍처팀이 Pub/Sub 토픽, 구독, 스키마 등의 상태와 구성을 통합적으로 관리할 수 있도록 지원합니다.

### 1.2. 사용자 스토리 (User Stories)
- **개발자**: 모든 프로젝트의 Pub/Sub 토픽과 구독 현황을 한눈에 파악하고 메시지 처리 성능을 최적화
- **아키텍처 엔지니어**: 메시징 토폴로지와 스키마 관리를 통해 시스템 간 데이터 흐름을 모니터링
- **팀 리더**: 팀별 Pub/Sub 리소스 사용량과 비용을 추적하여 예산 관리 최적화

### 1.3. 수용 기준 (Acceptance Criteria)
**P0 (필수)**:
- 모든 Pub/Sub 토픽 및 구독 정보 수집 (100% 정확도)
- 토픽별 구독 목록 및 설정 정보 연계
- 스키마 및 스냅샷 정보 수집

**P1 (중요)**:
- 메시지 보존 정책 및 필터링 설정
- 접근 제어 및 보안 설정 정보
- 다중 프로젝트 병렬 수집

**P2 (선택)**:
- 메시지 처리 성능 메트릭 연계
- 메시지 흐름 시각화

## 2. API 인터페이스 (API Interface)

### 2.1. 수집 엔드포인트 (Collection Endpoints)

#### 2.1.1. Pub/Sub 리소스 수집 API
- **경로**: Internal API (플러그인 인터페이스)
- **메서드**: `collect_cloud_service()`
- **인증**: Google Cloud Service Account 키 기반
- **Rate Limit**: Google Cloud API 할당량 (분당 1200 요청)
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
      "topic_filter": "optional array"
    }
  }
  ```

## 3. 데이터 & 아키텍처 (Data & Architecture)

### 3.1. 데이터 모델 (Data Models)

#### 3.1.1. 주요 엔터티
- **PubSubTopic**: 토픽 메인 엔터티
  - `topic_id`: 토픽 식별자
  - `name`: 토픽 이름
  - `labels`: 라벨 정보
  - `message_retention_duration`: 메시지 보존 기간
  - `kms_key_name`: KMS 키 이름
  - `schema_settings`: 스키마 설정
  - `message_storage_policy`: 메시지 저장 정책
  - `satisfies_pzs`: PZS(Physical Zone Separation) 만족 여부

- **PubSubSubscription**: 구독 엔터티
  - `subscription_id`: 구독 식별자
  - `name`: 구독 이름
  - `topic`: 연결된 토픽
  - `push_config`: 푸시 구성
  - `ack_deadline_seconds`: 확인 마감 시간
  - `retain_acked_messages`: 확인된 메시지 보존 여부
  - `message_retention_duration`: 메시지 보존 기간
  - `labels`: 라벨 정보
  - `enable_message_ordering`: 메시지 순서 보장 여부
  - `expiration_policy`: 만료 정책
  - `filter`: 메시지 필터
  - `dead_letter_policy`: 데드 레터 정책
  - `retry_policy`: 재시도 정책

- **PubSubSchema**: 스키마 엔터티
  - `schema_id`: 스키마 식별자
  - `name`: 스키마 이름
  - `type`: 스키마 타입 (AVRO, PROTOCOL_BUFFER)
  - `definition`: 스키마 정의
  - `revision_id`: 리비전 ID
  - `revision_create_time`: 리비전 생성 시간

- **PubSubSnapshot**: 스냅샷 엔터티
  - `snapshot_id`: 스냅샷 식별자
  - `name`: 스냅샷 이름
  - `topic`: 연결된 토픽
  - `expire_time`: 만료 시간
  - `labels`: 라벨 정보

- **PushConfig**: 푸시 구성 정보
  - `push_endpoint`: 푸시 엔드포인트
  - `attributes`: 속성
  - `oidc_token`: OIDC 토큰 설정
  - `pubsub_wrapper`: Pub/Sub 래퍼 설정

- **DeadLetterPolicy**: 데드 레터 정책
  - `dead_letter_topic`: 데드 레터 토픽
  - `max_delivery_attempts`: 최대 전달 시도 횟수

- **RetryPolicy**: 재시도 정책
  - `minimum_backoff`: 최소 백오프 시간
  - `maximum_backoff`: 최대 백오프 시간

## 4. 비즈니스 로직 플로우 (Business Logic Flow)

### 4.1. 정상 플로우
1. **인증 검증**: Service Account 크리덴셜 유효성 확인
2. **토픽 목록 수집**: 프로젝트 내 모든 Pub/Sub 토픽 목록 및 상세 정보 수집
3. **구독 목록 수집**: 각 토픽별 구독 목록 및 설정 정보 수집
4. **스키마 정보 수집**: 프로젝트 내 모든 스키마 및 리비전 정보 수집
5. **스냅샷 정보 수집**: 프로젝트 내 모든 스냅샷 정보 수집
6. **토픽-구독 관계 매핑**: 토픽과 구독 간의 관계 정보 구성
7. **데이터 변환**: SpaceONE 표준 모델로 변환
8. **응답 생성**: 각 리소스 타입별 Response 객체 생성

### 4.2. 예외 플로우
- **인증 실패**: 즉시 실패 반환, 재시도 없음
- **API 할당량 초과**: 지수 백오프로 재시도 (최대 3회)
- **네트워크 오류**: 연결 실패, 타임아웃에 대한 재시도 로직
- **개별 리소스 실패**: 로그 기록 후 다음 리소스 진행
- **데이터 파싱 실패**: 에러 응답 생성, 수집 계속

## 5. 외부 연동 (External Integration)

### 5.1. Google Cloud Pub/Sub API
- **의존 서비스**: Google Cloud Pub/Sub API v1
- **엔드포인트**: `https://pubsub.googleapis.com`
- **인증 방식**: Service Account 키 파일 기반 OAuth 2.0
- **API 할당량**: 프로젝트당 분당 1200 요청
- **장애 대응**: 
  - HTTP 429 (할당량 초과): 지수 백오프 재시도
  - HTTP 404 (리소스 없음): 정상 처리 (빈 결과 반환)
  - 기타 HTTP 오류: 로그 기록 후 다음 리소스 진행

## 6. 보안 & 컴플라이언스 (Security & Compliance)

### 6.1. 인증 및 인가
- **Google Cloud 인증**: Service Account 키 파일 기반 OAuth 2.0
- **필수 IAM 권한**:
  - `pubsub.topics.list`
  - `pubsub.topics.get`
  - `pubsub.subscriptions.list`
  - `pubsub.subscriptions.get`
  - `pubsub.schemas.list`
  - `pubsub.schemas.get`
  - `pubsub.snapshots.list`
- **권한 범위**: 프로젝트 수준 읽기 전용 권한

## 7. 운영 & 모니터링 (Operations & Monitoring)

### 7.1. 성능 메트릭
- **수집 성능**: 프로젝트당 평균 15초 이내 수집 완료
- **처리량**: 동시 5개 프로젝트 병렬 처리 지원
- **오류율**: 5% 미만 유지 목표
- **메트릭 수집**: 
  - `topic_count`: 프로젝트별 토픽 개수
  - `subscription_count`: 총 구독 개수
  - `schema_count`: 총 스키마 개수
  - `snapshot_count`: 총 스냅샷 개수

## 8. 현재 구현 상태 (Implementation Status)

### 8.1. 구현 완료 기능
- ✅ **TopicManager**: Pub/Sub 토픽 수집 및 상세 정보
- ✅ **SubscriptionManager**: 구독 정보 수집 및 설정
- ✅ **SchemaManager**: 스키마 정보 수집 및 리비전 관리
- ✅ **SnapshotManager**: 스냅샷 정보 수집
- ✅ **관계형 데이터 연계**: 토픽-구독 간의 관계 정보 포함
- ✅ **메타데이터**: SpaceONE 콘솔 UI 레이아웃, 위젯

### 8.2. 주요 구현 특징
- **전체 메시징 토폴로지 수집**: 프로젝트 내 모든 Pub/Sub 리소스 및 관계 정보 수집
- **상세 설정 정보**: 각 토픽과 구독의 세부 설정 및 정책 정보 포함
- **SpaceONE 모델 변환**: 수집된 모든 원시 데이터를 SpaceONE Cloud Service 모델 형식으로 변환
- **동적 UI 레이아웃**: 사용자가 수집된 리소스 정보를 쉽게 파악할 수 있는 UI 제공

### 8.3. 파일 구조
```
src/spaceone/inventory/
├── connector/pubsub/
│   ├── __init__.py
│   └── pubsub_v1.py                # Google Cloud Pub/Sub API 연동
├── manager/pubsub/
│   ├── __init__.py
│   ├── topic_manager.py            # 토픽 비즈니스 로직
│   ├── subscription_manager.py     # 구독 비즈니스 로직
│   ├── schema_manager.py           # 스키마 비즈니스 로직
│   └── snapshot_manager.py         # 스냅샷 비즈니스 로직
├── model/pubsub/
│   ├── topic/                      # 토픽 모델
│   ├── subscription/               # 구독 모델
│   ├── schema/                     # 스키마 모델
│   └── snapshot/                   # 스냅샷 모델
└── service/
    └── collector_service.py        # 플러그인 엔트리포인트
```

### 8.4. 기술 스택
- **언어**: Python 3.8+
- **프레임워크**: SpaceONE Core 2.0+, SpaceONE Inventory, Schematics
- **Google Cloud SDK**: 
  - google-oauth2 (Service Account 인증)
  - googleapiclient (Discovery API 클라이언트)
  - google-cloud-pubsub (Pub/Sub 클라이언트)
- **테스트**: unittest, unittest.mock (Google Cloud API 모킹)
- **품질 관리**: ruff (린팅/포맷팅), pytest-cov (커버리지)

## 참고 자료

- [Google Cloud Pub/Sub API 문서](https://cloud.google.com/pubsub/docs/reference/rest)
- [SpaceONE 플러그인 개발 가이드](https://cloudforet.io/docs/)
- [현재 구현 소스 코드](../../../../src/spaceone/inventory/)
