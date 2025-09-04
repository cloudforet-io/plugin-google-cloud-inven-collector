# Google Cloud Build 리소스 수집기 요구사항 정의서 (플러그인 기반)

본 문서는 현재 `plugin-google-cloud-inven-collector` 플러그인에 구현된 Cloud Build 수집 기능의 요구사항을 명세한다. 수집된 데이터는 시스템의 인벤토리 정보로 활용되며, 단순 개수 수집 방식을 통해 대시보드에서 리소스 현황을 시각화하는 것을 목표로 한다.

✅ **현재 상태**: 버전별 완전 분리 아키텍처로 V1과 V2 API를 독립적으로 지원하며, 단순 개수 수집 방식으로 다른 Google Cloud 도메인과 일관된 메트릭 체계를 구축하여 안정적이고 유지보수 가능한 모니터링 시스템을 제공한다.

---

## 📚 참고 문서

### Google Cloud Build 공식 문서

- **[Cloud Build 개요](https://cloud.google.com/build/docs/overview)**: Cloud Build 서비스의 전반적인 개념과 기능 설명
- **[Cloud Build API Reference](https://cloud.google.com/build/docs/api/reference/rest)**: REST API 상세 명세 및 리소스 구조
- **[Build 구성 파일 참조](https://cloud.google.com/build/docs/build-config-file-schema)**: cloudbuild.yaml 파일 스키마
- **[트리거 관리](https://cloud.google.com/build/docs/automating-builds/create-manage-triggers)**: 빌드 트리거 생성 및 관리 가이드
- **[워커풀 관리](https://cloud.google.com/build/docs/private-pools/private-pools-overview)**: 비공개 워커풀 구성 및 관리

### API 리소스 상세 문서

- **[Builds API](https://cloud.google.com/build/docs/api/reference/rest/v1/projects.builds)**: 빌드 리소스 API 명세
- **[Triggers API](https://cloud.google.com/build/docs/api/reference/rest/v1/projects.triggers)**: 트리거 리소스 API 명세
- **[WorkerPools API](https://cloud.google.com/build/docs/api/reference/rest/v1/projects.locations.workerPools)**: 워커풀 리소스 API 명세
- **[Connections API](https://cloud.google.com/build/docs/api/reference/rest/v2/projects.locations.connections)**: SCM 연결 API 명세 (v2)
- **[Repositories API](https://cloud.google.com/build/docs/api/reference/rest/v2/projects.locations.connections.repositories)**: 저장소 API 명세 (v2)

---

## 🎯 수집 대상 리소스

현재 플러그인의 커넥터(`cloud_build_v1.py`, `cloud_build_v2.py`)는 아래 리소스의 수집 기능을 제공한다. 각 버전은 완전히 분리되어 독립적으로 작동하며, 확장성을 위해 버전 간 혼용을 금지한다.

### 🔄 버전별 지원 리소스 매트릭스

| 리소스 타입                  | V1 API 지원          | V2 API 지원      | 주요 특징 |
| ---------------------------- | -------------------- | ---------------- | --------- |
| **Build**                    | ✅ Global + Regional | ❌ 지원되지 않음 | V1 전용   |
| **Trigger**                  | ✅ Global + Regional | ❌ 지원되지 않음 | V1 전용   |
| **Worker Pool**              | ✅ Regional 만       | ❌ 지원되지 않음 | V1 전용   |
| **Connection**               | ❌ 지원되지 않음     | ✅ Regional 만   | V2 전용   |
| **Repository**               | ❌ 지원되지 않음     | ✅ Regional 만   | V2 전용   |
| **GitHub Enterprise Config** | ✅ Global + Regional | ❌ 지원되지 않음 | V1 전용   |
| **Bitbucket Server Config**  | ✅ Regional 만       | ❌ 지원되지 않음 | V1 전용   |
| **GitLab Config**            | ✅ Regional 만       | ❌ 지원되지 않음 | V1 전용   |
| **Location**                 | ❌ (fallback 사용)   | ✅ 주요 지원     | V2 전용   |

### 📋 버전 분리 원칙

1. **완전한 독립성**: V1 Manager는 V1 Connector만 사용, V2 Manager는 V2 Connector만 사용
2. **확장성 보장**: 새로운 API 버전 추가 시 기존 버전에 영향 없음
3. **테스트 가능성**: 각 버전별로 독립적인 API 엔드포인트 테스트 지원
4. **Fallback 처리**: V1에서 지원되지 않는 API는 대체 방법으로 기능 제공

### 2.1. Build (빌드 내역)

- **API (v1)**:
  - `projects.builds.list`: Global 리전의 빌드 내역을 조회한다.
  - `projects.locations.builds.list`: 특정 리전(regional)의 빌드 내역을 조회한다.
- **수집 목적**: 빌드 상태, 실행 시간, 사용 환경(머신 타입) 등의 데이터를 수집하여 빌드 현황을 파악한다.
- **리소스 구조**: [Build 리소스 스키마](https://cloud.google.com/build/docs/api/reference/rest/v1/projects.builds#Build)

### 2.2. Trigger (빌드 트리거)

- **API (v1)**:
  - `projects.triggers.list`: Global 리전의 트리거 목록을 조회한다.
  - `projects.locations.triggers.list`: 특정 리전의 트리거 목록을 조회한다.
- **수집 목적**: 자동화된 빌드의 구성 정보를 파악하고, 1세대(Gen 1) 방식으로 연동된 GitHub 저장소 정보를 간접적으로 수집한다.
- **리소스 구조**: [BuildTrigger 리소스 스키마](https://cloud.google.com/build/docs/api/reference/rest/v1/projects.triggers#BuildTrigger)

### 2.3. Worker Pool (워커풀)

- **API (v1)**:
  - `projects.locations.workerPools.list`: 특정 리전의 비공개 워커풀(Private Pool) 목록을 조회한다.
- **수집 목적**: 비공개 풀의 구성(머신 타입, 네트워크) 정보를 수집하여 빌드 환경을 파악한다.
- **리소스 구조**: [WorkerPool 리소스 스키마](https://cloud.google.com/build/docs/api/reference/rest/v1/projects.locations.workerPools#WorkerPool)

### 2.4. Location (리전 정보)

- **API (v2)**:
  - `projects.locations.list`: Cloud Build 서비스를 지원하는 전체 위치(리전) 목록을 조회한다.
- **V1 Fallback**: V1에서는 해당 API가 지원되지 않으므로 `REGION_INFO`를 사용한 fallback 처리
- **수집 목적**: 다른 리소스들을 조회할 리전 목록을 동적으로 생성하는 데 사용된다.
- **리소스 구조**: [Location 리소스 스키마](https://cloud.google.com/build/docs/api/reference/rest/v2/projects.locations#Location)

### 2.5. SCM Connection & Repository (2세대 연동 정보)

- **API (v2)**:
  - `projects.locations.connections.list`: 특정 리전의 SCM 연결(Connection) 목록을 조회한다.
  - `projects.locations.connections.repositories.list`: 특정 SCM 연결을 통해 접근 가능한 저장소(Repository) 목록을 조회한다.
- **수집 목적**: 2세대(Gen 2) 방식으로 연동된 소스 저장소의 구성 정보를 파악한다.
- **리소스 구조**:
  - [Connection 리소스 스키마](https://cloud.google.com/build/docs/api/reference/rest/v2/projects.locations.connections#Connection)
  - [Repository 리소스 스키마](https://cloud.google.com/build/docs/api/reference/rest/v2/projects.locations.connections.repositories#Repository)

### 2.6. GitHub Enterprise Config (GitHub 엔터프라이즈 연동)

- **API (v1)**:
  - `projects.githubEnterpriseConfigs.list`: Global 리전의 GitHub Enterprise 설정을 조회한다.
  - `projects.locations.githubEnterpriseConfigs.list`: 특정 리전의 GitHub Enterprise 설정을 조회한다.
- **수집 목적**: GitHub Enterprise Server와의 연동 설정 정보를 파악한다.
- **리소스 구조**: [GitHubEnterpriseConfig 리소스 스키마](https://cloud.google.com/build/docs/api/reference/rest/v1/projects.githubEnterpriseConfigs#GitHubEnterpriseConfig)

### 2.7. Bitbucket Server Config (Bitbucket 서버 연동)

- **API (v1)**:
  - `projects.locations.bitbucketServerConfigs.list`: 특정 리전의 Bitbucket Server 설정을 조회한다.
- **수집 목적**: Bitbucket Server와의 연동 설정 정보를 파악한다.
- **리소스 구조**: [BitbucketServerConfig 리소스 스키마](https://cloud.google.com/build/docs/api/reference/rest/v1/projects.locations.bitbucketServerConfigs#BitbucketServerConfig)

### 2.8. GitLab Config (GitLab 연동)

- **API (v1)**:
  - `projects.locations.gitLabConfigs.list`: 특정 리전의 GitLab 설정을 조회한다.
- **수집 목적**: GitLab과의 연동 설정 정보를 파악한다.
- **리소스 구조**: [GitLabConfig 리소스 스키마](https://cloud.google.com/build/docs/api/reference/rest/v1/projects.locations.gitLabConfigs#GitLabConfig)

---

## 📊 핵심 메트릭 정의 (단순 개수 수집 방식)

### 3.1. 메트릭 수집 방식

다른 Google Cloud 도메인과의 일관성을 위해 Cloud Build도 **단순 개수 수집 방식**을 사용한다. 이는 대시보드에서 리소스의 전체적인 현황을 파악하고 관리하는 데 초점을 맞춘다.

### 3.2. 구현된 메트릭 목록

| 메트릭 파일                                | 메트릭 이름            | 방식              | 지원 버전 | 분석 가능 요소                                 |
| :----------------------------------------- | :--------------------- | :---------------- | :-------- | :--------------------------------------------- |
| `Build/build_count.yaml`                   | Build Count            | `operator: count` | V1 전용   | 상태별, 트리거별, 리전별, 저장소별 빌드 수     |
| `Build/build_count_by_status.yaml`         | Build Count by Status  | `operator: count` | V1 전용   | 빌드 상태별 대시보드 시각화 (성공/실패/진행중) |
| `Trigger/trigger_count.yaml`               | Trigger Count          | `operator: count` | V1 전용   | 트리거 수 및 설정 현황                         |
| `Trigger/trigger_status.yaml`              | Active Trigger Count   | `operator: count` | V1 전용   | 활성/비활성 트리거 수                          |
| `Connection/connection_count.yaml`         | Connection Count       | `operator: count` | V2 전용   | SCM 연결 수 (2세대)                            |
| `Repository/repository_count.yaml`         | Repository Count       | `operator: count` | V2 전용   | 연결된 저장소 수 (2세대)                       |
| `WorkerPool/worker_pool_count.yaml`        | WorkerPool Count       | `operator: count` | V1 전용   | 비공개 워커풀 수                               |
| `GitHubEnterpriseConfig/config_count.yaml` | GitHub Config Count    | `operator: count` | V1 전용   | GitHub Enterprise 연동 설정 수                 |
| `BitbucketServerConfig/config_count.yaml`  | Bitbucket Config Count | `operator: count` | V1 전용   | Bitbucket Server 연동 설정 수                  |
| `GitLabConfig/config_count.yaml`           | GitLab Config Count    | `operator: count` | V1 전용   | GitLab 연동 설정 수                            |

### 3.3. 메트릭 활용 방안

단순 개수 수집 방식으로도 다양한 대시보드 분석이 가능하다:

- **빌드 현황 모니터링**: 전체 빌드 수, 상태별 분포
- **트리거 관리**: 활성/비활성 트리거 현황
- **리소스 현황**: 워커풀, 연결, 저장소 수
- **리전별 분석**: 지역별 리소스 분포
- **프로젝트별 분석**: 프로젝트 간 비교 분석

**장점:**

- 다른 Google Cloud 도메인과 일관된 메트릭 방식
- 단순하고 안정적인 메트릭 수집
- 대시보드에서 직관적인 리소스 현황 파악

---

## 🏗️ 현재 구현 상세 분석

### 4.1. 버전별 아키텍처 분리

#### 4.1.1. V1 아키텍처 (Legacy 및 Core 리소스)

- **담당 리소스**: Build, Trigger, Worker Pool, SCM Configs (GitHub/Bitbucket/GitLab)
- **특징**: Global + Regional API 지원, 1세대 SCM 연동 방식
- **Connector**: `CloudBuildV1Connector`
- **Manager들**:
  - `CloudBuildBuildManagerV1`
  - `CloudBuildTriggerManagerV1`
  - `CloudBuildWorkerPoolManagerV1`
  - `CloudBuildGitHubEnterpriseConfigManagerV1`
  - `CloudBuildBitbucketServerConfigManagerV1`
  - `CloudBuildGitLabConfigManagerV1`

#### 4.1.2. V2 아키텍처 (Modern SCM 연동)

- **담당 리소스**: Connection, Repository, Location
- **특징**: Regional API 중심, 2세대 SCM 연동 방식
- **Connector**: `CloudBuildV2Connector`
- **Manager들**:
  - `CloudBuildConnectionManagerV2`
  - `CloudBuildRepositoryManagerV2`

#### 4.1.3. API 테스트 기능

각 Connector는 `test_api_endpoints()` 메서드를 제공하여 실제 API 사용 가능 여부를 동적으로 확인할 수 있다:

- **V1 테스트**: Global/Regional Builds, Triggers, Worker Pools, SCM Configs
- **V2 테스트**: Locations, Connections, Repositories

### 4.3. API 엔드포인트 실제 테스트 결과

아래는 Cloud Build API 엔드포인트들의 실제 지원 여부와 테스트 결과입니다:

| API 리소스                    | API 경로                                           | V1 지원                   | V2 지원      | 테스트 결과  | 비고    |
| ----------------------------- | -------------------------------------------------- | ------------------------- | ------------ | ------------ | ------- |
| **Global Builds**             | `projects.builds.list`                             | ✅ 지원                   | ❌ 미지원    | ✅ 사용 가능 | V1 전용 |
| **Global Triggers**           | `projects.triggers.list`                           | ✅ 지원                   | ❌ 미지원    | ✅ 사용 가능 | V1 전용 |
| **Locations**                 | `projects.locations.list`                          | ❌ 미지원 (fallback 사용) | ✅ 주요 지원 | ✅ 사용 가능 | V2 전용 |
| **Regional Builds**           | `projects.locations.builds.list`                   | ✅ 지원                   | ❌ 미지원    | ✅ 사용 가능 | V1 전용 |
| **Regional Triggers**         | `projects.locations.triggers.list`                 | ✅ 지원                   | ❌ 미지원    | ✅ 사용 가능 | V1 전용 |
| **Worker Pools**              | `projects.locations.workerPools.list`              | ✅ 지원                   | ❌ 미지원    | ✅ 사용 가능 | V1 전용 |
| **Connections**               | `projects.locations.connections.list`              | ❌ 미지원                 | ✅ 지원      | ✅ 사용 가능 | V2 전용 |
| **Repositories**              | `projects.locations.connections.repositories.list` | ❌ 미지원                 | ✅ 지원      | ✅ 사용 가능 | V2 전용 |
| **GitHub Enterprise Configs** | `projects.githubEnterpriseConfigs.list`            | ✅ 지원                   | ❌ 미지원    | ✅ 사용 가능 | V1 전용 |
| **Regional GitHub Configs**   | `projects.locations.githubEnterpriseConfigs.list`  | ✅ 지원                   | ❌ 미지원    | ✅ 사용 가능 | V1 전용 |
| **Bitbucket Server Configs**  | `projects.locations.bitbucketServerConfigs.list`   | ✅ 지원                   | ❌ 미지원    | ✅ 사용 가능 | V1 전용 |
| **GitLab Configs**            | `projects.locations.gitLabConfigs.list`            | ✅ 지원                   | ❌ 미지원    | ✅ 사용 가능 | V1 전용 |

#### 테스트 결과 요약

- **총 API 수**: 12개
- **V1에서 지원**: 9개 (75.0%)
- **V2에서 지원**: 3개 (25.0%)
- **전체 사용 가능**: 12개 (100%) - V1 fallback 포함
- **버전별 완전 분리**: ✅ 달성

#### 주요 발견사항

1. **V1 API의 핵심 기능 지원**: 빌드, 트리거, 워커풀 등 핵심 리소스는 V1에서 완전 지원
2. **V2 API의 특화된 역할**: 2세대 SCM 연동 (Connection/Repository)과 Location API에 특화
3. **Fallback 메커니즘**: V1에서 Locations API 미지원 시 REGION_INFO를 활용한 우회 처리
4. **완전한 버전 분리**: 각 API가 특정 버전에서만 지원되어 혼용 없음
5. **안정적인 API 접근**: Fallback을 포함하여 모든 주요 Cloud Build 리소스에 대한 접근 보장

### 4.2. 수집 대상 리소스별 현재 구현 (Manager 및 Connector)

- **사용 라이브러리**: `google-api-python-client`를 기반으로 한 `GoogleCloudConnector`를 사용한다.
- **리소스 조회 방식**: `global` API와 `regional` API를 모두 호출하는 방식을 사용한다. 전체 리소스 수집을 위해서는 아래 두 단계를 모두 수행해야 한다.
  1. Global API 호출: `projects.builds.list`, `projects.triggers.list`를 각각 호출하여 `global` 리전의 리소스를 수집한다.
  2. Regional API 호출: `projects.locations.list` (v2)를 통해 전체 리전 목록을 가져온 후, 각 리전을 순회하며 `projects.locations.builds.list`, `projects.locations.triggers.list` 등을 호출하여 각 리전의 리소스를 수집한다.
- **페이지네이션 처리**: 각 커넥터 메소드 내부에 `while request is not None` 루프와 `list_next(request, response)`를 사용하여, 모든 페이지의 결과를 수집하도록 구현되어 있다.
- **SCM 연동 방식 처리**: 1세대와 2세대 저장소를 모두 수집할 수 있도록 v1과 v2 커넥터에 필요한 메소드가 각각 구현되어 있다.
  1. **1세대(Gen 1)**: `cloud_build_v1.py`의 `list_triggers` 또는 `list_location_triggers`를 통해 수집된 정보에서 `github` 필드를 분석한다.
  2. **2세대(Gen 2)**: `cloud_build_v2.py`의 `list_connections`와 `list_repositories`를 순차적으로 호출하여 수집한다.

#### Build (빌드 내역)

- **Manager**: `CloudBuildBuildManager`
- **Connector**: `CloudBuildV1Connector`
- **수집 방식**: Global API + Regional API 순차 호출
- **데이터 모델**: 충분한 필드 보유 (시간 정보, 상태, 트리거 ID 등)
- **메트릭 구현**: `build_count.yaml`, `build_count_by_status.yaml` (상태별 카운트)

#### Trigger (빌드 트리거)

- **Manager**: `CloudBuildTriggerManager`
- **Connector**: `CloudBuildV1Connector`
- **수집 방식**: Global API + Regional API 순차 호출
- **데이터 모델**: 트리거 설정 정보, 활성화 상태 등 보유
- **메트릭 구현**: `trigger_count.yaml`, `trigger_status.yaml`

#### Worker Pool (워커풀)

- **Manager**: `CloudBuildWorkerPoolManager`
- **Connector**: `CloudBuildV1Connector`
- **수집 방식**: Regional API만 호출 (Global 없음)
- **데이터 모델**: 워커풀 구성 정보
- **메트릭 구현**: `worker_pool_count.yaml`

#### Connection & Repository (2세대 연동)

- **Manager**: `CloudBuildConnectionManager`, `CloudBuildRepositoryManager`
- **Connector**: `CloudBuildV2Connector`
- **수집 방식**: 리전별 Connection 조회 → 각 Connection별 Repository 조회
- **데이터 모델**: SCM 연결 정보 및 저장소 목록
- **메트릭 구현**: `connection_count.yaml`, `repository_count.yaml`

### 4.2. 메트릭 구현 현황

#### 현재 상태

- **모든 메트릭**: 단순 개수 카운트 방식으로 일관되게 구현
- **데이터 수집**: 모든 필요 리소스 정보가 완전히 수집됨
- **대시보드 활용**: 다양한 그룹화 옵션으로 세분화된 분석 가능

#### 장점

- **일관성**: 다른 Google Cloud 도메인과 동일한 메트릭 방식
- **안정성**: 단순한 카운트 방식으로 오류 가능성 최소화
- **유지보수성**: 메트릭 정의가 단순하여 유지보수 용이

---

## 🚀 개선 권장사항

### 6.1. 수정 완료 사항

1. **버전별 완전 분리 아키텍처 구현**

   - V1과 V2 Connector/Manager 간 완전한 독립성 확보
   - 버전 혼용 방지로 확장성 및 유지보수성 향상
   - 각 버전별 API 엔드포인트 테스트 기능 추가

2. **추가 리소스 지원 확대**

   - GitHub Enterprise Config, Bitbucket Server Config, GitLab Config 지원 추가
   - SCM 연동 설정의 완전한 가시성 확보

3. **모든 메트릭 검증 완료**
   - 10개 메트릭 모두 `operator: count` 방식 사용
   - 다른 Google Cloud 도메인과 일관된 패턴

### 6.2. 메트릭 활용 가이드

1. **대시보드 구성**

   - 상태별 빌드 수 차트 (성공/실패/진행중)
   - 리전별 리소스 분포 지도
   - 트리거 활성화 현황 표

2. **모니터링 지표**
   - 전체 빌드 수 추이
   - 프로젝트별 빌드 비중
   - 워커풀 사용 현황

### 6.3. API 테스트 및 검증 방법

실제 환경에서 API 엔드포인트 사용 가능 여부를 테스트하려면:

```bash
# 환경변수 설정
export GOOGLE_CLOUD_PROJECT='your-project-id'
export GOOGLE_APPLICATION_CREDENTIALS='/path/to/service-account.json'

# API 테스트 실행
python test_cloud_build_api_endpoints.py
```

#### 테스트 스크립트 기능

- **V1 API 테스트**: 모든 V1 엔드포인트의 실제 호출 및 응답 검증
- **V2 API 테스트**: 모든 V2 엔드포인트의 실제 호출 및 응답 검증
- **결과 분석**: 각 API의 지원 여부, 수집된 리소스 개수, 오류 정보 제공
- **테이블 생성**: 마크다운 형태의 API 지원 매트릭스 자동 생성

#### 출력 결과

1. **콘솔 출력**: 실시간 테스트 진행 상황과 결과 요약
2. **JSON 파일**: `cloud_build_api_test_results.json`에 상세 테스트 결과 저장
3. **마크다운 테이블**: API 지원 매트릭스를 테이블 형태로 출력

테스트 결과를 통해 실제 환경에서 사용 가능한 API들을 확인하고, 수집 가능한 리소스의 개수를 파악할 수 있다.

### 6.4. 현재 상태 요약

- **아키텍처**: ✅ 버전별 완전 분리 (V1/V2 독립성 확보)
- **수집 기능**: ✅ 완전 구현 (모든 Cloud Build 리소스 수집)
- **데이터 모델**: ✅ 충분 (모든 리소스 정보 완전 수집)
- **메트릭 구현**: ✅ 완료 (10개 메트릭, 단순 개수 수집 방식)
- **테스트 가능성**: ✅ 높음 (API 엔드포인트 동적 테스트 지원)
- **확장성**: ✅ 우수 (버전별 분리로 향후 API 변경에 유연 대응)
- **대시보드 활용도**: ✅ 높음 (다양한 그룹화 옵션으로 세분화된 분석 가능)

**결론**: 버전별 완전 분리 아키텍처와 단순 개수 수집 방식으로 다른 Google Cloud 도메인과 일관된 메트릭 체계를 구축하여 안정적이고 확장 가능하며 유지보수 가능한 모니터링 시스템을 제공한다.

---

## 📋 관련 리소스

### 구현 파일

- **플러그인 설정**: `src/spaceone/inventory/conf/cloud_service_conf.py`
- **데이터 모델**: `src/spaceone/inventory/model/cloud_build/`
- **커넥터**:
  - `src/spaceone/inventory/connector/cloud_build/cloud_build_v1.py`
  - `src/spaceone/inventory/connector/cloud_build/cloud_build_v2.py`
- **매니저**: `src/spaceone/inventory/manager/cloud_build/`
  - V1 Manager들: `*_manager_v1.py`
  - V2 Manager들: `*_manager_v2.py`
  - Legacy Manager들: `*_manager.py`
- **메트릭**: `src/spaceone/inventory/metrics/CloudBuild/`

### 테스트 도구

- **API 테스트 스크립트**: `test_cloud_build_api_endpoints.py`
  - V1/V2 모든 엔드포인트 실제 호출 테스트
  - 마크다운 테이블 형태 결과 출력
  - 상세한 오류 분석 및 리포팅
- **테스트 결과**: `cloud_build_api_test_results.json`
  - JSON 형태의 상세 테스트 결과
  - API별 지원 여부, 수집 개수, 오류 정보
  - 테스트 요약 통계

### 문서

- **PRD**: `docs/ko/prd/cloud_build/README.md` (본 문서)
- **API 참조**: [Cloud Build API Reference](https://cloud.google.com/build/docs/api/reference/rest)
