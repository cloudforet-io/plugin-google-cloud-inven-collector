# Google Cloud Inventory Collector Plugin

Language: [English](README.md) | [한국어](README_KR.md)

SpaceONE의 GCP(Google Cloud Platform) Inventory Collector 플러그인입니다. Inventory 플러그인은 구글 클라우드의 자원 정보를 자동 수집합니다.

## 목차 (Table of Contents)

1. [개요](#개요)
2. [플러그인 설정 및 배포 가이드](#플러그인-설정-및-배포-가이드)
3. [수집 대상 서비스](#수집-대상-서비스)
4. [GCP 서비스 엔드포인트](#gcp-서비스-엔드포인트)
5. [지원 리전 목록](#지원-리전-목록)
6. [서비스 목록](#서비스-목록)
7. [인증 개요](#인증-개요)
8. [IAM 권한 설정](#iam-권한-설정)
9. [자동 권한 설정 스크립트](#자동-권한-설정-스크립트)
10. [Secret Data 구성](#secret-data-구성)
11. [제품 요구사항 정의서 (PRD)](#제품-요구사항-정의서-prd)
12. [입력 파라미터](#입력-파라미터)

## 개요

이 문서는 SpaceONE Google Cloud Inventory Collector 플러그인에서 지원하는 Google Cloud 서비스들의 리소스 수집 방법과 구현 가이드를 제공합니다.

## 플러그인 설정 및 배포 가이드

### 1단계: Repository에 플러그인 등록

SpaceONE이 컨테이너 이미지를 플러그인으로 인식할 수 있도록 Repository 서비스에 등록합니다.


1.1 플러그인 등록 YAML 파일 생성

배포 환경에 따라 registry_type과 image 경로를 적절히 수정해야 합니다.


```yaml
# register_plugin.yaml
capability: {}
image: plugin-google-cloud-inven-collector
labels:
- Compute Engine
- Networking
- Cloud SQL
name: plugin-google-cloud-inven-collector
plugin_id: plugin-google-cloud-inven-collector
provider: google_cloud
registry_config:
  image_pull_secret: aramco-gcr-json-key
  url: asia-northeast3-docker.pkg.dev/mkkang-project/mkkang-repository
registry_type: GCP_PRIVATE_GCR
resource_type: inventory.Collector
tags: {}
```

#### 1.2 플러그인 등록

```bash
spacectl exec create repository.Plugin -f register_plugin.yaml
```


## 수집 대상 서비스

이 플러그인은 다음 Google Cloud 서비스들의 리소스를 수집합니다:

### 컴퓨팅 서비스
- **Compute Engine**: 가상 머신 인스턴스 및 관련 리소스 (VM Instance, Disk, Snapshot, Machine Image, Instance Template, Instance Group)
- **App Engine**: 완전 관리형 서버리스 플랫폼 (Application, Service, Version, Instance)
- **Kubernetes Engine (GKE)**: 관리형 Kubernetes 클러스터 서비스 (Cluster, Node Pool, Node, Node Group)
- **Cloud Run**: 컨테이너 기반 서버리스 플랫폼 (Service, Job, Execution, Task, Revision)
- **Cloud Functions**: 이벤트 기반 서버리스 함수 (1세대, 2세대)

### 데이터 및 스토리지 서비스
- **Cloud Storage**: 객체 스토리지 서비스 (Bucket, Object)
- **Cloud SQL**: 관리형 관계형 데이터베이스 (Instance, Database, User, Backup)
- **BigQuery**: 데이터 웨어하우스 및 분석 서비스 (Dataset, Table, Job)
- **Filestore**: 관리형 NFS 파일 시스템 (Instance, Backup, Snapshot)
- **Firestore**: NoSQL 문서 데이터베이스 (Database, Collection, Index, Backup)
- **Datastore**: NoSQL 문서 데이터베이스 (Database, Index, Namespace)

### 데이터 처리 및 분석
- **Dataproc**: 관리형 Apache Spark 및 Hadoop 서비스
- **Batch**: 배치 작업 처리 서비스
- **Storage Transfer**: 데이터 전송 서비스

### 개발 도구 및 CI/CD
- **Cloud Build**: 지속적 통합/배포 서비스
- **Firebase**: 모바일 및 웹 애플리케이션 개발 플랫폼

### 네트워킹 및 보안
- **Networking**: 네트워크 리소스 (VPC Network, Subnet, Firewall, External IP, Load Balancer, Route, VPN Gateway)
- **KMS (Key Management Service)**: 암호화 키 관리 서비스 (KeyRing, CryptoKey, CryptoKeyVersion)

### 메시징 및 통합
- **Pub/Sub**: 메시징 서비스 (Topic, Subscription, Schema, Snapshot)

## GCP 서비스 엔드포인트

각 Google Cloud 서비스는 다음과 같은 API 엔드포인트를 사용합니다:

| 서비스 | API 엔드포인트 | API 버전 |
|--------|---------------|----------|
| App Engine | `https://appengine.googleapis.com` | v1, v1beta |
| Kubernetes Engine | `https://container.googleapis.com` | v1, v1beta1 |
| Compute Engine | `https://compute.googleapis.com` | v1 |
| Cloud Run | `https://run.googleapis.com` | v1, v2 |
| Cloud Storage | `https://storage.googleapis.com` | v1 |
| Cloud SQL | `https://sqladmin.googleapis.com` | v1 |
| BigQuery | `https://bigquery.googleapis.com` | v2 |
| Dataproc | `https://dataproc.googleapis.com` | v1 |
| Cloud Build | `https://cloudbuild.googleapis.com` | v1, v2 |
| Filestore | `https://file.googleapis.com` | v1, v1beta1 |
| Firestore | `https://firestore.googleapis.com` | v1 |
| Datastore | `https://datastore.googleapis.com` | v1 |
| Firebase | `https://firebase.googleapis.com` | v1beta1 |
| KMS | `https://cloudkms.googleapis.com` | v1 |
| Batch | `https://batch.googleapis.com` | v1 |
| Storage Transfer | `https://storagetransfer.googleapis.com` | v1 |

## 지원 리전 목록

이 플러그인은 다음 Google Cloud 리전에서 리소스를 수집할 수 있습니다:

### 아시아 태평양 지역
- `asia-east1` (대만)
- `asia-east2` (홍콩)
- `asia-northeast1` (도쿄)
- `asia-northeast2` (오사카)
- `asia-northeast3` (서울)
- `asia-south1` (뭄바이)
- `asia-south2` (델리)
- `asia-southeast1` (싱가포르)
- `asia-southeast2` (자카르타)

### 유럽 지역
- `europe-central2` (바르샤바)
- `europe-north1` (핀란드)
- `europe-southwest1` (마드리드)
- `europe-west1` (벨기에)
- `europe-west2` (런던)
- `europe-west3` (프랑크푸르트)
- `europe-west4` (네덜란드)
- `europe-west6` (취리히)
- `europe-west8` (밀라노)
- `europe-west9` (파리)

### 북미 지역
- `northamerica-northeast1` (몬트리올)
- `northamerica-northeast2` (토론토)
- `us-central1` (아이오와)
- `us-east1` (사우스캐롤라이나)
- `us-east4` (북버지니아)
- `us-east5` (콜럼버스)
- `us-south1` (댈러스)
- `us-west1` (오레곤)
- `us-west2` (로스앤젤레스)
- `us-west3` (솔트레이크시티)
- `us-west4` (라스베이거스)

### 남미 지역
- `southamerica-east1` (상파울루)
- `southamerica-west1` (산티아고)

### 기타 지역
- `australia-southeast1` (시드니)
- `australia-southeast2` (멜버른)
- `me-central1` (도하)
- `me-west1` (텔아비브)

### 글로벌 리소스
- `global` (전역 리소스용)

## 서비스 목록

현재 구현된 서비스별 상세 정보:

### 1. Compute Engine
- **설명**: Google Cloud의 가상 머신 컴퓨팅 서비스
- **수집 리소스**: VM Instance, Disk, Snapshot, Machine Image, Instance Template, Instance Group
- **API 버전**: v1
- **문서**: [Compute Engine 가이드](./prd/compute_engine/README.md)

### 2. App Engine
- **설명**: Google Cloud의 완전 관리형 서버리스 플랫폼
- **수집 리소스**: Application, Service, Version, Instance
- **API 버전**: v1, v1beta (하위 호환성)
- **문서**: [App Engine 가이드](./prd/app_engine/README.md)

### 3. Kubernetes Engine (GKE)
- **설명**: Google Cloud의 관리형 Kubernetes 클러스터 서비스
- **수집 리소스**: Cluster, Node Pool, Node, Node Group
- **API 버전**: v1, v1beta (하위 호환성)
- **문서**: [Kubernetes Engine 가이드](./prd/kubernetes_engine/README.md)

### 4. Cloud Run
- **설명**: 컨테이너 기반 서버리스 플랫폼
- **수집 리소스**: Service, Job, Execution, Task, Revision, Worker Pool, Domain Mapping
- **API 버전**: v1, v2 (버전별 완전 분리)
- **문서**: [Cloud Run 가이드](./prd/cloud_run/README.md)

### 5. Cloud Functions
- **설명**: 이벤트 기반 서버리스 함수 서비스
- **수집 리소스**: Function (1세대, 2세대), Trigger, Environment Variables
- **API 버전**: v1, v2 (세대별 완전 분리)
- **문서**: [Cloud Functions 가이드](./prd/cloud_functions/README.md)

### 6. Cloud Storage
- **설명**: 객체 스토리지 서비스
- **수집 리소스**: Bucket, Lifecycle Policy, IAM Policy, Encryption Settings
- **API 버전**: v1
- **문서**: [Cloud Storage 가이드](./prd/cloud_storage/README.md)

### 7. Cloud SQL
- **설명**: 관리형 관계형 데이터베이스 서비스
- **수집 리소스**: Instance, Database, User, Backup Configuration
- **API 버전**: v1
- **문서**: [Cloud SQL 가이드](./prd/cloud_sql/README.md)

### 8. BigQuery
- **설명**: 데이터 웨어하우스 및 분석 서비스
- **수집 리소스**: Dataset, Table, View, Job, Schema
- **API 버전**: v2
- **문서**: [BigQuery 가이드](./prd/bigquery/README.md)

### 9. Cloud Build
- **설명**: 지속적 통합/배포 서비스
- **수집 리소스**: Build, Trigger, Worker Pool, Connection, Repository
- **API 버전**: v1, v2 (버전별 완전 분리)
- **문서**: [Cloud Build 가이드](./prd/cloud_build/README.md)

### 10. Dataproc
- **설명**: 관리형 Apache Spark 및 Hadoop 서비스
- **수집 리소스**: Cluster, Job, Workflow Template, Autoscaling Policy
- **API 버전**: v1
- **문서**: [Dataproc 가이드](./prd/dataproc/README.md)

### 11. Filestore
- **설명**: 관리형 NFS 파일 시스템
- **수집 리소스**: Instance, Backup, Snapshot
- **API 버전**: v1, v1beta1
- **문서**: [Filestore 가이드](./prd/filestore/README.md)

### 12. Firestore
- **설명**: NoSQL 문서 데이터베이스
- **수집 리소스**: Database, Collection, Index, Backup
- **API 버전**: v1
- **문서**: [Firestore 가이드](./prd/firestore/README.md)

### 13. Datastore
- **설명**: NoSQL 문서 데이터베이스 (Datastore 모드)
- **수집 리소스**: Database, Index, Namespace
- **API 버전**: v1
- **문서**: [Datastore 가이드](./prd/datastore/README.md)

### 14. Networking
- **설명**: 네트워크 인프라 서비스
- **수집 리소스**: VPC Network, Subnet, Firewall, External IP, Load Balancer, Route, VPN Gateway
- **API 버전**: v1
- **문서**: [Networking 가이드](./prd/networking/README.md)

### 15. KMS (Key Management Service)
- **설명**: 암호화 키 관리 서비스
- **수집 리소스**: KeyRing, CryptoKey, CryptoKeyVersion
- **API 버전**: v1
- **문서**: [KMS 가이드](./prd/kms/README.md)

### 16. Pub/Sub
- **설명**: 메시징 및 이벤트 스트리밍 서비스
- **수집 리소스**: Topic, Subscription, Schema, Snapshot
- **API 버전**: v1
- **문서**: [Pub/Sub 가이드](./prd/pubsub/README.md)

### 17. Firebase
- **설명**: 모바일 및 웹 애플리케이션 개발 플랫폼
- **수집 리소스**: Project
- **API 버전**: v1beta1
- **문서**: [Firebase 가이드](./prd/firebase/Google Firebase 제품 요구사항 정의서.md)

### 18. Batch
- **설명**: 배치 작업 처리 서비스
- **수집 리소스**: Job, Task
- **API 버전**: v1
- **문서**: [Batch 가이드](./prd/batch/Google Cloud Batch 제품 요구사항 정의서.md)

### 19. Storage Transfer
- **설명**: 데이터 전송 서비스
- **수집 리소스**: Transfer Job, Transfer Operation, Agent Pool, Service Account
- **API 버전**: v1
- **문서**: [Storage Transfer 가이드](./prd/storage_transfer/README.md)

## 인증 개요

Google Cloud Inventory Collector는 Google Cloud API에 접근하기 위해 Service Account 기반 인증을 사용합니다.

### 인증 방식
- **Service Account 키 파일**: JSON 형식의 Service Account 키 파일을 사용
- **OAuth 2.0**: Google Cloud API 표준 인증 방식
- **스코프**: `https://www.googleapis.com/auth/cloud-platform` (전체 Google Cloud 플랫폼 접근)

### 인증 흐름
1. Service Account 키 파일을 SpaceONE Secret에 등록
2. 플러그인이 키 파일을 사용하여 Google Cloud API에 인증
3. 각 서비스별 필요한 IAM 권한 확인
4. API 호출을 통한 리소스 수집

## IAM 권한 설정

각 Google Cloud 서비스별로 필요한 최소 IAM 권한은 다음과 같습니다:

### 기본 권한 (모든 서비스 공통)
```json
{
  "roles": [
    "roles/viewer",
    "roles/browser"
  ]
}
```

### 서비스별 세부 권한

#### App Engine
```json
{
  "permissions": [
    "appengine.applications.get",
    "appengine.services.list",
    "appengine.versions.list",
    "appengine.instances.list"
  ]
}
```

#### Kubernetes Engine (GKE)
```json
{
  "permissions": [
    "container.clusters.list",
    "container.clusters.get",
    "container.nodePools.list",
    "container.nodePools.get",
    "container.nodes.list"
  ]
}
```

#### Cloud Run
```json
{
  "permissions": [
    "run.services.list",
    "run.services.get",
    "run.jobs.list",
    "run.executions.list",
    "run.tasks.list",
    "run.revisions.list"
  ]
}
```

#### Cloud Build
```json
{
  "permissions": [
    "cloudbuild.builds.list",
    "cloudbuild.triggers.list",
    "cloudbuild.workerpools.list",
    "source.repos.list"
  ]
}
```

#### Dataproc
```json
{
  "permissions": [
    "dataproc.clusters.list",
    "dataproc.clusters.get",
    "dataproc.jobs.list",
    "dataproc.workflowTemplates.list",
    "dataproc.autoscalingPolicies.list"
  ]
}
```

#### Storage & Database Services
```json
{
  "permissions": [
    "storage.buckets.list",
    "storage.objects.list",
    "file.instances.list",
    "datastore.databases.list",
    "datastore.indexes.list",
    "datastore.entities.list"
  ]
}
```

#### KMS
```json
{
  "permissions": [
    "cloudkms.keyRings.list",
    "cloudkms.cryptoKeys.list",
    "cloudkms.cryptoKeyVersions.list"
  ]
}
```

## 자동 권한 설정 스크립트

다음 스크립트를 사용하여 필요한 IAM 권한을 자동으로 설정할 수 있습니다:

### 1. Service Account 생성 및 권한 부여
```bash
#!/bin/bash

# 변수 설정
PROJECT_ID="your-project-id"
SERVICE_ACCOUNT_NAME="spaceone-collector"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
KEY_FILE="spaceone-collector-key.json"

# Service Account 생성
gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME} \
    --display-name="SpaceONE Inventory Collector" \
    --description="Service account for SpaceONE Google Cloud inventory collection" \
    --project=${PROJECT_ID}

# 기본 권한 부여
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/viewer"

# 서비스별 권한 부여
ROLES=(
    "roles/appengine.appViewer"
    "roles/container.viewer"
    "roles/run.viewer"
    "roles/cloudbuild.builds.viewer"
    "roles/dataproc.viewer"
    "roles/storage.objectViewer"
    "roles/file.viewer"
    "roles/datastore.viewer"
    "roles/cloudkms.viewer"
    "roles/firebase.viewer"
)

for role in "${ROLES[@]}"; do
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="${role}"
done

# Service Account 키 파일 생성
gcloud iam service-accounts keys create ${KEY_FILE} \
    --iam-account=${SERVICE_ACCOUNT_EMAIL} \
    --project=${PROJECT_ID}

echo "Service Account 설정이 완료되었습니다."
echo "키 파일: ${KEY_FILE}"
echo "Service Account Email: ${SERVICE_ACCOUNT_EMAIL}"
```

### 2. API 활성화 스크립트
```bash
#!/bin/bash

PROJECT_ID="your-project-id"

# 필요한 API 목록
APIS=(
    "appengine.googleapis.com"
    "container.googleapis.com"
    "run.googleapis.com"
    "cloudbuild.googleapis.com"
    "dataproc.googleapis.com"
    "storage.googleapis.com"
    "file.googleapis.com"
    "datastore.googleapis.com"
    "cloudkms.googleapis.com"
    "firebase.googleapis.com"
    "batch.googleapis.com"
    "storagetransfer.googleapis.com"
    "compute.googleapis.com"
)

# API 활성화
for api in "${APIS[@]}"; do
    echo "Enabling ${api}..."
    gcloud services enable ${api} --project=${PROJECT_ID}
done

echo "모든 API가 활성화되었습니다."
```

## Secret Data 구성

SpaceONE에서 Google Cloud Inventory Collector를 사용하기 위한 Secret Data 구성 방법입니다.

### Secret Data 형식
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "spaceone-collector@your-project-id.iam.gserviceaccount.com",
  "client_id": "client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/spaceone-collector%40your-project-id.iam.gserviceaccount.com"
}
```

### SpaceONE Console에서 Secret 등록
1. **Asset > Service Account** 메뉴로 이동
2. **+ Create** 버튼 클릭
3. **Provider**: `Google Cloud` 선택
4. **Secret Data**: 위의 JSON 형식으로 Service Account 키 파일 내용 입력
5. **Save** 버튼으로 저장

### CLI를 통한 Secret 등록
```bash
# spacectl을 사용한 Secret 등록
spacectl exec register secret.secret \
    -p name="google-cloud-sa" \
    -p provider="google_cloud" \
    -p secret_type="CREDENTIALS" \
    -p data=@service-account-key.json
```

## 제품 요구사항 정의서 (PRD)

각 Google Cloud 서비스별 상세한 제품 요구사항 정의서는 다음 링크에서 확인할 수 있습니다:

### 컴퓨팅 서비스
- [App Engine PRD](./prd/app_engine/README.md) - 서버리스 애플리케이션 플랫폼
- [Kubernetes Engine PRD](./prd/kubernetes_engine/README.md) - 관리형 Kubernetes 서비스
- [Cloud Run PRD](./prd/cloud_run/README.md) - 컨테이너 기반 서버리스 플랫폼

### 데이터 및 스토리지
- [Filestore PRD](./prd/filestore/README.md) - 관리형 NFS 파일 시스템
- [Firestore PRD](./prd/firestore/README.md) - NoSQL 문서 데이터베이스
- [Datastore PRD](./prd/datastore/README.md) - NoSQL 데이터베이스 (Datastore 모드)

### 데이터 처리 및 분석
- [Dataproc PRD](./prd/dataproc/README.md) - 관리형 Spark/Hadoop 서비스
- [Batch PRD](./prd/batch/Google Cloud Batch 제품 요구사항 정의서.md) - 배치 작업 처리
- [Storage Transfer PRD](./prd/storage_transfer/README.md) - 데이터 전송 서비스

### 개발 도구 및 CI/CD
- [Cloud Build PRD](./prd/cloud_build/README.md) - 지속적 통합/배포 서비스
- [Firebase PRD](./prd/firebase/Google Firebase 제품 요구사항 정의서.md) - 모바일/웹 개발 플랫폼

### 보안 및 관리
- [KMS PRD](./prd/kms/README.md) - 암호화 키 관리 서비스

## 입력 파라미터

Google Cloud Inventory Collector는 다음과 같은 입력 파라미터를 지원합니다:

### 필수 파라미터
```json
{
  "secret_data": {
    "type": "service_account",
    "project_id": "string",
    "private_key": "string",
    "client_email": "string"
  }
}
```

### 선택적 파라미터
```json
{
  "options": {
    "cloud_service_types": ["AppEngine", "KubernetesEngine", "CloudRun"],
    "region_filter": ["asia-northeast3", "us-central1"],
    "exclude_regions": ["europe-west1", "us-west1"],
    "kms_locations": ["global", "asia-northeast3"],
    "include_jobs": true,
    "database_filter": ["(default)", "custom-db"],
    "job_filter": ["active-jobs-only"]
  }
}
```

### 파라미터 상세 설명

#### cloud_service_types
- **타입**: Array of String
- **설명**: 수집할 Google Cloud 서비스 타입 지정
- **기본값**: 모든 서비스
- **예시**: `["AppEngine", "KubernetesEngine", "CloudRun", "CloudBuild"]`

#### region_filter
- **타입**: Array of String
- **설명**: 수집할 리전 목록 지정
- **기본값**: 모든 리전
- **예시**: `["asia-northeast3", "us-central1", "global"]`

#### exclude_regions
- **타입**: Array of String
- **설명**: 수집에서 제외할 리전 목록
- **기본값**: 없음
- **예시**: `["europe-west1", "us-west1"]`

#### kms_locations (KMS 전용)
- **타입**: Array of String
- **설명**: KMS KeyRing을 검색할 특정 location 목록
- **기본값**: 모든 location 검색
- **권장값**: `["global", "asia-northeast3"]`

#### include_jobs (Dataproc 전용)
- **타입**: Boolean
- **설명**: Dataproc 클러스터의 작업(Job) 정보 포함 여부
- **기본값**: `false`

#### database_filter (Datastore/Firestore 전용)
- **타입**: Array of String
- **설명**: 수집할 데이터베이스 목록 지정
- **기본값**: 모든 데이터베이스
- **예시**: `["(default)", "custom-database"]`

## 문서 구조

```
docs/ko/
├── README.md                           # 이 파일
├── guide/                             # 일반 가이드
├── development/                       # 개발 가이드
└── prd/                              # 제품 요구사항 정의서
    ├── app_engine/                    # App Engine 도메인
    │   ├── README.md                  # 종합 가이드
    │   ├── API_Reference.md           # API 참조
    │   └── Implementation_Guide.md    # 구현 가이드
    ├── kubernetes_engine/             # Kubernetes Engine 도메인
    │   ├── README.md                  # 종합 가이드
    │   ├── API_Reference.md           # API 참조
    │   └── Implementation_Guide.md    # 구현 가이드
    ├── storage_transfer/              # Storage Transfer 도메인
    ├── firestore/                     # Firestore 도메인
    ├── kms/                           # KMS 도메인
    ├── datastore/                     # Datastore 도메인
    ├── filestore/                     # Filestore 도메인
    ├── dataproc/                      # Dataproc 도메인
    ├── cloud_run/                     # Cloud Run 도메인
    └── cloud_build/                   # Cloud Build 도메인
```

## 주요 기능

### 1. 리소스 수집
- **계층적 수집**: Application → Service → Version → Instance 구조
- **배치 처리**: 대량 데이터의 효율적인 처리
- **병렬 처리**: 여러 리소스의 동시 수집
- **캐싱**: 반복 API 호출 최소화

### 2. 에러 처리
- **재시도 로직**: 일시적 오류에 대한 자동 재시도
- **상세한 에러 메시지**: 문제 해결을 위한 명확한 정보 제공
- **로깅**: 모든 작업에 대한 상세한 로그 기록

### 3. 성능 최적화
- **타임아웃 관리**: API 호출별 적절한 타임아웃 설정
- **메모리 효율성**: 순차 처리로 메모리 사용량 최소화
- **API 할당량 관리**: 할당량 초과 방지 및 최적화

### 4. 모니터링
- **성능 메트릭**: 수집 시간, 오류율 등 성능 지표
- **상태 추적**: 리소스별 상태 및 건강도 모니터링
- **헬스 체크**: 서비스 상태 실시간 확인

## 아키텍처

### Service-Manager-Connector 구조
```
Service Layer (API 엔드포인트)
    ↓
Manager Layer (비즈니스 로직)
    ↓
Connector Layer (Google Cloud API 연동)
```

### 리소스 수집 플로우
1. **초기화**: 인증 정보 및 설정 로드
2. **수집**: API를 통한 리소스 정보 조회
3. **처리**: 메타데이터 추가 및 데이터 정제
4. **검증**: 데이터 무결성 및 관계 검사
5. **저장**: SpaceONE 인벤토리에 리소스 저장


## 개발 가이드

### 1. 새로운 서비스 추가
1. **Connector 구현**: Google Cloud API 연동
2. **Manager 구현**: 비즈니스 로직 및 데이터 처리
3. **Model 정의**: 데이터 구조 및 검증
4. **테스트 작성**: 단위 및 통합 테스트
5. **문서화**: API 참조 및 구현 가이드

### 2. 코딩 규칙
- **이름 규칙**: snake_case (변수, 함수), PascalCase (클래스)
- **문서화**: Google 스타일 Docstring (한국어)
- **에러 처리**: 구체적인 예외 처리 및 로깅
- **테스트**: 모든 기능에 대한 테스트 코드 작성

### 3. 품질 보증
- **린팅**: Ruff를 통한 코드 스타일 검사
- **포맷팅**: 자동 코드 포맷팅 적용
- **테스트**: pytest를 통한 테스트 실행
- **커버리지**: 코드 커버리지 80% 이상 유지

## 문제 해결

### 1. 일반적인 문제들
- **권한 오류**: IAM 역할 및 API 활성화 확인
- **리소스 없음**: 프로젝트 ID 및 리전 설정 확인
- **타임아웃**: 네트워크 지연 및 배치 크기 조정
- **할당량 초과**: API 할당량 증가 요청 또는 재시도 로직 구현

### 2. 디버깅 도구
- **로깅**: 상세한 로그 파일 분석
- **API 테스트**: curl 또는 gcloud 명령어로 직접 API 호출
- **성능 모니터링**: 수집 시간 및 메모리 사용량 추적

## 성능 최적화

### 1. 수집 성능 향상
- **배치 크기 조정**: 환경에 맞는 최적 배치 크기 설정
- **병렬 처리**: 여러 리소스의 동시 수집
- **캐싱 전략**: 자주 사용되는 데이터의 캐싱

### 2. 리소스 사용량 최적화
- **메모리 관리**: 순차 처리로 메모리 사용량 최소화
- **네트워크 최적화**: 적절한 타임아웃 및 재시도 설정
- **API 호출 최적화**: 불필요한 API 호출 최소화

## 보안 고려사항

### 1. 인증 및 권한
- **Service Account**: 최소 권한 원칙 적용
- **키 관리**: 키 파일의 안전한 보관 및 정기 교체
- **감사 로그**: 모든 API 호출에 대한 로깅

### 2. 데이터 보호
- **암호화**: 민감한 정보의 암호화 처리
- **네트워크 보안**: HTTPS를 통한 안전한 통신
- **접근 제어**: IP 화이트리스트 및 VPN 사용

## 모니터링 및 운영

### 1. 성능 모니터링
- **수집 성능**: 리소스별 수집 시간 및 성공률
- **시스템 리소스**: CPU, 메모리, 네트워크 사용량
- **API 할당량**: Google Cloud API 사용량 및 제한

### 2. 운영 관리
- **헬스 체크**: 정기적인 서비스 상태 확인
- **백업 및 복구**: 설정 및 데이터 백업 전략
- **업데이트**: 정기적인 의존성 및 보안 패치

## 참고 자료

### 1. 공식 문서
- [Google Cloud 문서](https://cloud.google.com/docs)
- [SpaceONE 문서](https://spaceone.io/docs)
- [Python 공식 문서](https://docs.python.org/)

### 2. 개발 도구
- [Ruff (Python 린터)](https://docs.astral.sh/ruff/)
- [pytest (테스트 프레임워크)](https://docs.pytest.org/)
- [Google Cloud Python 클라이언트](https://googleapis.dev/python/)

### 3. 커뮤니티
- [SpaceONE GitHub](https://github.com/spaceone)
- [Google Cloud Community](https://cloud.google.com/community)
- [Python 커뮤니티](https://www.python.org/community/)

## 기여하기

### 1. 기여 방법
1. **Issue 등록**: 버그 리포트 또는 기능 요청
2. **Fork 및 개발**: 개인 저장소에서 개발
3. **Pull Request**: 메인 저장소로 변경사항 제출
4. **코드 리뷰**: 팀원들의 코드 검토 및 피드백

### 2. 개발 환경 설정
- 개발 환경 설정 가이드 참조
- 테스트 코드 작성 및 실행
- 코딩 규칙 준수 확인

### 3. 문서 기여
- 한국어 문서 작성 및 번역
- 코드 예시 및 사용법 개선
- 문제 해결 가이드 추가

## 라이선스

이 프로젝트는 Apache License 2.0 하에 배포됩니다. 자세한 내용은 [LICENSE](../LICENSE) 파일을 참조하세요.

## 지원

### 1. 기술 지원
- **GitHub Issues**: 버그 리포트 및 기능 요청
- **문서**: 각 도메인별 상세 가이드 참조
- **커뮤니티**: SpaceONE 및 Google Cloud 커뮤니티 활용

### 2. 연락처
- **이메일**: support@spaceone.dev
- **GitHub**: [SpaceONE Organization](https://github.com/spaceone)
- **웹사이트**: [SpaceONE](https://spaceone.io/)

---

**참고**: 이 문서는 지속적으로 업데이트됩니다. 최신 정보는 GitHub 저장소를 확인하세요.
