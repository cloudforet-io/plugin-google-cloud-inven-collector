# Google Cloud Filestore 인벤토리 수집 제품 요구사항 정의서 (PRD)

## 1. 비즈니스 요구사항 (Business Requirements)

### 1.1. 목적 (Purpose)
SpaceONE 인벤토리 플랫폼에서 Google Cloud Filestore 리소스를 자동으로 수집, 분류, 모니터링하여 클라우드 파일 스토리지 관리 효율성을 극대화합니다. 개발팀과 인프라 관리팀이 Filestore 인스턴스의 상태, 비용, 성능을 통합적으로 관리할 수 있도록 지원합니다.

### 1.2. 사용자 스토리 (User Stories)
- **인프라 관리자**: 모든 프로젝트의 Filestore 인스턴스 현황을 한눈에 파악하고 용량 및 비용 최적화 포인트를 식별
- **개발자**: 애플리케이션에서 사용 중인 파일 스토리지 상태를 모니터링하여 성능 이슈를 사전에 감지
- **팀 리더**: 팀별 Filestore 리소스 사용량과 비용을 추적하여 예산 관리 최적화

### 1.3. 수용 기준 (Acceptance Criteria)
**P0 (필수)**:
- 모든 활성 Filestore 인스턴스 정보 수집 (100% 정확도)
- 인스턴스별 파일 공유, 백업, 스냅샷 정보 연계
- 실시간 상태 모니터링 (5분 이내 갱신)

**P1 (중요)**:
- 다중 API 버전 지원 (v1, v1beta1)
- 네트워크 및 보안 설정 정보 수집
- 다중 프로젝트 병렬 수집

**P2 (선택)**:
- 성능 메트릭 연계
- 예측적 알림 기능

## 2. API 인터페이스 (API Interface)

### 2.1. 수집 엔드포인트 (Collection Endpoints)

#### 2.1.1. Filestore 인스턴스 수집 API
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
- **Response 스키마**:
  ```json
  {
    "resources": [
      {
        "name": "instance_name",
        "data": "FilestoreInstance 모델",
        "reference": {
          "resource_id": "instance_id",
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
- **FilestoreInstance**: 인스턴스 메인 엔터티
  - `instance_id`: 인스턴스 식별자
  - `name`: 인스턴스 이름
  - `state`: 인스턴스 상태 (CREATING, READY, DELETING 등)
  - `tier`: 성능 계층 (BASIC_HDD, BASIC_SSD, HIGH_SCALE_SSD 등)
  - `location`: 지리적 위치
  - `networks`: 네트워크 설정 정보
  - `file_shares`: 파일 공유 목록
  - `detailed_shares`: v1beta1 API를 통한 상세 파일 공유 정보
  - `snapshots`: 스냅샷 목록

- **Network**: 네트워크 구성 정보
  - `network`: VPC 네트워크 이름
  - `modes`: 연결 모드 (DIRECT_PEERING, PRIVATE_SERVICE_ACCESS)
  - `reserved_ip_range`: 예약된 IP 범위
  - `connect_mode`: 연결 모드

- **FileShare**: 파일 공유 정보
  - `name`: 파일 공유 이름
  - `capacity_gb`: 할당된 용량 (GB)
  - `source_backup`: 소스 백업
  - `nfs_export_options`: NFS 내보내기 옵션

#### 3.1.2. 트랜잭션 바운더리
- **읽기 전용 수집**: 모든 API 호출은 READ COMMITTED 격리 수준
- **전역 수집**: 모든 리전의 인스턴스를 한 번의 API 호출로 효율적 조회
- **실패 처리**: 개별 인스턴스 수집 실패가 전체 수집에 영향 없음

#### 3.1.3. 캐싱 전략
- **API 응답 캐시**: 없음 (실시간 상태 반영 필요)
- **메타데이터 캐시**: 5분 TTL로 Cloud Service Type 정보 캐싱

## 4. 비즈니스 로직 플로우 (Business Logic Flow)

### 4.1. 정상 플로우
1. **인증 검증**: Service Account 크리덴셜 유효성 확인
2. **전역 인스턴스 조회**: `projects/{project_id}/locations/-/instances` 엔드포인트를 통한 모든 리전 인스턴스 수집
3. **다중 API 버전 활용**: v1 API (기본 기능)와 v1beta1 API (고급 기능) 병행 사용
4. **상세 정보 수집**: 각 인스턴스의 파일 공유, 백업, 스냅샷 등 관련 리소스 포함 수집
5. **데이터 변환**: SpaceONE 표준 모델로 변환
6. **응답 생성**: FilestoreInstanceResponse 객체 생성

### 4.2. 예외 플로우
- **인증 실패**: 즉시 실패 반환, 재시도 없음
- **API 할당량 초과**: 지수 백오프로 재시도 (최대 3회)
- **네트워크 오류**: 연결 실패, 타임아웃에 대한 재시도 로직
- **개별 인스턴스 실패**: 로그 기록 후 다음 인스턴스 진행
- **데이터 파싱 실패**: 에러 응답 생성, 수집 계속

### 4.3. 복구 전략
- **부분 실패 허용**: 일부 인스턴스 수집 실패 시에도 성공한 데이터 반환
- **재시도 로직**: 네트워크 오류에 대해서만 제한적 재시도
- **장애 격리**: 인스턴스별 독립적 처리로 장애 전파 방지

## 5. 외부 연동 (External Integration)

### 5.1. Google Cloud Filestore API
- **의존 서비스**: Google Cloud Filestore API v1, v1beta1
- **엔드포인트**: `https://file.googleapis.com`
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
- **Google Cloud 인증**: Service Account 키 파일 (.json) 사용
- **필수 IAM 권한**:
  - `file.instances.list`
  - `file.instances.get`
  - `file.snapshots.list`
  - `file.backups.list`
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
- **수집 성능**: 프로젝트당 평균 10초 이내 수집 완료
- **처리량**: 동시 10개 프로젝트 병렬 처리 지원
- **오류율**: 5% 미만 유지 목표
- **메트릭 수집**: 
  - `filestore_count`: 프로젝트별 Filestore 인스턴스 개수
  - `capacity_gb`: Filestore 인스턴스의 총 할당 용량(GB)

### 7.3. 알림 설정
- **임계치 초과**: API 할당량 80% 도달 시 경고
- **장애 감지**: 연속 3회 수집 실패 시 알림
- **성능 저하**: 수집 시간 30초 초과 시 모니터링

## 8. AI 개발 지시사항 (AI Development Guidelines)

### 8.1. 개발 우선순위
1. **P0**: 기본 인스턴스 수집 기능 완성
2. **P1**: 파일 공유 및 백업 정보 연계
3. **P2**: 성능 메트릭 및 모니터링 연동

### 8.2. 검증 체크리스트
- **정확성**: 실제 GCP 콘솔과 수집 데이터 일치 확인
- **트랜잭션**: 부분 실패 시에도 성공한 데이터 반환 검증
- **보안**: 민감 정보 로깅 방지 및 인증 처리 검증  
- **성능**: 대용량 프로젝트(100+ 인스턴스) 수집 성능 검증
- **에러**: 모든 예외 상황에 대한 적절한 처리 및 복구 검증

### 8.3. 참고 자료
- [Google Cloud Filestore API 문서](https://cloud.google.com/filestore/docs/reference/rest)
- [SpaceONE 플러그인 개발 가이드](https://cloudforet.io/docs/)
- [현재 구현 소스 코드](../../../../src/spaceone/inventory/)

---

## 부록: 현재 구현 상태 (Implementation Status)

### A.1. 구현 완료 기능
- ✅ **FilestoreInstanceConnector**: Google Cloud API 연동, Service Account 인증, 전역 리소스 조회
- ✅ **FilestoreInstanceManager**: 비즈니스 로직, 인스턴스 목록/상세 조회, 데이터 변환  
- ✅ **다중 API 버전 지원**: v1 API(기본 기능)와 v1beta1 API(고급 기능) 병행 활용
- ✅ **데이터 모델**: FilestoreInstance, Network, FileShare, DetailedShare, Snapshot 등 완전한 모델
- ✅ **메타데이터**: SpaceONE 콘솔 UI 레이아웃, 위젯 (총 개수, 리전별, 프로젝트별 차트)
- ✅ **테스트**: 단위 테스트 및 통합 테스트

### A.2. 주요 구현 특징
- **전역 리소스 조회**: `projects/{project_id}/locations/-/instances` 엔드포인트를 통한 모든 리전 인스턴스 효율적 수집
- **상세 정보 수집**: 각 인스턴스의 파일 공유, 백업, 스냅샷 등 관련 리소스까지 포함하여 수집
- **SpaceONE 통합**: 수집된 데이터를 SpaceONE의 Cloud Service 모델 형식에 맞게 변환하여 콘솔에서 직관적 확인 가능

### A.3. 파일 구조
```
src/spaceone/inventory/
├── connector/filestore/
│   ├── __init__.py
│   ├── instance_v1.py              # Google Cloud Filestore API v1 연동
│   └── instance_v1beta1.py         # Google Cloud Filestore API v1beta1 연동
├── manager/filestore/
│   ├── __init__.py
│   └── instance_manager.py         # 비즈니스 로직, 데이터 변환
├── model/filestore/instance/
│   ├── __init__.py
│   ├── data.py                     # FilestoreInstance, Network 등 데이터 모델
│   ├── cloud_service.py            # FilestoreInstanceResource/Response 모델
│   ├── cloud_service_type.py       # CloudServiceType 정의
│   └── widget/                     # SpaceONE 콘솔 위젯 설정
└── service/
    └── collector_service.py        # 플러그인 엔트리포인트
```

### A.4. 기술 스택
- **언어**: Python 3.8+
- **프레임워크**: SpaceONE Core 2.0+, SpaceONE Inventory, Schematics
- **Google Cloud SDK**: 
  - google-oauth2 (Service Account 인증)
  - googleapiclient (Discovery API 클라이언트)
- **테스트**: unittest, unittest.mock (Google Cloud API 모킹)
- **품질 관리**: ruff (린팅/포맷팅), pytest-cov (커버리지) 