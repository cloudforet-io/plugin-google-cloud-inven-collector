## SpaceONE Google Cloud Inventory Collector PRD 자동 생성 가이드

> 이 문서는 SpaceONE Google Cloud Inventory Collector 플러그인에서 AI가 Google Cloud 서비스별 PRD를 자동 생성하도록 안내합니다. SpaceONE 플러그인 아키텍처와 Google Cloud API 특성을 엄격히 반영합니다.

### 🎯 목적

- Google Cloud 서비스 수집 기능의 최소 정보로 SpaceONE 플러그인 PRD 빠르게 산출
- SpaceONE CloudServiceResponse 기반 데이터 모델과 Google Cloud API 연동 명세 포함
- 구현 코드는 포함하지 않음(개념·명세 중심)
  - 예: 실제 Python/Connector 구현 금지, Google Cloud API 연동 방식과 SpaceONE 표준 모델만 기술

### 🧭 3단계 프로세스

1. Google Cloud 서비스 복잡도 분류 → SIMPLE_COLLECTOR / MULTI_RESOURCE_COLLECTOR / COMPLEX_GCP_INTEGRATION 중 선택
2. SpaceONE 플러그인 체크리스트 반영 → 인증/API연동/데이터모델/에러/로깅/테스트 등
3. AI 요청 템플릿에 Google Cloud 서비스 정보를 기입하여 생성 요청

---

### 1️⃣ Google Cloud 서비스 복잡도 분류

#### SIMPLE_COLLECTOR (단순 리소스 수집)

- 특징: 단일 Google Cloud 리소스 타입, 기본 list/get API만 사용, 지역별 수집
- 예시: Cloud Storage Buckets, Cloud KMS Keys, Cloud DNS Zones
- Google Cloud API: 1-2개 메서드 (`list()`, `get()`)

#### MULTI_RESOURCE_COLLECTOR (다중 리소스 수집)

- 특징: 여러 연관 리소스 수집, 리소스 간 관계 매핑, 메타데이터 연계
- 예시: Compute Engine (Instance + Disk + Network), Dataproc (Cluster + Jobs + Templates)
- Google Cloud API: 3-5개 메서드, 리소스 간 참조 관계 처리

#### COMPLEX_GCP_INTEGRATION (복잡한 GCP 통합)

- 특징: 실시간 모니터링 연동, 여러 GCP 서비스 통합, 스트리밍/이벤트 처리
- 예시: Cloud Run (Service + Revision + Traffic) + Cloud Monitoring, BigQuery (Dataset + Table + Job) + Cloud Logging
- Google Cloud API: 6개 이상 메서드, 비동기 처리 필요

---

### 2️⃣ SpaceONE 플러그인 체크리스트(선택 적용)

아래 항목은 SpaceONE Google Cloud Inventory Collector 표준과 직결되며, 필요 시 PRD에 명시적으로 포함하세요.

- **플러그인 구조**: Service → Manager → Connector 3계층 아키텍처, `spaceone.inventory` 네임스페이스 사용
- **Google Cloud 인증**: Service Account 키 파일 기반, OAuth 2.0 토큰 자동 갱신
- **API 연동**: Google Cloud Client Library 사용, API 할당량 및 재시도 로직 포함
- **데이터 모델**: Schematics 기반 SpaceONE 표준 모델, CloudServiceResponse/CloudServiceType 상속
- **수집 패턴**: 리전별 병렬 수집, 부분 실패 허용 (개별 리소스 실패가 전체 수집에 영향 없음)
- **에러 핸들링**: Google Cloud API 오류 (401, 403, 404, 429) 상황별 처리, SpaceONE Core 예외 사용
- **로깅**: Google Cloud 민감정보(토큰, 키) 미포함, 수집 성능 메트릭 포함
- **테스트**: unittest.mock으로 Google Cloud API 모킹, spaceone 패키지 의존성 모킹

> 주의: 구현 코드는 포함하지 않습니다. 개념적 명세·요구사항·플로우만 기술합니다.

---

### 4️⃣ AI 요청 템플릿 (SpaceONE Google Cloud Collector 전용)

다음 프롬프트를 복사해 필수 값을 채운 뒤 AI에 요청하세요. 산출물은 `docs/ko/prd/{service}/README.md` 형태의 PRD 구조를 사용합니다.

```markdown
"SpaceONE Google Cloud Inventory Collector 플러그인의 {서비스명} 수집 기능 PRD를 작성해줘.
구현 코드는 포함하지 말고(개념·명세만), 아래 입력을 반영해.

[입력]

- Google Cloud 서비스명: {예: Cloud Dataproc}
- 수집 대상 리소스: {예: Clusters, Jobs, Workflow Templates}
- 복잡도: {SIMPLE_COLLECTOR | MULTI_RESOURCE_COLLECTOR | COMPLEX_GCP_INTEGRATION}
- Google Cloud API 목록:
  - dataproc.projects.regions.clusters.list
  - dataproc.projects.regions.clusters.get
  - dataproc.projects.regions.jobs.list
- 인증/권한: Service Account 키 기반, 필요한 IAM 권한 목록
- 주요 데이터 모델: {SpaceONE CloudServiceResponse 기반 엔터티}
- 수집 패턴: {리전별/프로젝트별/전역}
- 외부 연동: Google Cloud {서비스명} API v{버전}
- 성능 목표: {수집 완료 시간}, 처리량 {리소스 수/분}
- 에러 처리: Google Cloud API 오류 상황별 처리 방식
- 테스트 정책: Google Cloud API 모킹, spaceone 의존성 모킹

[반영할 SpaceONE 표준]

- 플러그인 구조: Service → Manager → Connector 3계층
- 인증: Google Cloud Service Account 키 파일, OAuth 2.0
- API 연동: Google Cloud Client Library, 할당량/재시도 로직
- 데이터 모델: Schematics 기반, CloudServiceResponse/CloudServiceType
- 수집 패턴: 리전별 병렬, 부분 실패 허용
- 에러/로깅: SpaceONE Core 예외, Google Cloud 민감정보 제외
- 테스트: unittest.mock, Google Cloud API 모킹

[출력 규칙]

- `docs/ko/prd/{service}/README.md` 파일 형태로 작성
- Google Cloud API 문서 참조 링크 포함
- SpaceONE 플러그인 개발 지시사항 포함
- 개념적 JSON/API 스키마는 허용, 실제 Python 코드는 작성 금지
  "
```

#### 예시 입력 (Google Cloud Storage)

```markdown
- Google Cloud 서비스명: Cloud Storage
- 수집 대상 리소스: Buckets, Objects (메타데이터만)
- 복잡도: SIMPLE_COLLECTOR
- Google Cloud API 목록:
  - storage.buckets.list
  - storage.buckets.get
  - storage.buckets.getIamPolicy
- 인증/권한: Service Account 키 기반, storage.buckets.list, storage.buckets.get 권한
- 주요 데이터 모델: StorageBucket (CloudServiceResponse 기반)
- 수집 패턴: 프로젝트별 (리전 무관)
- 외부 연동: Google Cloud Storage API v1
- 성능 목표: 프로젝트당 평균 10초, 처리량 100 버킷/분
- 에러 처리: 403 (권한 없음), 404 (버킷 없음) 정상 처리
- 테스트 정책: Google Cloud Storage API 모킹, spaceone.core 모킹
```

---

### 5️⃣ 산출물 위치/파일명 권장

- Google Cloud 서비스별 문서 폴더: `docs/ko/prd/{service}/`
  - 예: `docs/ko/prd/dataproc/`, `docs/ko/prd/storage/`, `docs/ko/prd/compute/`
- 기본 파일명: `README.md` (PRD 본문)
- 필요 시 추가 문서: `requirements.md`, `api-integration.md`, `data-models.md` 등으로 분리 가능

---

### ✅ 리뷰 체크리스트 (SpaceONE Google Cloud Collector)

- SpaceONE 플러그인 PRD 구조 준수, 구현 코드 미포함
- Google Cloud API 연동 방식 명시 (Service Account 인증, OAuth 2.0)
- SpaceONE CloudServiceResponse/CloudServiceType 기반 데이터 모델 설계
- Service → Manager → Connector 3계층 아키텍처 반영
- Google Cloud API 오류 처리 (401, 403, 404, 429) 상황별 정의
- 리전별 병렬 수집, 부분 실패 허용 패턴 명시
- Google Cloud 민감정보 로깅 금지 원칙 포함
- unittest.mock 기반 테스트 정책 (Google Cloud API 모킹, spaceone 의존성 모킹) 명시

---

### 📌 빠른 참조

- **SIMPLE_COLLECTOR**: 단일 리소스 타입 (Storage Buckets, KMS Keys)
- **MULTI_RESOURCE_COLLECTOR**: 연관 리소스 수집 (Compute Instance+Disk, Dataproc Cluster+Jobs)
- **COMPLEX_GCP_INTEGRATION**: 다중 서비스 통합 (Cloud Run+Monitoring, BigQuery+Logging)
- **필수 표준**: Service→Manager→Connector 구조, Google Cloud API 연동, SpaceONE 표준 모델, 민감정보 제외 로깅

> 본 가이드는 SpaceONE Google Cloud Inventory Collector 플러그인 전용입니다. 다른 클라우드 프로바이더 지침은 포함하지 않습니다.

---

### 📦 PRD 단위와 Endpoint 포함 원칙

- **PRD의 단위**: 하나의 명확한 사용자 가치/업무 시나리오를 완결하는 "기능(Feature)" 단위입니다.
- **여러 Endpoint 포함 여부**: 동일한 사용자 스토리/수용 기준을 달성하기 위해 필요한 API 묶음이라면 하나의 PRD에 여러 엔드포인트를 포함합니다.
- **묶음/분리 판단 기준**:
  - 같은 도메인이고 하나의 플로우에서 함께 동작(목록→상세→행동)한다면 묶음
  - 서로 다른 사용자 가치(예: 사용자 관리 vs 권한 정책 관리)라면 분리
  - 관리자/외부시스템 등 대상/위험/릴리즈 단위가 다르면 분리 고려
  - 휴리스틱: 동일 플로우 내 엔드포인트가 5개 이하이면 단일 PRD 유지 권장

### 🗂 문서 분할 가이드

- **기본 원칙**: 단일 파일(`1.feature-spec.md`) 유지가 가독성과 추적에 유리함
- **분할이 유효한 경우**:
  - 4개 이상 세부 플로우, 외부 연동 다수, 서로 다른 팀 소유 영역이 명확히 존재
  - OpenAPI 명세/데이터 모델/로직 플로우를 병렬 작업해야 하는 경우
- **분할 방식**: 마스터 PRD(`1.feature-spec.md`)는 유지하고, 세부 항목만 `2-1.api-spec.yaml`, `2-2.api-schemas.md`, `3.data-model.md`, `4.logic-flow.md`로 보조 분리
- **안티패턴**: 작은 기능을 과도하게 분할, 동일 정보가 파일 간 중복되는 경우

### 🤖 복잡도 자동 분류 규칙(AI)

- **자동 분류**: 기본적으로 AI가 입력을 바탕으로 SIMPLE/MULTI/COMPLEX를 판정하고, 필요 시 질문 후 확정합니다.
- **판정 기준(휴리스틱)**:
  - SIMPLE: 단일 엔드포인트 또는 단순 조회/토글, 외부 연동 없음, 트랜잭션 단순
  - MULTI: 2–3 엔드포인트 CRUD 조합, 기본 인증/권한, 트랜잭션 경계 명확
  - COMPLEX: 4개 이상 엔드포인트, 외부 연동/스트리밍/다단계 상태전이/고급 트랜잭션
- **사람 오버라이드**: 필요 시 사람이 복잡도 레벨을 명시하면 그 값을 우선합니다.

### ❓ 정보 부족/모순 시 질의·검증 절차

- **최소 입력 요구**(부족하면 질문):
  - 기능명, 도메인, 목적 또는 사용자 스토리, 주요 리소스/행위, 인증/권한 유무, 성능/우선순위(선택), 외부 연동 유무
- **대표 Clarifying Questions**:
  1. 이 기능으로 달성하려는 단일 사용자 가치를 한 문장으로 요약해 주세요.
  2. 대상 사용자는 누구인가요? (일반 사용자/관리자/외부 시스템)
  3. 필요한 엔드포인트가 목록/상세/생성/수정/삭제 중 무엇인지요?
  4. 인증/권한 정책이 필요합니까? 필요한 경우 대상 역할은?
  5. 외부 연동(예: 스토리지/결제/서드파티 API)이 있나요?
  6. 성능 목표(p95 응답시간, RPS/TPS)나 데이터량 제약이 있나요?
  7. 데이터 모델의 핵심 필드는 무엇인가요? (개념 수준)
- **모순 감지 예**:
  - 사용자 스토리는 비인증 접근이라고 했는데, 엔드포인트에 관리자 권한 요구 → 정책 재확인 요청
  - `/v1` 버저닝 원칙 위반 경로 → 경로 수정 제안
  - 도메인과 리소스 네이밍 불일치 → 네이밍 정합성 질의

### 🛠 AI 생성 워크플로(자동 분류/질의 포함)

1. 입력 수집 → 2) 자동 복잡도 판정(모호하면 질문) → 3) 모순/누락 검사 및 보완 질의 → 4) `1.prd-template.md` 구조에 맞춰 초안 생성 → 5) 체크리스트로 내부 품질 검증 → 6) 초안 전달 및 피드백 반영

### 📝 자동판단형 요청 템플릿

```markdown
"백엔드 기능의 PRD를 생성해줘. docs/prd-templates/1.prd-template.md 구조를 그대로 사용하고,
복잡도는 네가 자동으로 판정해. 정보가 모호/부족/모순이면 먼저 질문한 뒤에 작성해줘.

[현재 입력]

- 기능명: { }
- 도메인: { }
- 목적/사용자 스토리(가능하면 둘 다): { }
- 주요 리소스/엔드포인트 후보: { } # 없으면 AI가 제안
- 인증/권한: { }
- 외부 연동: { }
- 성능/우선순위(선택): { }

[규칙]

- /api/v1 버전 프리픽스, 도메인별 router → core/router_endpoint 포함 원칙 준수
- JWT 인증과 미들웨어 트랜잭션, Repository 패턴, MCP 모델 순서 일치, 글로벌 에러/로깅, 테스트 정책(.env.test, 롤백)을 반영
- 구현 코드는 금지하고 개념적 JSON/SQL/플로우만 작성
  "
```