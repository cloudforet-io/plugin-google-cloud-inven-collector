# Google Cloud Firestore 인벤토리 수집 제품 요구사항 정의서 (PRD)

## 1. 비즈니스 요구사항 (Business Requirements)

### 1.1. 목적 (Purpose)
SpaceONE 인벤토리 플랫폼에서 Google Cloud Firestore 리소스를 자동으로 수집, 분류, 모니터링하여 NoSQL 문서 데이터베이스 관리 효율성을 극대화합니다. 개발팀과 데이터베이스 관리팀이 Firestore 데이터베이스, 컬렉션, 문서, 인덱스의 상태와 구조를 통합적으로 관리할 수 있도록 지원합니다.

### 1.2. 사용자 스토리 (User Stories)
- **데이터베이스 관리자**: 모든 프로젝트의 Firestore 데이터베이스 현황을 한눈에 파악하고 컬렉션 구조 및 인덱스 최적화 포인트를 식별
- **개발자**: 애플리케이션에서 사용 중인 Firestore 스키마와 문서 구조를 모니터링하여 성능 이슈를 사전에 감지
- **팀 리더**: 팀별 Firestore 리소스 사용량과 데이터 구조를 추적하여 데이터 아키텍처 최적화

### 1.3. 수용 기준 (Acceptance Criteria)
**P0 (필수)**:
- 모든 FIRESTORE_NATIVE 데이터베이스 정보 수집 (100% 정확도)
- 데이터베이스별 컬렉션, 문서, 인덱스 정보 연계
- 재귀적 문서 탐색을 통한 전체 문서 구조 수집

**P1 (중요)**:
- 다중 API 활용 (Admin API, Document API)
- 컬렉션별 문서 메타데이터 수집
- 복합 인덱스 정보 수집

**P2 (선택)**:
- 성능 메트릭 연계
- 문서 사용량 분석

## 2. API 인터페이스 (API Interface)

### 2.1. 수집 엔드포인트 (Collection Endpoints)

#### 2.1.1. Firestore 리소스 수집 API
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
      "database_filter": "optional array"
    }
  }
  ```
- **Response 스키마**:
  ```json
  {
    "resources": [
      {
        "name": "database_name",
        "data": "FirestoreDatabase/Collection/Index 모델",
        "reference": {
          "resource_id": "database_id",
          "external_link": "console_url"
        },
        "region_code": "location",
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
- **FirestoreDatabase**: 데이터베이스 메인 엔터티
  - `database_id`: 데이터베이스 식별자
  - `name`: 데이터베이스 이름
  - `type`: 데이터베이스 타입 (FIRESTORE_NATIVE)
  - `location_id`: 지리적 위치
  - `concurrency_control`: 동시성 제어 설정
  - `create_time`: 생성 시간
  - `etag`: 버전 태그

- **FirestoreCollection**: 컬렉션 엔터티
  - `collection_id`: 컬렉션 식별자
  - `collection_path`: 전체 경로
  - `depth_level`: 중첩 깊이
  - `parent_document_path`: 부모 문서 경로
  - `documents`: 포함된 문서 목록
  - `document_count`: 문서 개수

- **DocumentInfo**: 문서 정보 엔터티
  - `document_id`: 문서 식별자
  - `name`: 문서 전체 이름
  - `fields`: 문서 필드 정보
  - `create_time`: 생성 시간
  - `update_time`: 수정 시간

- **FirestoreIndex**: 인덱스 엔터티
  - `index_id`: 인덱스 식별자
  - `state`: 인덱스 상태 (CREATING, READY, ERROR 등)
  - `query_scope`: 쿼리 범위 (COLLECTION, COLLECTION_GROUP)
  - `fields`: 인덱스 필드 목록 (필드명, 순서, 모드)

#### 3.1.2. 트랜잭션 바운더리
- **읽기 전용 수집**: 모든 API 호출은 READ COMMITTED 격리 수준
- **데이터베이스 중심 수집**: FIRESTORE_NATIVE 타입의 데이터베이스만 필터링하여 수집
- **실패 처리**: 개별 리소스 수집 실패가 전체 수집에 영향 없음

#### 3.1.3. 캐싱 전략
- **데이터베이스 목록 캐시**: 5분 TTL로 FIRESTORE_NATIVE 데이터베이스 목록 캐싱
- **API 응답 캐시**: 없음 (실시간 상태 반영 필요)

## 4. 비즈니스 로직 플로우 (Business Logic Flow)

### 4.1. 정상 플로우
1. **인증 검증**: Service Account 크리덴셜 유효성 확인
2. **데이터베이스 목록 조회**: `projects.databases.list` API를 통한 모든 데이터베이스 조회
3. **FIRESTORE_NATIVE 필터링**: `type`이 `FIRESTORE_NATIVE`인 데이터베이스만 선별
4. **재귀적 컬렉션 수집**:
   - `projects.databases.documents.listCollectionIds`로 최상위 컬렉션 조회
   - 각 컬렉션의 문서 목록 조회 (`projects.databases.documents.list`)
   - 각 문서의 하위 컬렉션을 재귀적으로 탐색
5. **인덱스 정보 수집**: `projects.databases.collectionGroups.indexes.list`로 복합 인덱스 조회
6. **데이터 변환**: SpaceONE 표준 모델로 변환
7. **응답 생성**: 각 리소스 타입별 Response 객체 생성

### 4.2. 예외 플로우
- **인증 실패**: 즉시 실패 반환, 재시도 없음
- **API 할당량 초과**: 지수 백오프로 재시도 (최대 3회)
- **네트워크 오류**: 연결 실패, 타임아웃에 대한 재시도 로직
- **개별 데이터베이스 실패**: 로그 기록 후 다음 데이터베이스 진행
- **재귀 탐색 실패**: 해당 브랜치만 건너뛰고 다른 컬렉션 계속 탐색

### 4.3. 복구 전략
- **부분 실패 허용**: 일부 데이터베이스 수집 실패 시에도 성공한 데이터 반환
- **재시도 로직**: 네트워크 오류에 대해서만 제한적 재시도
- **장애 격리**: 데이터베이스별, 컬렉션별 독립적 처리로 장애 전파 방지

## 5. 외부 연동 (External Integration)

### 5.1. Google Cloud Firestore API
- **의존 서비스**: Google Cloud Firestore API v1
- **엔드포인트**: `https://firestore.googleapis.com`
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
  - `datastore.databases.list`
  - `datastore.databases.get`
  - `datastore.documents.list`
  - `datastore.indexes.list`
- **권한 범위**: 프로젝트 수준 읽기 전용 권한 (Cloud Datastore Viewer 역할)

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
- **수집 성능**: 프로젝트당 평균 20초 이내 수집 완료 (재귀 탐색 포함)
- **처리량**: 동시 3개 프로젝트 병렬 처리 지원
- **오류율**: 5% 미만 유지 목표
- **메트릭 수집**: 
  - `document_count`: 데이터베이스별 총 문서 수
  - `index_count`: 데이터베이스별 총 인덱스 수

### 7.3. 알림 설정
- **임계치 초과**: API 할당량 80% 도달 시 경고
- **장애 감지**: 연속 3회 수집 실패 시 알림
- **성능 저하**: 수집 시간 60초 초과 시 모니터링

## 8. AI 개발 지시사항 (AI Development Guidelines)

### 8.1. 개발 우선순위
1. **P0**: 기본 데이터베이스 수집 기능 완성
2. **P1**: 재귀적 컬렉션 및 문서 수집
3. **P2**: 인덱스 정보 연계 및 성능 메트릭

### 8.2. 검증 체크리스트
- **정확성**: 실제 GCP 콘솔과 수집 데이터 일치 확인
- **트랜잭션**: 부분 실패 시에도 성공한 데이터 반환 검증
- **보안**: 민감 정보 로깅 방지 및 인증 처리 검증  
- **성능**: 대용량 프로젝트(1000+ 문서) 수집 성능 검증
- **에러**: 모든 예외 상황에 대한 적절한 처리 및 복구 검증

### 8.3. 참고 자료
- [Google Cloud Firestore API 문서](https://cloud.google.com/firestore/docs/reference/rest)
- [SpaceONE 플러그인 개발 가이드](https://cloudforet.io/docs/)
- [현재 구현 소스 코드](../../../../src/spaceone/inventory/)

---

## 부록: 현재 구현 상태 (Implementation Status)

### A.1. 구현 완료 기능
- ✅ **FirestoreManager**: 통합 매니저를 통한 데이터베이스, 컬렉션, 인덱스 수집
- ✅ **FirestoreDatabaseConnector**: Google Cloud Firestore API 연동, Admin SDK 활용
- ✅ **재귀적 문서 탐색**: 모든 컬렉션을 재귀적으로 수집하여 전체 문서 구조 파악
- ✅ **다중 리소스 타입**: Database, Collection, Index 3가지 리소스 타입 지원
- ✅ **데이터 모델**: Database, Collection, DocumentInfo, Index 완전한 모델
- ✅ **메타데이터**: SpaceONE 콘솔 UI 레이아웃, 위젯

### A.2. 주요 구현 특징
- **데이터베이스 중심 수집**: `projects.databases.list`를 통해 `FIRESTORE_NATIVE` 타입만 필터링
- **재귀적 문서 탐색**: 최상위 컬렉션부터 시작하여 모든 하위 컬렉션과 문서를 재귀적으로 탐색
- **인덱스 정보 수집**: `projects.databases.collectionGroups.indexes.list`를 통한 복합 인덱스 수집
- **SpaceONE 모델 변환**: 수집된 모든 원시 데이터를 SpaceONE Cloud Service 모델 형식으로 변환

### A.3. 수집 플로우
1. **데이터베이스 목록 조회**: `list_databases()`로 모든 데이터베이스 조회
2. **FIRESTORE_NATIVE 필터링**: 해당 타입의 데이터베이스만 선별
3. **각 데이터베이스별 리소스 수집**:
   - Database 리소스 생성
   - Collection 리소스 생성 (재귀적 문서 탐색 포함)
   - Index 리소스 생성
4. **통합 응답 생성**: 3가지 리소스 타입을 혼합한 응답 리스트 반환

### A.4. 파일 구조
```
src/spaceone/inventory/
├── connector/firestore/
│   ├── __init__.py
│   └── database_v1.py              # Google Cloud Firestore API 연동
├── manager/firestore/
│   ├── __init__.py
│   └── firestore_manager.py        # 통합 매니저 (Database, Collection, Index)
├── model/firestore/
│   ├── database/                   # 데이터베이스 모델
│   ├── collection/                 # 컬렉션 모델
│   └── index/                      # 인덱스 모델
└── service/
    └── collector_service.py        # 플러그인 엔트리포인트
```

### A.5. 기술 스택
- **언어**: Python 3.8+
- **프레임워크**: SpaceONE Core 2.0+, SpaceONE Inventory, Schematics
- **Google Cloud SDK**: 
  - google-oauth2 (Service Account 인증)
  - googleapiclient (Discovery API 클라이언트)
  - google-cloud-firestore (Firestore Admin SDK)
- **테스트**: unittest, unittest.mock (Google Cloud API 모킹)
- **품질 관리**: ruff (린팅/포맷팅), pytest-cov (커버리지)
