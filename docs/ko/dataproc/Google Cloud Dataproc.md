# Google Cloud Dataproc 제품 요구사항 정의서 (PRD)

## 1. 개요 (Overview)

Google Cloud Dataproc은 Apache Spark, Hadoop 및 30개 이상의 오픈소스 프레임워크를 위한 완전 관리형 플랫폼입니다. 복잡한 데이터 처리 클러스터의 생성, 확장, 관리를 자동화하여 데이터 엔지니어와 데이터 과학자가 인프라 운영보다 분석 작업 자체에 집중할 수 있도록 지원합니다. Dataproc은 기존 온프레미스 Hadoop 및 Spark 워크로드를 클라우드로 마이그레이션하거나, 클라우드 네이티브 데이터 애플리케이션을 구축하는 데 효과적으로 사용됩니다.

## 2. 주요 기능 및 이점 (Key Features & Benefits)

### 2.1. 기능
- **관리형 오픈소스 생태계**: Spark와 전체 Hadoop 스택(MapReduce, HDFS, YARN)뿐만 아니라 Flink, Trino, Hive 등 30개 이상의 오픈소스 도구를 위한 완전 관리형 서비스를 제공합니다.
- **Spark용 Lightning Engine**: Compute Engine 기반 Dataproc의 프리미엄 등급에서 사용할 수 있는 Lightning Engine은 Spark SQL 및 DataFrame 작업의 성능을 크게 향상시켜 쿼리 속도를 높여줍니다.
- **자동 확장(Autoscaling)**: 워크로드의 변화에 따라 클러스터의 작업자 노드 수를 동적으로 조정하여 리소스 사용을 최적화하고 비용을 절감합니다.
- **유연한 클러스터 관리**: GPU, 선점형 VM, 초기화 작업 등 다양한 머신 유형과 구성을 지원하여 필요에 맞는 클러스터를 맞춤설정할 수 있습니다.
- **GKE 기반 Dataproc**: Google Kubernetes Engine(GKE) 클러스터에서 Spark 작업을 실행하여 컨테이너화된 워크로드와 데이터 처리 워크로드를 통합 관리할 수 있습니다.
- **광범위한 통합**: BigQuery, Vertex AI, Spanner, Cloud Storage 등 다른 Google Cloud 서비스와 기본적으로 통합되어 강력한 엔드 투 엔드 솔루션을 구축할 수 있습니다.
- **엔터프라이즈급 보안**: Kerberos, Apache Ranger와의 통합, IAM, VPC 서비스 제어 등 Google Cloud의 강력한 보안 기능을 활용하여 데이터를 안전하게 보호합니다.

### 2.2. 이점
- **비용 효율성**: 자동 확장 및 선점형 VM과 같은 기능을 통해 다른 클라우드 대안 대비 비용을 절감할 수 있습니다.
- **운영 간소화**: 평균 90초 이내에 클러스터를 신속하게 생성, 확장 및 종료하여 복잡한 클러스터 관리 및 모니터링을 자동화합니다.
- **강력한 보안**: 엔터프라이즈급 보안 기능을 활용하여 데이터를 안전하게 보호합니다.

## 3. 주요 사용 사례 (Use Cases)

- **데이터 레이크 현대화 및 Hadoop 마이그레이션**: 온프레미스 워크로드를 클라우드로 쉽게 이전하고 Cloud Storage의 데이터에 대해 다양한 작업을 실행합니다.
- **대규모 일괄 ETL 처리**: Spark 또는 MapReduce를 사용하여 대규모 데이터 세트를 효율적으로 처리하고 변환합니다.
- **데이터 과학 및 머신러닝**: Jupyter, Vertex AI 등 익숙한 도구와 통합하여 대규모 모델 학습 및 고급 분석을 수행할 수 있습니다.
- **다양한 분석 엔진 실행**: 대화형 SQL을 위한 Trino나 스트림 처리를 위한 Flink 등 특정 목적에 맞는 전용 클러스터를 배포할 수 있습니다.

## 4. 가격 책정 (Pricing)

- **가격 책정 모델**: Dataproc의 가격은 클러스터의 가상 CPU(vCPU) 수와 클러스터가 실행된 시간을 기준으로 책정됩니다.
- **요금 공식**: `vCPU 수 × 시간당 $0.010` 이며, 요금은 초 단위로 비례하여 계산되고 최소 1분의 사용 시간이 적용됩니다.
- **추가 비용**: Dataproc 요금 외에 클러스터를 구성하는 Compute Engine 인스턴스, 영구 디스크, 네트워킹 등 다른 Google Cloud 리소스에 대한 비용이 별도로 청구됩니다.

> 상세한 최신 정보는 공식 [Dataproc 가격 책정 페이지](https://cloud.google.com/dataproc/pricing)를 참고하세요.

## 5. 기술 참조 및 리소스 (Technical References & Resources)

- **API 및 클라이언트 라이브러리**: C++, C#, Go, Java, Python, Ruby 등 다양한 프로그래밍 언어를 위한 Cloud 클라이언트 라이브러리를 제공합니다.
- **REST 및 RPC API**: 클러스터, 작업, 워크플로 템플릿과 같은 리소스를 관리하기 위한 상세한 REST 및 RPC API 참조 문서를 제공합니다.
- **gcloud CLI**: `gcloud dataproc` 명령어를 사용하여 터미널에서 Dataproc 리소스를 관리할 수 있습니다.
- **출시 노트**: 새로운 기능, 개선 사항, 해결된 문제 등 최신 업데이트 정보는 [Dataproc 출시 노트](https://cloud.google.com/dataproc/docs/release-notes)를 통해 확인할 수 있습니다.

---

## 6. 현재 구현된 수집 기능 (Based on Source Code)

이 섹션은 현재 SpaceONE 플러그인에서 실제로 구현하고 수집하는 Dataproc 리소스의 상세 내역을 기술합니다.

### 6.1. 수집 리소스
- **Dataproc Cluster**: Google Cloud 프로젝트 내의 모든 Dataproc 클러스터를 수집합니다.
- **Workflow Template**: 모든 리전의 Dataproc 워크플로우 템플릿을 수집합니다.
- **Autoscaling Policy**: 모든 리전의 Dataproc 자동 확장 정책을 수집합니다.

### 6.2. 핵심 수집 데이터
- **클러스터 (Cluster)**
  - **기본 정보**: 클러스터 이름, UUID, 프로젝트 ID, 위치(리전/존), 상태, 생성 시간, 라벨
  - **클러스터 구성**: GCE 클러스터 설정, 인스턴스 그룹 설정(마스터/워커), 소프트웨어 설정, 스토리지 설정 등
  - **연관 작업 정보 (Associated Jobs)**: 각 클러스터에 연결된 최근 작업(최대 10개)의 상태, ID, 배치 정보 등을 수집하여 `jobs` 필드에 포함합니다.
- **워크플로우 템플릿 (Workflow Template)**
  - 템플릿 ID, 이름, 버전, 생성/수정 시간, 라벨, 배치 정보, 작업 목록 등
- **자동 확장 정책 (Autoscaling Policy)**
  - 정책 ID, 이름, 워커 설정, 알고리즘 등

### 6.3. 수집 메트릭
- **cluster_cpu_utilization**: 클러스터의 평균 CPU 사용률
- **cluster_memory_utilization**: 클러스터의 평균 메모리 사용률
- **cluster_hdfs_capacity**: 클러스터의 HDFS 총 용량
- **cluster_yarn_memory**: 클러스터의 YARN 사용 가능 메모리

### 6.4. 주요 구현 기능
- Google Cloud API를 통해 각 프로젝트의 모든 리전에 있는 Dataproc 클러스터, 워크플로우 템플릿, 자동 확장 정책 정보를 조회합니다.
- 성능 향상을 위해 API 호출 시 GCP 리전 목록을 캐싱하여 사용합니다.
- 수집된 데이터를 SpaceONE의 Cloud Service 모델 형식에 맞게 변환합니다.
- SpaceONE 콘솔에서 사용자가 클러스터 및 관련 정보를 쉽게 파악할 수 있도록 동적 테이블 및 항목 레이아웃을 제공합니다.