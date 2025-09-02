# Kubernetes Engine (GKE) 구현 가이드

## 개요

이 문서는 SpaceONE Google Cloud Inventory Collector에서 Kubernetes Engine (GKE) 리소스를 수집하는 구현 방법을 단계별로 설명합니다.

## 구현 단계

### 1. 프로젝트 구조 설정

```
src/spaceone/inventory/
├── connector/
│   └── kubernetes_engine/
│       ├── __init__.py
│       ├── cluster_v1.py          # v1 API 클러스터 전용
│       ├── cluster_v1beta.py      # v1beta1 API 클러스터 전용
│       ├── node_pool_v1.py        # v1 API 노드풀/노드 전용
│       └── node_pool_v1beta.py    # v1beta1 API 노드풀/노드 전용
├── manager/
│   └── kubernetes_engine/
│       ├── __init__.py
│       ├── cluster_manager.py      # 클러스터 관리자
│       └── node_pool_manager.py    # 노드풀 관리자
└── model/
    └── kubernetes_engine/
        ├── __init__.py
        ├── cluster.py              # 클러스터 모델
        ├── node_pool.py            # 노드풀 모델
        ├── node.py                 # 노드 모델
        └── node_group.py           # 노드 그룹 모델
```

### 2. Connector 구현

#### Cluster Connector (v1)
```python
# src/spaceone/inventory/connector/kubernetes_engine/cluster_v1.py

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from spaceone.inventory.connector.base import BaseConnector

class GKEClusterV1Connector(BaseConnector):
    def __init__(self, credentials, project_id, location):
        self.credentials = credentials
        self.project_id = project_id
        self.location = location
        self.client = build('container', 'v1', credentials=credentials)
    
    def list_clusters(self, page_size=100):
        """클러스터 목록 조회"""
        clusters = []
        page_token = None
        
        while True:
            try:
                request = self.client.projects().locations().clusters().list(
                    parent=f"projects/{self.project_id}/locations/{self.location}",
                    pageSize=page_size,
                    pageToken=page_token
                )
                response = request.execute()
                
                clusters.extend(response.get('clusters', []))
                page_token = response.get('nextPageToken')
                
                if not page_token:
                    break
                    
            except HttpError as e:
                self._handle_error(e)
        
        return clusters
    
    def get_cluster(self, cluster_name):
        """특정 클러스터 정보 조회"""
        try:
            request = self.client.projects().locations().clusters().get(
                name=cluster_name
            )
            response = request.execute()
            return response
        except HttpError as e:
            self._handle_error(e)
    
    def _handle_error(self, error):
        """에러 처리"""
        if error.resp.status == 403:
            raise PermissionError(f"GKE API 접근 권한이 없습니다: {error}")
        elif error.resp.status == 404:
            raise ResourceNotFoundError(f"GKE 클러스터를 찾을 수 없습니다: {error}")
        else:
            raise GKEError(f"GKE API 오류: {error}")
```

#### Cluster Connector (v1beta1)
```python
# src/spaceone/inventory/connector/kubernetes_engine/cluster_v1beta.py

class GKEClusterV1BetaConnector(BaseConnector):
    def __init__(self, credentials, project_id, location):
        self.credentials = credentials
        self.project_id = project_id
        self.location = location
        self.client = build('container', 'v1beta1', credentials=credentials)
    
    def list_fleets(self, **query):
        """Fleet 목록 조회 (v1beta1 전용)"""
        # v1beta1에서만 사용 가능한 Fleet API
        pass
    
    def list_memberships(self, **query):
        """Membership 목록 조회 (v1beta1 전용)"""
        # v1beta1에서만 사용 가능한 Membership API
        pass
```

#### Node Pool Connector (v1)
```python
# src/spaceone/inventory/connector/kubernetes_engine/node_pool_v1.py

class GKENodePoolV1Connector(BaseConnector):
    def __init__(self, credentials, project_id, location):
        self.credentials = credentials
        self.project_id = project_id
        self.location = location
        self.client = build('container', 'v1', credentials=credentials)
    
    def list_node_pools(self, cluster_name, page_size=100):
        """노드 풀 목록 조회"""
        node_pools = []
        page_token = None
        
        while True:
            try:
                request = self.client.projects().locations().clusters().nodePools().list(
                    parent=cluster_name,
                    pageSize=page_size,
                    pageToken=page_token
                )
                response = request.execute()
                
                node_pools.extend(response.get('nodePools', []))
                page_token = response.get('nextPageToken')
                
                if not page_token:
                    break
                    
            except HttpError as e:
                self._handle_error(e)
        
        return node_pools
    
    def list_nodes(self, cluster_name, node_pool_name, **query):
        """노드 목록 조회"""
        # 노드풀 내의 노드들을 조회
        pass
    
    def get_node(self, cluster_name, node_pool_name, node_name):
        """특정 노드 정보 조회"""
        # 특정 노드의 상세 정보 조회
        pass
```

#### Node Pool Connector (v1beta1)
```python
# src/spaceone/inventory/connector/kubernetes_engine/node_pool_v1beta.py

class GKENodePoolV1BetaConnector(BaseConnector):
    def __init__(self, credentials, project_id, location):
        self.credentials = credentials
        self.project_id = project_id
        self.location = location
        self.client = build('container', 'v1beta1', credentials=credentials)
    
    def list_node_groups(self, cluster_name, node_pool_name, **query):
        """노드 그룹 목록 조회 (v1beta1 전용)"""
        # v1beta1에서만 사용 가능한 노드 그룹 API
        pass
    
    def get_node_group(self, cluster_name, node_pool_name, node_group_name):
        """특정 노드 그룹 정보 조회 (v1beta1 전용)"""
        # v1beta1에서만 사용 가능한 노드 그룹 API
        pass
```

### 3. Manager 구현

#### Cluster Manager
```python
# src/spaceone/inventory/manager/kubernetes_engine/cluster_manager.py

from spaceone.inventory.manager.base import BaseManager
from spaceone.inventory.connector.kubernetes_engine import (
    GKEClusterV1Connector, 
    GKEClusterV1BetaConnector
)

class GKEClusterManager(BaseManager):
    def __init__(self, credentials, project_id, location, api_version="v1"):
        self.project_id = project_id
        self.location = location
        self.api_version = api_version
        
        # API 버전에 따른 커넥터 선택
        if api_version == "v1":
            self.connector = GKEClusterV1Connector(credentials, project_id, location)
        else:
            self.connector = GKEClusterV1BetaConnector(credentials, project_id, location)
    
    def collect_clusters(self):
        """클러스터 수집"""
        return self.connector.list_clusters()
    
    def collect_cluster_details(self, cluster_name):
        """클러스터 상세 정보 수집"""
        return self.connector.get_cluster(cluster_name, self.location)
    
    def collect_operations(self):
        """작업 목록 수집"""
        return self.connector.list_operations()
    
    def collect_workloads(self, cluster_name):
        """워크로드 정보 수집"""
        return self.connector.list_workloads(cluster_name, self.location)
    
    # v1beta1 전용 기능
    def collect_fleets(self):
        """Fleet 목록 수집 (v1beta1 전용)"""
        if hasattr(self.connector, 'list_fleets'):
            return self.connector.list_fleets()
        return []
    
    def collect_memberships(self):
        """Membership 목록 수집 (v1beta1 전용)"""
        if hasattr(self.connector, 'list_memberships'):
            return self.connector.list_memberships()
        return []
```
        self.location = location
    
    def collect(self):
        """클러스터 정보 수집"""
        try:
            clusters = self.connector.list_clusters()
            
            # 메타데이터 추가
            for cluster in clusters:
                cluster['resource_type'] = 'gke_cluster'
                cluster['project_id'] = self.project_id
                cluster['location'] = self.location
                cluster['collection_timestamp'] = datetime.utcnow().isoformat()
            
            return clusters
            
        except Exception as e:
            self.logger.error(f"클러스터 수집 실패: {e}")
            raise
```

#### Node Pool Manager
```python
# src/spaceone/inventory/manager/kubernetes_engine/node_pool_manager.py

from spaceone.inventory.manager.base import BaseManager
from spaceone.inventory.connector.kubernetes_engine import (
    GKENodePoolV1Connector, 
    GKENodePoolV1BetaConnector
)

class GKENodePoolManager(BaseManager):
    def __init__(self, credentials, project_id, location, api_version="v1"):
        self.project_id = project_id
        self.location = location
        self.api_version = api_version
        
        # API 버전에 따른 커넥터 선택
        if api_version == "v1":
            self.connector = GKENodePoolV1Connector(credentials, project_id, location)
        else:
            self.connector = GKENodePoolV1BetaConnector(credentials, project_id, location)
    
    def collect_node_pools(self, cluster_name):
        """노드풀 목록 수집"""
        return self.connector.list_node_pools(cluster_name, self.location)
    
    def collect_node_pool_details(self, cluster_name, node_pool_name):
        """특정 노드풀 상세 정보 수집"""
        return self.connector.get_node_pool(cluster_name, self.location, node_pool_name)
    
    def collect_nodes(self, cluster_name, node_pool_name):
        """노드 목록 수집"""
        return self.connector.list_nodes(cluster_name, self.location, node_pool_name)
    
    def collect_node_details(self, cluster_name, node_pool_name, node_name):
        """특정 노드 상세 정보 수집"""
        return self.connector.get_node(cluster_name, self.location, node_pool_name, node_name)
    
    # v1beta1 전용 기능
    def collect_node_groups(self, cluster_name, node_pool_name):
        """노드 그룹 목록 수집 (v1beta1 전용)"""
        if hasattr(self.connector, 'list_node_groups'):
            return self.connector.list_node_groups(cluster_name, self.location, node_pool_name)
        return []
    
    def collect_node_group_details(self, cluster_name, node_pool_name, node_group_name):
        """특정 노드 그룹 상세 정보 수집 (v1beta1 전용)"""
        if hasattr(self.connector, 'get_node_group'):
            return self.connector.get_node_group(cluster_name, self.location, node_pool_name, node_group_name)
        return None
    
    def collect_all_resources(self, cluster_name):
        """클러스터의 모든 노드풀 관련 리소스 수집"""
        try:
            resources = []
            
            # 노드풀 수집
            node_pools = self.collect_node_pools(cluster_name)
            for node_pool in node_pools:
                node_pool['resource_type'] = 'gke_node_pool'
                node_pool['project_id'] = self.project_id
                node_pool['location'] = self.location
                node_pool['cluster_name'] = cluster_name
                node_pool['collection_timestamp'] = datetime.utcnow().isoformat()
                resources.append(node_pool)
                
                # 노드 수집
                nodes = self.collect_nodes(cluster_name, node_pool['name'])
                for node in nodes:
                    node['resource_type'] = 'gke_node'
                    node['project_id'] = self.project_id
                    node['location'] = self.location
                    node['cluster_name'] = cluster_name
                    node['node_pool_name'] = node_pool['name']
                    node['collection_timestamp'] = datetime.utcnow().isoformat()
                    resources.append(node)
            
            return resources
            
        except Exception as e:
            self.logger.error(f"노드풀 리소스 수집 실패: {e}")
            raise
```

### 4. Model 정의

#### Cluster Model
```python
# src/spaceone/inventory/model/kubernetes_engine/cluster.py

from dataclasses import dataclass
from typing import Optional, List

@dataclass
class GKECluster:
    name: str
    status: str
    location: str
    current_master_version: str
    current_node_version: str
    initial_node_count: int
    current_node_count: int
    endpoint: str
    master_auth: dict
    network: str
    subnetwork: str
    node_pools: List[dict]
    project_id: str
    resource_type: str = "gke_cluster"
    collection_timestamp: Optional[str] = None
```

#### Node Pool Model
```python
# src/spaceone/inventory/model/kubernetes_engine/node_pool.py

@dataclass
class GKENodePool:
    name: str
    config: dict
    initial_node_count: int
    autoscaling: dict
    management: dict
    version: str
    status: str
    conditions: List[dict]
    cluster_name: str
    project_id: str
    location: str
    resource_type: str = "gke_node_pool"
    collection_timestamp: Optional[str] = None
```

### 5. 통합 및 등록

#### Manager 등록
```python
# src/spaceone/inventory/manager/__init__.py

from .kubernetes_engine.cluster_manager import GKEClusterManager
from .kubernetes_engine.node_pool_manager import GKENodePoolManager

MANAGER_REGISTRY = {
    'gke_cluster': GKEClusterManager,
    'gke_node_pool': GKENodePoolManager,
    # ... 기타 매니저들
}
```

#### Service에서 사용
```python
# src/spaceone/inventory/service/collector_service.py

class CollectorService:
    def collect_gke_resources(self, credentials, project_id, location, api_version="v1"):
        """GKE 리소스 수집"""
        resources = []
        
        # 클러스터 수집
        cluster_manager = GKEClusterManager(credentials, project_id, location, api_version)
        cluster_resources = cluster_manager.collect_clusters()
        resources.extend(cluster_resources)
        
        # 각 클러스터의 노드풀 및 노드 수집
        for cluster in cluster_resources:
            node_pool_manager = GKENodePoolManager(credentials, project_id, location, api_version)
            node_pool_resources = node_pool_manager.collect_all_resources(cluster['name'])
            resources.extend(node_pool_resources)
        
        return resources
    
    def collect_gke_cluster_details(self, credentials, project_id, location, cluster_name, api_version="v1"):
        """특정 클러스터 상세 정보 수집"""
        cluster_manager = GKEClusterManager(credentials, project_id, location, api_version)
        return cluster_manager.collect_cluster_details(cluster_name)
    
    def collect_gke_node_pool_details(self, credentials, project_id, location, cluster_name, node_pool_name, api_version="v1"):
        """특정 노드풀 상세 정보 수집"""
        node_pool_manager = GKENodePoolManager(credentials, project_id, location, api_version)
        return node_pool_manager.collect_node_pool_details(cluster_name, node_pool_name)
```

## 설정 및 환경 변수

### 1. 환경 변수 설정
```bash
# .env 파일
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
GKE_API_VERSION=v1
GKE_LOCATION=us-central1
GKE_TIMEOUT=120
GKE_BATCH_SIZE=100
```

### 2. 설정 파일
```yaml
# config/kubernetes_engine.yml
kubernetes_engine:
  api_version: "v1"
  location: "us-central1"
  timeout: 120
  batch_size: 100
  enable_caching: true
  max_retries: 3
  retry_delay: 2000
  enable_parallel_processing: true
  max_workers: 10
```

## 테스트 구현

### 1. 단위 테스트
```python
# test/test_gke_manager.py

import pytest
from unittest.mock import Mock, patch
from spaceone.inventory.manager.kubernetes_engine.cluster_manager import GKEClusterManager
from spaceone.inventory.manager.kubernetes_engine.node_pool_manager import GKENodePoolManager

class TestGKEClusterManager:
    def setup_method(self):
        self.credentials = Mock()
        self.project_id = "test-project"
        self.location = "us-central1"
        self.manager = GKEClusterManager(self.credentials, self.project_id, self.location, "v1")
    
    def test_collect_clusters_success(self):
        """클러스터 수집 성공 테스트"""
        # Given
        mock_clusters = [
            {
                "name": "projects/test-project/locations/us-central1/clusters/test-cluster",
                "status": "RUNNING",
                "currentNodeCount": 3
            }
        ]
        
        with patch.object(self.manager.connector, 'list_clusters', return_value=mock_clusters):
            # When
            result = self.manager.collect_clusters()
            
            # Then
            assert len(result) == 1
            assert result[0]["status"] == "RUNNING"
    
    def test_collect_clusters_v1beta1(self):
        """v1beta1 API 클러스터 수집 테스트"""
        # Given
        manager = GKEClusterManager(self.credentials, self.project_id, self.location, "v1beta1")
        mock_fleets = [{"name": "test-fleet"}]
        
        with patch.object(manager.connector, 'list_fleets', return_value=mock_fleets):
            # When
            result = manager.collect_fleets()
            
            # Then
            assert len(result) == 1
            assert result[0]["name"] == "test-fleet"
    
    def test_collect_clusters_error(self):
        """클러스터 수집 실패 테스트"""
        # Given
        with patch.object(self.manager.connector, 'list_clusters', side_effect=Exception("API Error")):
            # When & Then
            with pytest.raises(Exception):
                self.manager.collect_clusters()

class TestGKENodePoolManager:
    def setup_method(self):
        self.credentials = Mock()
        self.project_id = "test-project"
        self.location = "us-central1"
        self.manager = GKENodePoolManager(self.credentials, self.project_id, self.location, "v1")
    
    def test_collect_node_pools_success(self):
        """노드풀 수집 성공 테스트"""
        # Given
        mock_node_pools = [
            {
                "name": "default-pool",
                "config": {"machineType": "e2-medium"},
                "status": "RUNNING"
            }
        ]
        
        with patch.object(self.manager.connector, 'list_node_pools', return_value=mock_node_pools):
            # When
            result = self.manager.collect_node_pools("test-cluster")
            
            # Then
            assert len(result) == 1
            assert result[0]["name"] == "default-pool"
    
    def test_collect_all_resources_success(self):
        """모든 리소스 수집 성공 테스트"""
        # Given
        mock_node_pools = [{"name": "default-pool"}]
        mock_nodes = [{"name": "node-1"}]
        
        with patch.object(self.manager.connector, 'list_node_pools', return_value=mock_node_pools), \
             patch.object(self.manager.connector, 'list_nodes', return_value=mock_nodes):
            # When
            result = self.manager.collect_all_resources("test-cluster")
            
            # Then
            assert len(result) == 2  # 노드풀 1개 + 노드 1개
            assert result[0]["resource_type"] == "gke_node_pool"
            assert result[1]["resource_type"] == "gke_node"
        # Given
        with patch.object(self.manager.connector, 'list_clusters', side_effect=Exception("API Error")):
            # When & Then
            with pytest.raises(Exception):
                self.manager.collect()
```

### 2. 통합 테스트
```python
# test/integration/test_gke_integration.py

class TestGKEIntegration:
    def test_end_to_end_collection(self):
        """전체 수집 프로세스 테스트"""
        # Given
        credentials = self.get_test_credentials()
        project_id = "test-project"
        location = "us-central1"
        
        # When
        collector_service = CollectorService()
        resources = collector_service.collect_gke_resources(credentials, project_id, location)
        
        # Then
        assert len(resources) > 0
        assert all("resource_type" in resource for resource in resources)
        assert all("collection_timestamp" in resource for resource in resources)
```

## 성능 최적화

### 1. 배치 처리
```python
def collect_clusters_batch(self, batch_size=100):
    """클러스터 배치 수집"""
    clusters = []
    page_token = None
    
    while True:
        response = self.connector.list_clusters_page(batch_size, page_token)
        clusters.extend(response.get('clusters', []))
        page_token = response.get('nextPageToken')
        
        if not page_token:
            break
    
    return clusters
```

### 2. 병렬 처리
```python
import concurrent.futures

def collect_node_pools_parallel(self, clusters, max_workers=5):
    """여러 클러스터의 노드 풀 병렬 수집"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_cluster = {
            executor.submit(self._collect_node_pools_by_cluster, cluster): cluster
            for cluster in clusters
        }
        
        results = []
        for future in concurrent.futures.as_completed(future_to_cluster):
            cluster = future_to_cluster[future]
            try:
                node_pools = future.result()
                results.extend(node_pools)
            except Exception as e:
                self.logger.error(f"클러스터 {cluster['name']}: 노드 풀 수집 실패 - {e}")
        
        return results
```

### 3. 캐싱 구현
```python
from functools import lru_cache

class GKEManager(BaseManager):
    @lru_cache(maxsize=128)
    def get_cached_cluster_info(self, cluster_name):
        """클러스터 정보 캐싱"""
        return self.connector.get_cluster(cluster_name)
```

## 에러 처리 및 로깅

### 1. 에러 처리
```python
def handle_collection_error(self, error, resource_type):
    """수집 에러 처리"""
    error_info = {
        "resource_type": resource_type,
        "error": str(error),
        "timestamp": datetime.utcnow().isoformat(),
        "project_id": self.project_id,
        "location": self.location
    }
    
    self.logger.error(f"리소스 수집 실패: {error_info}")
    
    # 에러 메트릭 업데이트
    self.update_error_metrics(resource_type, error)
    
    raise CollectionError(f"{resource_type} 수집 실패: {error}")
```

### 2. 로깅 설정
```python
import logging

def setup_logging(self):
    """로깅 설정"""
    logger = logging.getLogger("gke_collector")
    logger.setLevel(logging.INFO)
    
    # 파일 핸들러
    file_handler = logging.FileHandler("gke_collection.log")
    file_handler.setLevel(logging.DEBUG)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
```

## 배포 및 운영

### 1. Docker 설정
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/

CMD ["python", "-m", "spaceone.inventory.service.collector_service"]
```

### 2. 헬스 체크
```python
def health_check(self):
    """헬스 체크"""
    try:
        # 간단한 API 호출로 연결 상태 확인
        self.connector.list_clusters(page_size=1)
        return {"status": "healthy", "service": "gke_collector"}
    except Exception as e:
        return {"status": "unhealthy", "service": "gke_collector", "error": str(e)}
```

## 모니터링 및 메트릭

### 1. 성능 메트릭
```python
def collect_metrics(self):
    """성능 메트릭 수집"""
    metrics = {
        "collection_start_time": datetime.now().isoformat(),
        "total_resources": 0,
        "clusters_count": 0,
        "node_pools_count": 0,
        "api_calls": 0,
        "errors": 0,
        "duration": 0
    }
    
    start_time = time.time()
    
    try:
        resources = self.collect_all_resources()
        
        # 리소스별 카운트
        for resource in resources:
            resource_type = resource.get("resource_type", "")
            if resource_type == "gke_cluster":
                metrics["clusters_count"] += 1
            elif resource_type == "gke_node_pool":
                metrics["node_pools_count"] += 1
        
        metrics["total_resources"] = len(resources)
        metrics["duration"] = time.time() - start_time
        metrics["status"] = "success"
        
    except Exception as e:
        metrics["status"] = "error"
        metrics["error_message"] = str(e)
        metrics["duration"] = time.time() - start_time
    
    return metrics
```

### 2. 클러스터 상태 모니터링
```python
def monitor_cluster_health(self, cluster):
    """클러스터 상태 모니터링"""
    health_info = {
        "cluster_name": cluster["name"],
        "status": cluster["status"],
        "node_count": cluster.get("currentNodeCount", 0),
        "version": cluster.get("currentMasterVersion", "unknown"),
        "health_timestamp": datetime.utcnow().isoformat(),
        "health_score": 100
    }
    
    # 노드 풀 상태 확인
    node_pools = cluster.get("nodePools", [])
    unhealthy_pools = [pool for pool in node_pools if pool.get("status") != "RUNNING"]
    
    if unhealthy_pools:
        health_info["unhealthy_node_pools"] = len(unhealthy_pools)
        health_info["health_status"] = "degraded"
        health_info["health_score"] = max(0, 100 - (len(unhealthy_pools) * 20))
    else:
        health_info["health_status"] = "healthy"
    
    return health_info
```

### 2. 통합 테스트
```python
# test/test_gke_integration.py

import pytest
from unittest.mock import Mock, patch
from spaceone.inventory.service.collector_service import CollectorService

class TestGKEIntegration:
    def setup_method(self):
        self.credentials = Mock()
        self.project_id = "test-project"
        self.location = "us-central1"
        self.service = CollectorService()
    
    def test_collect_gke_resources_integration(self):
        """GKE 리소스 통합 수집 테스트"""
        # Given
        mock_clusters = [
            {
                "name": "projects/test-project/locations/us-central1/clusters/test-cluster",
                "status": "RUNNING"
            }
        ]
        mock_node_pools = [{"name": "default-pool"}]
        mock_nodes = [{"name": "node-1"}]
        
        with patch('spaceone.inventory.manager.kubernetes_engine.cluster_manager.GKEClusterManager.collect_clusters', return_value=mock_clusters), \
             patch('spaceone.inventory.manager.kubernetes_engine.node_pool_manager.GKENodePoolManager.collect_all_resources', return_value=mock_node_pools + mock_nodes):
            # When
            result = self.service.collect_gke_resources(
                self.credentials, 
                self.project_id, 
                self.location
            )
            
            # Then
            assert len(result) == 3  # 클러스터 1개 + 노드풀 1개 + 노드 1개
            assert any(r["resource_type"] == "gke_cluster" for r in result)
            assert any(r["resource_type"] == "gke_node_pool" for r in result)
            assert any(r["resource_type"] == "gke_node" for r in result)
    
    def test_api_version_selection(self):
        """API 버전 선택 테스트"""
        # Given
        mock_fleets = [{"name": "test-fleet"}]
        
        with patch('spaceone.inventory.manager.kubernetes_engine.cluster_manager.GKEClusterManager.collect_fleets', return_value=mock_fleets):
            # When
            result = self.service.collect_gke_resources(
                self.credentials, 
                self.project_id, 
                self.location, 
                "v1beta1"
            )
            
            # Then
            # v1beta1에서는 Fleet 정보도 수집 가능
            assert len(result) >= 1

## 문제 해결

### 1. 일반적인 문제들

#### 권한 오류
```
Error 403: The caller does not have permission
```
**해결 방법:**
1. Google Cloud Console에서 Container Engine API 활성화
2. IAM 권한 확인 및 수정
3. Service Account 키 파일 확인

#### 리소스 없음
```
Error 404: Requested entity was not found
```
**해결 방법:**
1. 프로젝트 ID 및 리전 확인
2. GKE 클러스터 존재 여부 확인
3. 리전 설정 확인

#### 타임아웃 오류
```
Error 408: Request timeout
```
**해결 방법:**
1. 타임아웃 값 증가
2. 배치 크기 감소
3. 네트워크 지연 시간 확인

### 2. 디버깅 팁
- API 응답 로깅 활성화
- 네트워크 지연 시간 모니터링
- 메모리 사용량 추적
- API 호출 빈도 제한
- 클러스터 크기별 성능 분석

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

## 참고 자료

- [GKE API 문서](https://cloud.google.com/kubernetes-engine/docs/reference/rest)
- [Container API 문서](https://cloud.google.com/kubernetes-engine/docs/reference/rest/v1)
- [IAM 권한 가이드](https://cloud.google.com/iam/docs/understanding-roles)
- [API 할당량 관리](https://cloud.google.com/apis/docs/quotas)
- [GKE 보안 모범 사례](https://cloud.google.com/kubernetes-engine/docs/how-to/hardening-your-cluster)
