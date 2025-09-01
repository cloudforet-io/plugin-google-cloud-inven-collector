# Google Firebase 제품 요구사항 정의서

## 1. Asset Type 정의

- **수집 대상**: Google Cloud와 연결된 **Firebase Project**
- **Cloud Service Group**: `Firebase`
- **Cloud Service Type**: `Project`
- **Resource-ID Format**: `projects/{project_id}`

## 2. 수집 데이터 모델 정의

Firebase 프로젝트의 기본 정보와 상태를 수집합니다.

### 2.1. Cloud Service Group: `Firebase`

- **Group Name**: Firebase
- **Provider**: `google_cloud`

### 2.2. Cloud Service Type: `Project`

- **Service Code**: `Project`
- **Name**: Firebase Project
- **Group**: `Firebase`
- **Provider**: `google_cloud`
- **Metadata (View)**:
    - `google_cloud.yaml`
        - `search`:
            - `search_key: data.project_id`
            - `search_key: data.project_number`
            - `search_key: data.display_name`
            - `search_key: data.state`
        - `table`:
            - `layout`: `list`
            - `fields`:
                - `name`: `Name`
                - `data.project_id`: `Project ID`
                - `data.project_number`: `Project Number`
                - `data.state`: `State`
                - `data.create_time`: `Creation Time`

### 2.3. 수집 대상 리소스 및 데이터

#### 2.3.1. Firebase Project

| 필드명 | 데이터 타입 | 설명 |
| --- | --- | --- |
| project_id | `string` | Firebase 프로젝트의 고유 ID (GCP 프로젝트 ID와 동일) |
| project_number | `string` | Firebase 프로젝트의 고유 번호 |
| display_name | `string` | Firebase 프로젝트의 표시 이름 |
| name | `string` | Firebase 프로젝트의 리소스 이름 (`projects/{project_id}`) |
| state | `string` | 프로젝트의 생명주기 상태 (`ACTIVE`, `DELETED` 등) |
| resources | `object` | 프로젝트와 연결된 Firebase 관련 리소스 정보 (Hosting 사이트, Storage 버킷 등) |
| create_time | `datetime` | 프로젝트 생성 시간 |
| etag | `string` | 리소스의 ETag |

## 3. 수집 주기

- **주기**: 1시간

## 4. API 정보 및 권한

### 4.1. 사용 API

1.  **`firebase.projects.get`**: 특정 GCP 프로젝트에 연결된 Firebase 프로젝트의 상세 정보를 조회합니다.
    - **HTTP Request**: `GET https://firebase.googleapis.com/v1beta1/projects/{project_id}`

### 4.2. 필요 IAM 권한

- 수집을 위해서는 서비스 계정에 다음 역할이 필요합니다.
    - `roles/firebase.viewer` 또는 `roles/viewer`

## 5. Collector 구현 로직

1.  **GCP 프로젝트 기반 조회**:
    - SpaceONE에 등록된 GCP 프로젝트(`project_id`)를 기준으로 루프를 실행합니다.
2.  **Firebase 프로젝트 정보 수집**:
    - 각 `project_id`에 대해 `firebase.projects.get` API를 호출하여 연결된 Firebase 프로젝트 정보를 가져옵니다.
    - API 응답에서 `state`가 `ACTIVE`이고, Firebase 서비스가 활성화된(`hasFirebaseServices: true`) 프로젝트만 필터링합니다.
3.  **데이터 변환**:
    - 수집된 Firebase 프로젝트 정보를 SpaceONE의 `Cloud Service` 모델 형식에 맞게 변환하여 저장합니다.
