# Google Cloud Firestore 제품 요구사항 정의서

## 1. 제품 개요

Google Cloud Firestore는 모바일, 웹, 서버 개발을 위한 유연하고 확장 가능한 NoSQL 클라우드 데이터베이스입니다. Firebase 및 Google Cloud Platform의 일부로, 실시간 데이터 동기화와 오프라인 지원 기능을 통해 클라이언트 간 데이터 동기화를 손쉽게 구현할 수 있습니다. 서버리스 아키텍처를 채택하여 개발자가 인프라 관리에 대한 걱정 없이 애플리케이션 개발에 집중할 수 있도록 지원합니다.

## 2. 주요 기능

- **서버리스 및 완전 관리형:** 인프라 설정이나 유지보수 없이 자동으로 확장 및 축소됩니다.
- **실시간 데이터 동기화:** 연결된 모든 클라이언트에 데이터 변경 사항이 실시간으로 전파됩니다.
- **오프라인 지원:** 네트워크 연결이 끊어져도 앱이 원활하게 작동하며, 연결이 복구되면 데이터를 자동으로 동기화합니다.
- **강력한 쿼리 기능:** 복잡한 쿼리, 트랜잭션, 벡터 검색을 지원하여 유연한 데이터 조회가 가능합니다.
- **포괄적인 보안:** Firebase 인증 및 Google Cloud IAM(Identity and Access Management)과 통합되어 강력한 데이터 보안 및 접근 제어 규칙을 제공합니다.
- **MongoDB 호환성:** 기존 MongoDB 애플리케이션 코드, 드라이버, 도구를 Firestore와 함께 사용할 수 있습니다.
- **생성형 AI 지원:** LangChain, LlamaIndex와 같은 프레임워크와의 통합 및 벡터 검색 기능을 통해 생성형 AI 애플리케이션 구축을 지원합니다.

## 4. 수집 기능 요구사항 (Collection Requirements)

이 섹션은 SpaceONE 플러그인에서 Firestore 리소스를 수집하기 위한 상세 요구사항을 기술합니다.

### 4.1. 수집 리소스
- **Database**: 프로젝트 내의 모든 Firestore 데이터베이스를 수집의 기본 단위로 합니다. (삭제된 리소스 및 `DATASTORE_MODE` 타입 제외)
- **Collection / Document**: `FIRESTORE_NATIVE` 타입의 각 데이터베이스 내 모든 컬렉션과 문서를 재귀적으로 탐색하여 수집합니다.
- **Index**: 각 데이터베이스의 컬렉션 그룹에 대한 모든 복합 인덱스를 수집합니다.

### 4.2. 핵심 수집 데이터

#### 4.2.1. Database 관련 데이터
- **기본 정보**: Database ID, 프로젝트 ID, 위치(Location ID), 타입 (`FIRESTORE_NATIVE`), 동시성 제어(Concurrency Control), 생성 시간, Etag

#### 4.2.2. Collection / Document 관련 데이터
- **Collection**: 컬렉션 ID, 전체 경로(Path)
- **Document**: 문서 ID, 전체 경로(Path), 필드(Fields), 생성 및 업데이트 시간

#### 4.2.3. Index 관련 데이터
- **기본 정보**: 인덱스 ID, 상태(State)
- **인덱스 구성**: 쿼리 범위(Query Scope), 필드(Fields) 목록 및 순서/모드

### 4.3. 수집 메트릭
- **문서 개수 (document_count)**: 데이터베이스별 총 문서 수를 집계합니다.
- **인덱스 개수 (index_count)**: 데이터베이스별 총 인덱스 수를 집계합니다.

### 4.4. 주요 구현 기능
- **데이터베이스 중심 수집**: `projects.databases.list`를 통해 프로젝트 내 데이터베이스 목록을 조회하고, `type`이 `FIRESTORE_NATIVE`인 데이터베이스만 필터링하여 수집을 진행합니다.
- **재귀적 문서 탐색**:
    1. `projects.databases.documents.listCollectionIds`를 사용하여 최상위 컬렉션 ID 목록을 조회합니다.
    2. 각 컬렉션에 대해 `projects.databases.documents.list`를 호출하여 문서 목록을 가져옵니다.
    3. 각 문서에 대해 다시 `listCollectionIds`를 호출하여 하위 컬렉션 목록을 가져오는 과정을 반복하며 모든 문서를 재귀적으로 탐색합니다.
- **인덱스 정보 수집**: `projects.databases.collectionGroups.indexes.list` API를 사용하여 각 데이터베이스의 모든 복합 인덱스 정보를 수집합니다.
- **SpaceONE 모델 변환**: 수집된 모든 원시 데이터를 SpaceONE의 Cloud Service 모델 형식에 맞게 변환하여 일관된 데이터 관리를 지원합니다.

### 4.5. 필요 권한
Firestore 데이터 수집을 위해 서비스 계정에 다음 IAM 역할이 필요합니다.
- **Cloud Datastore Viewer**: Firestore 데이터베이스, 문서, 인덱스에 대한 읽기 전용 접근 권한을 제공합니다.
