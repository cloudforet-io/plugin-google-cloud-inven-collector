# Google Cloud Batch 제품 요구사항 정의서

## 1. Asset Type 정의

- **수집 대상**: Google Cloud Batch 서비스의 **Job**
- **Cloud Service Group**: `Batch`
- **Cloud Service Type**: `Job`
- **Resource-ID Format**: `projects/{project_id}/locations/{location}/jobs/{job_id}`

## 2. 수집 데이터 모델 정의

Batch Job 리소스의 상세 정보를 수집하며, 각 Job에 속한 Task Group과 Task 정보를 포함합니다.

### 2.1. Cloud Service Group: `Batch`

- **Group Name**: Batch
- **Provider**: `google_cloud`

### 2.2. Cloud Service Type: `Job`

- **Service Code**: `Job`
- **Name**: Batch Job
- **Group**: `Batch`
- **Provider**: `google_cloud`
- **Metadata (View)**:
    - `google_cloud.yaml`
        - `search`:
            - `search_key: data.name`
            - `search_key: data.uid`
            - `search_key: data.status.state`
            - `search_key: data.create_time`
        - `table`:
            - `layout`: `list`
            - `fields`:
                - `name`: `Name`
                - `data.status.state`: `State`
                - `data.task_groups.task_count`: `Tasks`
                - `data.create_time`: `Creation Time`

### 2.3. 수집 대상 리소스 및 데이터

#### 2.3.1. Job

| 필드명 | 데이터 타입 | 설명 |
| --- | --- | --- |
| name | `string` | Job의 이름 (고유 식별자) |
| uid | `string` | Job의 고유 ID |
| priority | `integer` | Job의 우선순위 |
| status | `object` | Job의 현재 상태 (`QUEUED`, `SCHEDULED`, `RUNNING`, `SUCCEEDED`, `FAILED` 등) |
| task_groups | `list` | Job을 구성하는 Task Group의 목록 |
| allocation_policy | `object` | Job 실행을 위한 리소스 할당 정책 |
| logs_policy | `object` | 로그 저장 위치 및 정책 |
| create_time | `datetime` | Job 생성 시간 |
| update_time | `datetime` | Job 마지막 업데이트 시간 |

#### 2.3.2. Task (Job 내 포함)

| 필드명 | 데이터 타입 | 설명 |
| --- | --- | --- |
| name | `string` | Task의 이름 |
| status | `object` | Task의 현재 상태 |

## 3. 수집 주기

- **주기**: 1시간

## 4. API 정보 및 권한

### 4.1. 사용 API

1.  **`batch.projects.locations.jobs.list`**: 특정 프로젝트와 위치에 있는 모든 Batch Job 목록을 조회합니다.
    - **HTTP Request**: `GET https://batch.googleapis.com/v1/{parent=projects/*/locations/*}/jobs`
2.  **`batch.projects.locations.jobs.taskGroups.tasks.list`**: 특정 Job의 Task Group에 속한 모든 Task 목록을 조회합니다.
    - **HTTP Request**: `GET https://batch.googleapis.com/v1/{parent=projects/*/locations/*/jobs/*/taskGroups/*}/tasks`

### 4.2. 필요 IAM 권한

- 수집을 위해서는 서비스 계정에 다음 역할이 필요합니다.
    - `roles/batch.jobs.viewer` 또는 `roles/viewer`

## 5. Collector 구현 로직

1.  **Job 목록 수집**:
    - 활성화된 모든 GCP 프로젝트와 리전(location)에 대해 `batch.projects.locations.jobs.list` API를 호출하여 Job 목록을 가져옵니다.
2.  **Task 정보 수집**:
    - 각 Job에 대해 `taskGroups` 필드를 순회합니다.
    - 각 Task Group에 대해 `batch.projects.locations.jobs.taskGroups.tasks.list` API를 호출하여 해당 그룹에 속한 Task 목록을 가져옵니다.
3.  **데이터 조합 및 변환**:
    - 수집된 Job 정보와 각 Job에 속한 Task 정보를 조합합니다.
    - `task_count`와 같은 집계 정보를 계산합니다.
    - 최종적으로 SpaceONE의 `Cloud Service` 모델 형식에 맞게 데이터를 변환하여 저장합니다.
