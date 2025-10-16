# Google Cloud Compute Engine 인벤토리 수집 제품 요구사항 정의서 (PRD)

## 1. 비즈니스 요구사항 (Business Requirements)

### 1.1. 목적 (Purpose)
SpaceONE 인벤토리 플랫폼에서 Google Cloud Compute Engine 리소스를 자동으로 수집, 분류, 모니터링하여 가상 머신 인프라 관리 효율성을 극대화합니다. 인프라 관리팀과 개발팀이 VM 인스턴스, 디스크, 스냅샷, 네트워크 등의 상태와 비용을 통합적으로 관리할 수 있도록 지원합니다.

### 1.2. 사용자 스토리 (User Stories)
- **인프라 관리자**: 모든 프로젝트의 Compute Engine 리소스 현황을 한눈에 파악하고 비용 최적화 포인트를 식별
- **개발자**: 애플리케이션에서 사용 중인 VM 인스턴스와 디스크 상태를 모니터링하여 성능 이슈를 사전에 감지
- **팀 리더**: 팀별 Compute Engine 리소스 사용량과 비용을 추적하여 예산 관리 최적화

### 1.3. 수용 기준 (Acceptance Criteria)
**P0 (필수)**:
- 모든 활성 VM 인스턴스 정보 수집 (100% 정확도)
- 인스턴스별 디스크, 스냅샷, 머신 이미지 정보 연계
- 인스턴스 템플릿 및 인스턴스 그룹 정보 수집

**P1 (중요)**:
- 네트워크 인터페이스 및 IP 주소 정보
- 메타데이터 및 라벨 정보 수집
- 다중 프로젝트 및 리전 병렬 수집

**P2 (선택)**:
- 성능 메트릭 연계
- 예측적 알림 기능

## 2. API 인터페이스 (API Interface)

### 2.1. 수집 엔드포인트 (Collection Endpoints)

#### 2.1.1. Compute Engine 리소스 수집 API
- **경로**: Internal API (플러그인 인터페이스)
- **메서드**: `collect_cloud_service()`
- **인증**: Google Cloud Service Account 키 기반
- **Rate Limit**: Google Cloud API 할당량 (분당 2000 요청)
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
      "zone_filter": "optional array"
    }
  }
  ```

## 3. 데이터 & 아키텍처 (Data & Architecture)

### 3.1. 데이터 모델 (Data Models)

#### 3.1.1. 주요 엔터티
- **VMInstance**: VM 인스턴스 메인 엔터티
  - `instance_id`: 인스턴스 식별자
  - `name`: 인스턴스 이름
  - `status`: 인스턴스 상태 (RUNNING, STOPPED, TERMINATED 등)
  - `machine_type`: 머신 타입
  - `zone`: 가용 영역
  - `disks`: 연결된 디스크 목록
  - `network_interfaces`: 네트워크 인터페이스 목록
  - `metadata`: 인스턴스 메타데이터
  - `labels`: 라벨 정보

- **Disk**: 디스크 엔터티
  - `disk_id`: 디스크 식별자
  - `name`: 디스크 이름
  - `type`: 디스크 타입 (pd-standard, pd-ssd, pd-balanced 등)
  - `size_gb`: 디스크 크기 (GB)
  - `zone`: 가용 영역
  - `status`: 디스크 상태
  - `source_image`: 소스 이미지

- **Snapshot**: 스냅샷 엔터티
  - `snapshot_id`: 스냅샷 식별자
  - `name`: 스냅샷 이름
  - `source_disk`: 소스 디스크
  - `disk_size_gb`: 디스크 크기
  - `storage_bytes`: 저장 용량
  - `creation_timestamp`: 생성 시간

- **MachineImage**: 머신 이미지 엔터티
  - `image_id`: 이미지 식별자
  - `name`: 이미지 이름
  - `source_instance`: 소스 인스턴스
  - `storage_locations`: 저장 위치
  - `total_storage_bytes`: 총 저장 용량

- **InstanceTemplate**: 인스턴스 템플릿 엔터티
  - `template_id`: 템플릿 식별자
  - `name`: 템플릿 이름
  - `machine_type`: 머신 타입
  - `source_instance`: 소스 인스턴스
  - `properties`: 템플릿 속성

- **InstanceGroup**: 인스턴스 그룹 엔터티
  - `group_id`: 그룹 식별자
  - `name`: 그룹 이름
  - `zone`: 가용 영역 (Zonal의 경우)
  - `region`: 리전 (Regional의 경우)
  - `size`: 그룹 크기
  - `instances`: 포함된 인스턴스 목록

## 4. 비즈니스 로직 플로우 (Business Logic Flow)

### 4.1. 정상 플로우
1. **인증 검증**: Service Account 크리덴셜 유효성 확인
2. **리전/존 목록 조회**: 사용 가능한 리전 및 존 목록 수집
3. **VM 인스턴스 수집**: 각 존별 VM 인스턴스 목록 및 상세 정보 수집
4. **디스크 정보 수집**: 각 존별 디스크 목록 및 상세 정보 수집
5. **스냅샷 정보 수집**: 프로젝트 레벨 스냅샷 목록 수집
6. **머신 이미지 수집**: 프로젝트 레벨 머신 이미지 목록 수집
7. **인스턴스 템플릿 수집**: 프로젝트 레벨 인스턴스 템플릿 수집
8. **인스턴스 그룹 수집**: 존별/리전별 인스턴스 그룹 수집
9. **데이터 변환**: SpaceONE 표준 모델로 변환
10. **응답 생성**: 각 리소스 타입별 Response 객체 생성

### 4.2. 예외 플로우
- **인증 실패**: 즉시 실패 반환, 재시도 없음
- **API 할당량 초과**: 지수 백오프로 재시도 (최대 3회)
- **네트워크 오류**: 연결 실패, 타임아웃에 대한 재시도 로직
- **개별 리소스 실패**: 로그 기록 후 다음 리소스 진행
- **데이터 파싱 실패**: 에러 응답 생성, 수집 계속

## 5. 외부 연동 (External Integration)

### 5.1. Google Cloud Compute Engine API
- **의존 서비스**: Google Cloud Compute Engine API v1
- **엔드포인트**: `https://compute.googleapis.com`
- **인증 방식**: Service Account 키 파일 기반 OAuth 2.0
- **API 할당량**: 프로젝트당 분당 2000 요청
- **장애 대응**: 
  - HTTP 429 (할당량 초과): 지수 백오프 재시도
  - HTTP 404 (리소스 없음): 정상 처리 (빈 결과 반환)
  - 기타 HTTP 오류: 로그 기록 후 다음 리소스 진행

## 6. 보안 & 컴플라이언스 (Security & Compliance)

### 6.1. 인증 및 인가
- **Google Cloud 인증**: Service Account 키 파일 기반 OAuth 2.0
- **필수 IAM 권한**:
  - `compute.instances.list`
  - `compute.instances.get`
  - `compute.disks.list`
  - `compute.snapshots.list`
  - `compute.images.list`
  - `compute.instanceTemplates.list`
  - `compute.instanceGroups.list`
- **권한 범위**: 프로젝트 수준 읽기 전용 권한

## 7. 운영 & 모니터링 (Operations & Monitoring)

### 7.1. 성능 메트릭
- **수집 성능**: 프로젝트당 평균 30초 이내 수집 완료
- **처리량**: 동시 10개 프로젝트 병렬 처리 지원
- **오류율**: 5% 미만 유지 목표
- **메트릭 수집**: 
  - `instance_count`: 프로젝트별 VM 인스턴스 개수
  - `disk_count`: 프로젝트별 디스크 개수
  - `total_disk_size_gb`: 총 디스크 용량 (GB)

## 8. 현재 구현 상태 (Implementation Status)

### 8.1. 구현 완료 기능
- ✅ **VMInstanceManager**: VM 인스턴스 수집 및 상세 정보
- ✅ **DiskManager**: 디스크 정보 수집
- ✅ **SnapshotManager**: 스냅샷 정보 수집
- ✅ **MachineImageManager**: 머신 이미지 정보 수집
- ✅ **InstanceTemplateManager**: 인스턴스 템플릿 수집
- ✅ **InstanceGroupManager**: 인스턴스 그룹 수집
- ✅ **다중 존/리전 지원**: 모든 가용 영역에서 리소스 수집
- ✅ **메타데이터**: SpaceONE 콘솔 UI 레이아웃, 위젯

### 8.2. 주요 구현 특징
- **존별 리소스 수집**: 각 가용 영역별로 독립적인 리소스 수집
- **관계형 데이터 연계**: VM 인스턴스와 디스크, 스냅샷 간의 관계 정보 포함
- **SpaceONE 모델 변환**: 수집된 모든 원시 데이터를 SpaceONE Cloud Service 모델 형식으로 변환
- **동적 UI 레이아웃**: 사용자가 수집된 리소스 정보를 쉽게 파악할 수 있는 UI 제공

### 8.3. 파일 구조
```
src/spaceone/inventory/
├── connector/compute_engine/
│   ├── __init__.py
│   └── compute_engine_v1.py        # Google Cloud Compute Engine API 연동
├── manager/compute_engine/
│   ├── __init__.py
│   ├── vm_instance_manager.py      # VM 인스턴스 비즈니스 로직
│   ├── disk_manager.py             # 디스크 비즈니스 로직
│   ├── snapshot_manager.py         # 스냅샷 비즈니스 로직
│   ├── machine_image_manager.py    # 머신 이미지 비즈니스 로직
│   ├── instance_template_manager.py # 인스턴스 템플릿 비즈니스 로직
│   └── instance_group_manager.py   # 인스턴스 그룹 비즈니스 로직
├── model/compute_engine/
│   ├── vm_instance/                # VM 인스턴스 모델
│   ├── disk/                       # 디스크 모델
│   ├── snapshot/                   # 스냅샷 모델
│   ├── machine_image/              # 머신 이미지 모델
│   ├── instance_template/          # 인스턴스 템플릿 모델
│   └── instance_group/             # 인스턴스 그룹 모델
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

- [Google Cloud Compute Engine API 문서](https://cloud.google.com/compute/docs/reference/rest/v1)
- [SpaceONE 플러그인 개발 가이드](https://cloudforet.io/docs/)
- [현재 구현 소스 코드](../../../../src/spaceone/inventory/)
