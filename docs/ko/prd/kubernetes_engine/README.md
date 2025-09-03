# Google Cloud Kubernetes Engine (GKE) 도메인 가이드

## 개요

Google Cloud Kubernetes Engine (GKE)는 Google Cloud에서 관리형 Kubernetes 클러스터를 제공하는 서비스입니다. 이 문서는 SpaceONE Google Cloud Inventory Collector에서 GKE 리소스를 수집하는 방법과 관련 아키텍처를 설명합니다.

## 아키텍처

### 매니저 구조
```
Kubernetes Engine Managers
├── Cluster Managers (클러스터 매니저)
│   ├── cluster_v1_manager.py          # v1 API 클러스터 전용
│   └── cluster_v1beta_manager.py      # v1beta1 API 클러스터 전용
├── Node Pool Managers (노드풀 매니저)
│   ├── node_pool_v1_manager.py        # v1 API 노드풀/노드 전용
│   └── node_pool_v1beta_manager.py    # v1beta1 API 노드풀/노드 전용
```

### 커넥터 구조
```
Kubernetes Engine Connectors
├── Cluster Connectors (클러스터 커넥터)
│   ├── cluster_v1.py          # v1 API 클러스터 전용
│   └── cluster_v1beta.py      # v1beta1 API 클러스터 전용
├── Node Pool Connectors (노드풀 커넥터)
│   ├── node_pool_v1.py        # v1 API 노드풀/노드 전용
│   └── node_pool_v1beta.py    # v1beta1 API 노드풀/노드 전용
```

### 클러스터 구조
```
GKE Cluster
├── Cluster (클러스터)
│   ├── Node Pool (노드 풀)
│   │   ├── Node (노드)
│   │   └── Node Group (노드 그룹)
│   ├── Networking (네트워킹)
│   │   ├── VPC
│   │   ├── Subnet
│   │   └── Firewall Rules
│   └── Security (보안)
│       ├── IAM Policies
│       ├── RBAC
│       └── Network Policies
```

### 계층별 리소스 수집

#### 1. Cluster Level
- **리소스**: `container.googleapis.com/Cluster`
- **수집 정보**: 
  - 클러스터 이름 및 ID
  - 프로젝트 ID
  - 리전 및 영역
  - Kubernetes 버전
  - 클러스터 상태
  - 마스터 인증 정보
  - 네트워크 설정
  - 보안 설정

#### 2. Node Pool Level
- **리소스**: `container.googleapis.com/NodePool`
- **수집 정보**:
  - 노드 풀 이름
  - 노드 수
  - 머신 타입
  - 디스크 크기 및 타입
  - 이미지 타입
  - 자동 스케일링 설정
  - 업그레이드 정책
  - **노드 정보 (새로 추가됨)**

#### 3. Node Level
- **리소스**: `container.googleapis.com/Node`
- **수집 정보**:
  - 노드 이름
  - 상태 (RUNNING, STOPPING, ERROR 등)
  - 가용성 영역
  - 머신 타입
  - CPU 및 메모리 할당량
  - 디스크 정보
  - 라벨 및 테인트
  - **내부/외부 IP 주소 (새로 추가됨)**

#### 4. Node Group Level
- **리소스**: `container.googleapis.com/NodeGroup`
- **수집 정보**:
  - 노드 그룹 이름
  - 노드 템플릿
  - 자동 스케일링 그룹
  - 지역 분산 설정
  - 업그레이드 정책

## API 버전 관리

### 지원 API 버전
- **v1**: 현재 안정 버전, 프로덕션 환경 권장
- **v1beta**: 베타 기능 테스트용, 하위 호환성 지원

### 매니저별 API 버전
```python
# 클러스터 매니저
from spaceone.inventory.manager.kubernetes_engine.cluster_v1_manager import GKEClusterV1Manager
from spaceone.inventory.manager.kubernetes_engine.cluster_v1beta_manager import GKEClusterV1BetaManager

# 노드풀 매니저  
from spaceone.inventory.manager.kubernetes_engine.node_pool_v1_manager import GKENodePoolV1Manager
from spaceone.inventory.manager.kubernetes_engine.node_pool_v1beta_manager import GKENodePoolV1BetaManager

# 커넥터
from spaceone.inventory.connector.kubernetes_engine.cluster_v1 import GKEClusterV1Connector
from spaceone.inventory.connector.kubernetes_engine.cluster_v1beta import GKEClusterV1BetaConnector
from spaceone.inventory.connector.kubernetes_engine.node_pool_v1 import GKENodePoolV1Connector
from spaceone.inventory.connector.kubernetes_engine.node_pool_v1beta import GKENodePoolV1BetaConnector
```

## 리소스 수집 프로세스

### 1. 초기화 단계
```python
def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.api_version = "v1"
    self.connector_name = "GKENodePoolV1Connector"
    self.cloud_service_group = "KubernetesEngine"
```

### 2. 수집 단계
```python
def collect_cloud_service(self, params: Dict[str, Any]) -> Tuple[List[Any], List[ErrorResourceResponse]]:
    """GKE 노드 그룹 정보를 수집합니다 (v1 API)"""
    
    # 1. GKE 노드 그룹 목록 조회
    node_groups = self.list_node_pools(params)
    
    for node_group in node_groups:
        # 2. 메트릭 정보 조회
        metrics = self.get_node_pool_metrics(
            cluster_name, location, node_pool_name, params
        )
        
        # 3. 노드 정보 조회 (새로 추가됨)
        nodes = self.get_node_pool_nodes(
            cluster_name, location, node_pool_name, params
        )
        
        # 4. 노드 정보를 노드 그룹 데이터에 추가
        if nodes:
            node_group_data["nodes"] = []
            for node in nodes:
                node_info = {
                    "name": str(node.get("name", "")),
                    "status": str(node.get("status", "")),
                    "machineType": str(node.get("machineType", "")),
                    "zone": str(node.get("zone", "")),
                    "internalIP": str(node.get("internalIP", "")),
                    "externalIP": str(node.get("externalIP", "")),
                    "createTime": node.get("createTime"),
                    "labels": node.get("labels", {}),
                    "taints": node.get("taints", []),
                }
                node_group_data["nodes"].append(node_info)
```

### 3. 메타데이터 처리
```python
def _process_metadata(self, resource: dict) -> dict:
    """리소스 메타데이터 처리"""
    metadata = {
        "resource_type": "kubernetes_engine",
        "collection_timestamp": datetime.utcnow().isoformat(),
        "project_id": self.project_id,
        "location": self.location,
        "api_version": self.api_version
    }
    
    resource["metadata"] = metadata
    return resource
```

## 권한 관리

### 필요한 IAM 권한
```json
{
  "role": "roles/container.viewer",
  "permissions": [
    "container.clusters.list",
    "container.clusters.get",
    "container.nodePools.list",
    "container.nodePools.get",
    "container.nodes.list",
    "container.nodes.get"
  ]
}
```

### 최소 권한 원칙
- **읽기 전용**: 수집 목적으로는 읽기 권한만 필요
- **범위 제한**: 특정 클러스터에 대한 권한만 부여
- **감사 로그**: 모든 API 호출에 대한 감사 로그 활성화

## 성능 최적화

### 1. 배치 처리
```python
def _collect_clusters_batch(self, batch_size: int = 100) -> List[dict]:
    """클러스터 배치 수집"""
    clusters = []
    page_token = None
    
    while True:
        response = self.client.projects().locations().clusters().list(
            parent=f"projects/{self.project_id}/locations/{self.location}",
            pageSize=batch_size,
            pageToken=page_token
        ).execute()
        
        clusters.extend(response.get("clusters", []))
        page_token = response.get("nextPageToken")
        
        if not page_token:
            break
    
    return clusters
```

### 2. 캐싱 전략
```python
@lru_cache(maxsize=128)
def _get_cluster_info(self, cluster_name: str) -> dict:
    """클러스터 정보 캐싱"""
    return self.client.projects().locations().clusters().get(
        name=f"projects/{self.project_id}/locations/{self.location}/clusters/{cluster_name}"
    ).execute()
```

### 3. 타임아웃 관리
```python
def _create_client(self) -> Resource:
    """API 클라이언트 생성 (타임아웃 설정)"""
    return build(
        "container",
        self.api_version,
        credentials=self.credentials,
        cache_discovery=False,
        timeout=60  # GKE API는 더 긴 타임아웃 필요
    )
```

## 에러 처리

### 1. API 오류 처리
```python
def _handle_api_error(self, error: HttpError) -> None:
    """API 오류 처리"""
    if error.resp.status == 403:
        raise PermissionError(f"GKE API 접근 권한이 없습니다: {error}")
    elif error.resp.status == 404:
        raise ResourceNotFoundError(f"GKE 리소스를 찾을 수 없습니다: {error}")
    elif error.resp.status == 429:
        raise QuotaExceededError(f"GKE API 할당량이 초과되었습니다: {error}")
    else:
        raise GKEError(f"GKE API 오류: {error}")
```

### 2. 재시도 로직
```python
@retry(stop_max_attempt_number=3, wait_exponential_multiplier=2000)
def _api_call_with_retry(self, api_method, *args, **kwargs):
    """재시도 로직이 포함된 API 호출"""
    try:
        return api_method(*args, **kwargs).execute()
    except HttpError as e:
        if e.resp.status in [429, 500, 502, 503, 504]:
            raise  # 재시도 가능한 오류
        else:
            raise  # 재시도 불가능한 오류
```

## 모니터링 및 로깅

### 1. 성능 메트릭
```python
def _log_collection_metrics(self, start_time: float, resource_count: int):
    """수집 성능 메트릭 로깅"""
    duration = time.time() - start_time
    self.logger.info(
        f"GKE 수집 완료: {resource_count}개 리소스, "
        f"소요시간: {duration:.2f}초"
    )
```

### 2. 상태 추적
```python
def _track_collection_status(self, status: str, details: str = None):
    """수집 상태 추적"""
    self.collection_status = {
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "details": details
    }
```

### 3. 리소스별 상태 모니터링
```python
def _monitor_cluster_health(self, cluster: dict) -> dict:
    """클러스터 상태 모니터링"""
    health_info = {
        "cluster_name": cluster["name"],
        "status": cluster["status"],
        "node_count": cluster.get("currentNodeCount", 0),
        "version": cluster.get("currentMasterVersion", "unknown"),
        "health_timestamp": datetime.utcnow().isoformat()
    }
    
    # 노드 풀 상태 확인
    node_pools = cluster.get("nodePools", [])
    unhealthy_pools = [pool for pool in node_pools if pool.get("status") != "RUNNING"]
    
    if unhealthy_pools:
        health_info["unhealthy_node_pools"] = len(unhealthy_pools)
        health_info["health_status"] = "degraded"
    else:
        health_info["health_status"] = "healthy"
    
    return health_info
```

## 테스트 전략

### 1. 단위 테스트
```python
def test_collect_clusters(self):
    """클러스터 수집 테스트"""
    # Given
    mock_client = Mock()
    mock_client.projects().locations().clusters().list().execute.return_value = {
        "clusters": [
            {"name": "test-cluster", "status": "RUNNING"}
        ]
    }
    
    # When
    result = self.collector._collect_clusters()
    
    # Then
    assert len(result) == 1
    assert result[0]["name"] == "test-cluster"
    assert result[0]["status"] == "RUNNING"
```

### 2. 통합 테스트
```python
def test_end_to_end_collection(self):
    """전체 수집 프로세스 테스트"""
    # Given
    options = {
        "project_id": "test-project",
        "location": "us-central1"
    }
    
    # When
    resources = self.collector.collect()
    
    # Then
    assert len(resources) > 0
    assert all("metadata" in resource for resource in resources)
    assert all(resource["metadata"]["resource_type"] == "kubernetes_engine" 
               for resource in resources)
```

### 3. 모의 데이터 테스트
```python
def test_with_mock_data(self):
    """모의 데이터를 사용한 테스트"""
    # Given
    mock_clusters = [
        {
            "name": "cluster-1",
            "status": "RUNNING",
            "currentNodeCount": 3,
            "nodePools": [
                {"name": "pool-1", "status": "RUNNING"}
            ]
        }
    ]
    
    # When
    result = self.collector._process_clusters(mock_clusters)
    
    # Then
    assert len(result) == 1
    assert result[0]["name"] == "cluster-1"
```

## 배포 및 운영

### 1. 환경별 설정
```yaml
# development.yml
kubernetes_engine:
  api_version: "v1"
  timeout: 60
  batch_size: 50
  enable_caching: true
  location: "us-central1"

# production.yml
kubernetes_engine:
  api_version: "v1"
  timeout: 120
  batch_size: 100
  enable_caching: true
  enable_retry: true
  max_retries: 3
  location: "us-central1"
  enable_health_monitoring: true
```

### 2. 헬스 체크
```python
def health_check(self) -> dict:
    """GKE 수집기 헬스 체크"""
    try:
        # 간단한 API 호출로 연결 상태 확인
        self.client.projects().locations().clusters().list(
            parent=f"projects/{self.project_id}/locations/{self.location}"
        ).execute()
        return {"status": "healthy", "service": "kubernetes_engine"}
    except Exception as e:
        return {"status": "unhealthy", "service": "kubernetes_engine", "error": str(e)}
```

### 3. 자동 스케일링
```python
def auto_scale_collection(self) -> None:
    """수집 프로세스 자동 스케일링"""
    cluster_count = self._get_cluster_count()
    
    if cluster_count > 100:
        # 대규모 클러스터 환경에서는 배치 크기 증가
        self.batch_size = min(200, cluster_count // 10)
        self.timeout = min(300, cluster_count * 2)
    elif cluster_count < 10:
        # 소규모 환경에서는 배치 크기 감소
        self.batch_size = max(20, cluster_count)
        self.timeout = 60
```

## 문제 해결

### 1. 일반적인 문제들

#### 권한 오류
```
Error 403: The caller does not have permission
```
**해결 방법**: Container Engine API 활성화 및 적절한 IAM 권한 부여

#### 리소스 없음
```
Error 404: Requested entity was not found
```
**해결 방법**: 프로젝트 ID 및 리전 확인, GKE 클러스터 존재 여부 확인

#### API 할당량 초과
```
Error 429: Quota exceeded
```
**해결 방법**: API 할당량 증가 요청 또는 재시도 로직 구현

#### 타임아웃 오류
```
Error 408: Request timeout
```
**해결 방법**: 타임아웃 값 증가, 배치 크기 감소

### 2. 디버깅 팁
- API 응답 로깅 활성화
- 네트워크 지연 시간 모니터링
- 메모리 사용량 추적
- API 호출 빈도 제한
- 클러스터 크기별 성능 분석

### 3. 성능 최적화 팁
- 대규모 클러스터는 병렬 처리 고려
- 노드 풀별 배치 처리
- 캐싱 전략 활용
- 네트워크 대역폭 모니터링

## 보안 고려사항

### 1. 인증 및 권한
- Service Account 키 파일 보안 관리
- 최소 권한 원칙 적용
- 정기적인 권한 검토

### 2. 데이터 보호
- 민감한 정보 암호화
- 네트워크 전송 보안
- 로그 데이터 보존 정책

### 3. 감사 및 모니터링
- 모든 API 호출 로깅
- 비정상 접근 패턴 감지
- 정기적인 보안 감사

## 최신 업데이트 (2024년 9월)

### NodePool 정보 수집 기능 추가
- **노드 정보 수집**: 각 노드 풀의 개별 노드 정보를 상세하게 수집
- **노드 메타데이터**: 노드 이름, 상태, 머신 타입, IP 주소, 라벨, 테인트 등
- **향상된 로깅**: 수집 과정의 상세한 로그 및 에러 처리 개선
- **에러 처리 강화**: 개별 리소스 수집 실패 시에도 전체 프로세스 계속 진행

### 구현된 매니저 및 커넥터
- `GKENodePoolV1Manager`: v1 API 노드 풀 및 노드 정보 수집
- `GKENodePoolV1BetaManager`: v1beta1 API 노드 풀 및 노드 정보 수집
- `GKENodePoolV1Connector`: v1 API 노드 풀 API 호출
- `GKENodePoolV1BetaConnector`: v1beta1 API 노드 풀 API 호출

## 참고 자료

- [GKE API 문서](https://cloud.google.com/kubernetes-engine/docs/reference/rest)
- [Container API 문서](https://cloud.google.com/kubernetes-engine/docs/reference/rest/v1)
- [IAM 권한 가이드](https://cloud.google.com/iam/docs/understanding-roles)
- [API 할당량 관리](https://cloud.google.com/apis/docs/quotas)
- [GKE 보안 모범 사례](https://cloud.google.com/kubernetes-engine/docs/how-to/hardening-your-cluster)
