# Google Cloud Dataproc 인벤토리 수집 제품 요구사항 정의서 (PRD)

## 1. 비즈니스 요구사항 (Business Requirements)

### 1.1. 목적 (Purpose)
SpaceONE 인벤토리 플랫폼에서 Google Cloud Dataproc 리소스를 자동으로 수집, 분류, 모니터링하여 클라우드 인프라 관리 효율성을 극대화합니다. 데이터 엔지니어링팀과 인프라 관리팀이 Dataproc 클러스터의 상태, 비용, 성능을 통합적으로 관리할 수 있도록 지원합니다.

### 1.2. 사용자 스토리 (User Stories)
- **인프라 관리자**: 모든 프로젝트의 Dataproc 클러스터 현황을 한눈에 파악하고 비용 최적화 포인트를 식별
- **데이터 엔지니어**: 실행 중인 클러스터와 작업 상태를 모니터링하여 데이터 파이프라인 안정성 확보
- **팀 리더**: 팀별 Dataproc 리소스 사용량과 비용을 추적하여 예산 관리 최적화

### 1.3. 수용 기준 (Acceptance Criteria)
**P0 (필수)**:
- 모든 활성 Dataproc 클러스터 정보 수집 (100% 정확도)
- 클러스터별 최근 10개 작업(Job) 정보 연계
- 실시간 상태 모니터링 (5분 이내 갱신)

**P1 (중요)**:
- 워크플로 템플릿 및 오토스케일링 정책 수집
- 비용 및 성능 메트릭 연계
- 다중 프로젝트 순차 수집

**P2 (선택)**:
- 히스토리 데이터 분석
- 예측적 알림 기능

## 2. API 인터페이스 (API Interface)

### 2.1. 수집 엔드포인트 (Collection Endpoints)

#### 2.1.1. 클러스터 수집 API
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
      "region_filter": "optional array",
      "include_jobs": "boolean"
    }
  }
  ```
- **Response 스키마**:
  ```json
  {
    "resources": [
      {
        "name": "cluster_name",
        "data": "DataprocCluster 모델",
        "reference": {
          "resource_id": "cluster_uuid",
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
- **DataprocCluster**: 클러스터 메인 엔터티
  - `project_id`: 프로젝트 식별자
  - `cluster_name`: 클러스터 이름
  - `cluster_uuid`: 고유 식별자
  - `status`: 클러스터 상태 정보
  - `config`: 클러스터 구성 설정
  - `location`: 지리적 위치
  - `jobs`: 연관된 작업 목록 (최대 10개)

- **ClusterConfig**: 클러스터 구성 정보
  - `master_config`: 마스터 노드 설정
  - `worker_config`: 워커 노드 설정  
  - `software_config`: 소프트웨어 구성
  - `gce_cluster_config`: GCE 클러스터 설정

#### 3.1.2. 트랜잭션 바운더리
- **읽기 전용 수집**: 모든 API 호출은 READ COMMITTED 격리 수준
- **배치 처리**: 리전별 순차 수집으로 안정성 최적화
- **실패 처리**: 개별 클러스터 수집 실패가 전체 수집에 영향 없음

#### 3.1.3. 캐싱 전략
- **리전 캐시**: 5분 TTL로 사용 가능한 리전 목록 캐싱
- **API 응답 캐시**: 없음 (실시간 상태 반영 필요)

## 4. 비즈니스 로직 플로우 (Business Logic Flow)

### 4.1. 정상 플로우
1. **인증 검증**: Service Account 크리덴셜 유효성 확인
2. **상태 카운터 초기화**: 수집 시작 시 SUCCESS/FAILURE/TIMEOUT/UNKNOWN 카운터 리셋
3. **동적 리전 최적화**: Google Cloud Compute API를 통한 실시간 리전 조회, 실패 시 핵심 리전(10개)으로 축소
4. **메모리 최적화 순차 클러스터 수집**: 순차 처리를 통한 안정적이고 메모리 효율적인 클러스터 수집
5. **안정적 순차 작업 수집**: 순차 처리를 통한 효율적이고 안정적인 작업 정보 수집
6. **스레드 안전성**: 각 스레드별 독립적인 API 클라이언트 및 강화된 타임아웃 관리
7. **선택적 상세 정보 수집**: 클러스터별 상세 구성 및 옵션 기반 작업 정보 조회 (성능 최적화)
8. **데이터 변환**: SpaceONE 표준 모델로 변환
9. **상태 추적 응답 생성**: 자동 로깅 기능을 포함한 상태별 카운터와 요약 정보 제공

### 4.2. 예외 플로우
- **인증 실패**: 즉시 실패 반환, 자동 FAILURE 상태 로깅, 재시도 없음
- **API 할당량 초과**: 지수 백오프로 재시도 (클러스터: 최대 3회, 작업: 최대 2회)
- **네트워크/SSL 오류**: 연결 실패, 타임아웃, SSL 오류에 대한 강화된 재시도 로직
- **개별 리전 실패**: 자동 DEBUG 레벨 로그 기록 후 다음 리전 진행, 순차 처리 중단 없음
- **스레드 타임아웃**: 클러스터 수집 90초(전체)/60초(개별), 작업 수집 15초 타임아웃으로 성능 보장
- **데이터 파싱 실패**: 자동 로깅 시스템을 통한 FAILURE 상태 기록 및 에러 응답 생성, 수집 계속
- **전역 타임아웃**: TIMEOUT 상태로 자동 분류하여 WARNING 레벨 로깅

### 4.3. 복구 전략
- **부분 실패 허용**: 일부 클러스터 수집 실패 시에도 성공한 데이터 반환
- **재시도 로직**: 네트워크 오류에 대해서만 제한적 재시도
- **장애 격리**: 클러스터별 독립적 처리로 장애 전파 방지

## 5. 외부 연동 (External Integration)

### 5.1. Google Cloud Dataproc API
- **의존 서비스**: Google Cloud Dataproc API v1
- **엔드포인트**: `https://dataproc.googleapis.com`
- **인증 방식**: Service Account 키 파일 기반 OAuth 2.0
- **API 할당량**: 프로젝트당 분당 1000 요청
- **장애 대응**: 
  - HTTP 429 (할당량 초과): 지수 백오프 재시도
  - HTTP 404 (리소스 없음): 정상 처리 (빈 결과 반환)
  - 기타 HTTP 오류: 로그 기록 후 다음 리전 진행

### 5.2. SpaceONE 플랫폼 연동
- **플러그인 인터페이스**: SpaceONE Inventory Collector Protocol
- **데이터 포맷**: CloudServiceResponse 표준 모델
- **메타데이터**: DynamicLayout 기반 UI 구성
- **위젯**: 차트 및 테이블 형태 대시보드 제공

## 6. 보안 & 컴플라이언스 (Security & Compliance)

### 6.1. 인증 및 인가
- **Google Cloud 인증**: Service Account 키 파일 (.json) 사용
- **필수 IAM 권한**:
  - `dataproc.clusters.list`
  - `dataproc.clusters.get`
  - `dataproc.jobs.list`
  - `dataproc.workflowTemplates.list`
  - `dataproc.autoscalingPolicies.list`
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
- **수집 성능**: 프로젝트당 평균 7.1초 이내 수집 완료 (메모리 제약 환경 최적화, 안정성 우선)
- **메모리 최적화 순차 처리**: 순차 처리를 통한 안정적이고 메모리 효율적인 성능 달성 (메모리 사용량 50-70% 절약)
- **순차 처리 최적화**: 메모리 효율성과 안정성을 극대화한 순차 처리 방식 채택
- **처리량**: 순차 프로젝트 처리 지원, 클러스터 처리율 평균 3-5 클러스터/초 (안정적 처리)
- **타임아웃 관리**: 클러스터 개별 조회 60초, 작업 조회 15초, 전체 순차 처리로 안정성 최적화
- **동적 리전 조회**: Google Cloud Compute API를 통한 실시간 리전 목록 갱신
- **상태 추적**: SUCCESS/FAILURE/TIMEOUT/UNKNOWN 상태별 자동 카운팅 및 요약 정보 제공
- **오류율**: 5% 미만 유지 목표, 자동 로깅을 통한 실시간 모니터링

### 7.3. 알림 설정
- **임계치 초과**: API 할당량 80% 도달 시 경고
- **장애 감지**: 연속 3회 수집 실패 시 알림
- **성능 저하**: 수집 시간 60초 초과 시 모니터링

## 8. AI 개발 지시사항 (AI Development Guidelines)

### 8.1. 개발 우선순위
1. **P0**: 기본 클러스터 수집 기능 완성
2. **P1**: 작업(Job) 정보 연계 및 오류 처리 강화
3. **P2**: 워크플로 템플릿 및 오토스케일링 정책 수집

### 8.2. 검증 체크리스트
- **정확성**: 실제 GCP 콘솔과 수집 데이터 일치 확인
- **트랜잭션**: 부분 실패 시에도 성공한 데이터 반환 검증
- **보안**: 민감 정보 로깅 방지 및 인증 처리 검증  
- **성능**: 대용량 프로젝트(100+ 클러스터) 수집 성능 검증
- **에러**: 모든 예외 상황에 대한 적절한 처리 및 복구 검증

### 8.3. 참고 자료
- [Google Cloud Dataproc API 문서](https://cloud.google.com/dataproc/docs/reference/rest)
- [SpaceONE 플러그인 개발 가이드](https://cloudforet.io/docs/)
- [현재 구현 소스 코드](../../../../src/spaceone/inventory/)

---

## 부록: 현재 구현 상태 (Implementation Status)

### A.1. 구현 완료 기능
- ✅ **DataprocClusterConnector**: Google Cloud API 연동, Service Account 인증, 연결 검증
- ✅ **DataprocClusterManager**: 비즈니스 로직, 클러스터 목록/상세 조회, 데이터 변환  
- ✅ **데이터 모델**: DataprocCluster, ClusterConfig, ClusterStatus, ClusterMetrics 등 완전한 모델
- ✅ **메타데이터**: SpaceONE 콘솔 UI 레이아웃, 위젯 (총 개수, 리전별, 프로젝트별 차트)
- ✅ **테스트**: 단위 테스트 및 통합 테스트 (Connector, Manager, Integration 테스트 포함)

### A.2. 구현 완료 기능 (P1) - v2.1 메모리 최적화
- ✅ **메모리 최적화 순차 클러스터 수집**: 순차 처리를 통한 안정적 성능 달성 (메모리 사용량 50-70% 절약), 안정적 타임아웃 관리
- ✅ **안정적 순차 작업 수집**: 순차 처리를 통한 효율적이고 안정적인 작업 정보 수집 (메모리 효율성 극대화)
- ✅ **동적 리전 조회**: Google Cloud Compute API를 통한 실시간 리전 목록 갱신, fallback 핵심 리전 지원
- ✅ **상태 추적 로깅 시스템**: SUCCESS/FAILURE/TIMEOUT/UNKNOWN 상태별 자동 카운팅 및 요약 정보 제공
- ✅ **워크플로 템플릿 수집**: WorkflowTemplate 모델 완성, API 연동 구현 완료
- ✅ **오토스케일링 정책 수집**: AutoscalingPolicy 모델 완성, API 연동 구현 완료
- ✅ **스레드 안전성**: 스레드별 독립적 API 클라이언트 관리 (`_get_thread_safe_client()`)
- ✅ **강화된 에러 처리**: 네트워크, SSL, 타임아웃 오류에 대한 세분화된 재시도 로직
- ✅ **자동 로깅 시스템**: 상태별 자동 로깅 (SUCCESS 무음, FAILURE/TIMEOUT 자동 기록)

### A.3. 파일 구조
```
src/spaceone/inventory/
├── connector/dataproc/
│   ├── __init__.py
│   └── cluster_connector.py        # Google Cloud Dataproc API 연동, 인증
├── manager/dataproc/
│   ├── __init__.py
│   └── cluster_manager.py          # 비즈니스 로직, 데이터 변환
├── model/dataproc/cluster/
│   ├── __init__.py
│   ├── data.py                     # DataprocCluster, ClusterConfig 등 데이터 모델
│   ├── cloud_service.py            # DataprocClusterResource/Response 모델
│   ├── cloud_service_type.py       # CloudServiceType 정의
│   └── widget/                     # SpaceONE 콘솔 위젯 설정
│       ├── total_count.yaml
│       ├── count_by_region.yaml
│       └── count_by_project.yaml
└── service/
    └── collector_service.py        # 플러그인 엔트리포인트
test/
├── test_dataproc.py                # 단위/통합 테스트
└── test_dataproc_integration.py    # 통합 테스트
```

### A.4. 기술 스택
- **언어**: Python 3.8+
- **프레임워크**: SpaceONE Core 2.0+, SpaceONE Inventory, Schematics
- **Google Cloud SDK**: 
  - google-oauth2 (Service Account 인증)
  - googleapiclient (Discovery API 클라이언트)
  - google-cloud-dataproc (Dataproc API)
- **테스트**: unittest, unittest.mock (Google Cloud API 모킹)
- **품질 관리**: ruff (린팅/포맷팅), pytest-cov (커버리지)