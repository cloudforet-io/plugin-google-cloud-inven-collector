# Kubernetes Engine (GKE) API 참조 가이드

## 개요

이 문서는 Google Cloud Kubernetes Engine (GKE) API를 사용하여 리소스를 수집하는 방법과 API 엔드포인트에 대한 상세한 정보를 제공합니다.

## 커넥터별 API 엔드포인트

### 1. Cluster Connector APIs

#### GKEClusterV1Connector
```python
# 클러스터 목록 조회
connector.list_clusters(**query)

# 특정 클러스터 조회
connector.get_cluster(name, location)

# 작업 목록 조회
connector.list_operations(**query)

# 워크로드 목록 조회
connector.list_workloads(cluster_name, location, **query)
```

#### GKEClusterV1BetaConnector
```python
# v1beta1 전용 기능 포함
connector.list_fleets(**query)           # Fleet 목록 조회
connector.list_memberships(**query)      # Membership 목록 조회
```

### 2. Node Pool Connector APIs

#### GKENodePoolV1Connector
```python
# 노드풀 목록 조회
connector.list_node_pools(cluster_name, location, **query)

# 특정 노드풀 조회
connector.get_node_pool(cluster_name, location, node_pool_name)

# 노드 목록 조회
connector.list_nodes(cluster_name, location, node_pool_name, **query)

# 특정 노드 조회
connector.get_node(cluster_name, location, node_pool_name, node_name)
```

#### GKENodePoolV1BetaConnector
```python
# v1beta1 전용 기능 포함
connector.list_node_groups(cluster_name, location, node_pool_name, **query)
connector.get_node_group(cluster_name, location, node_pool_name, node_group_name)
```

### 3. API 엔드포인트 예시

#### Cluster API
```
GET /v1/projects/{projectId}/locations/{location}/clusters
```

**응답 예시:**
```json
{
  "clusters": [
    {
      "name": "projects/my-project/locations/us-central1/clusters/my-cluster",
      "status": "RUNNING",
      "currentMasterVersion": "1.24.0-gke.1000",
      "currentNodeCount": 3,
      "endpoint": "35.184.123.456"
    }
  ]
}
```

#### Node Pool API
```
GET /v1/projects/{projectId}/locations/{location}/clusters/{clusterId}/nodePools
```

**응답 예시:**
```json
{
  "nodePools": [
    {
      "name": "default-pool",
      "config": {
        "machineType": "e2-medium",
        "diskSizeGb": 100
      },
      "status": "RUNNING"
    }
  ]
}
```

## 리소스 모델

### Cluster 리소스
```python
@dataclass
class GKECluster:
    name: str
    status: str
    location: str
    current_master_version: str
    current_node_count: int
    endpoint: str
    project_id: str
```

### Node Pool 리소스
```python
@dataclass
class GKENodePool:
    name: str
    config: dict
    status: str
    cluster_id: str
    project_id: str
```

## 권한 및 인증

### 필요한 IAM 역할
```json
{
  "role": "roles/container.viewer",
  "permissions": [
    "container.clusters.list",
    "container.clusters.get",
    "container.nodePools.list",
    "container.nodePools.get"
  ]
}
```

## 성능 최적화

### 1. 배치 처리
```python
def collect_clusters_batch(self, batch_size: int = 100):
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
def get_cluster_info(self, cluster_name: str):
    """클러스터 정보 캐싱"""
    return self.client.projects().locations().clusters().get(
        name=cluster_name
    ).execute()
```

## 에러 처리

### API 오류 처리
```python
def handle_api_error(self, error: HttpError):
    """API 오류 처리"""
    if error.resp.status == 403:
        raise PermissionError(f"GKE API 접근 권한이 없습니다: {error}")
    elif error.resp.status == 404:
        raise ResourceNotFoundError(f"GKE 리소스를 찾을 수 없습니다: {error}")
    else:
        raise GKEError(f"GKE API 오류: {error}")
```

## 문제 해결

### 일반적인 문제들

#### 권한 오류
```
Error 403: The caller does not have permission
```
**해결 방법**: Container Engine API 활성화 및 적절한 IAM 권한 부여

#### 리소스 없음
```
Error 404: Requested entity was not found
```
**해결 방법**: 프로젝트 ID 및 리전 확인

## 참고 자료

- [GKE API 문서](https://cloud.google.com/kubernetes-engine/docs/reference/rest)
- [Container API 문서](https://cloud.google.com/kubernetes-engine/docs/reference/rest/v1)
- [IAM 권한 가이드](https://cloud.google.com/iam/docs/understanding-roles)
