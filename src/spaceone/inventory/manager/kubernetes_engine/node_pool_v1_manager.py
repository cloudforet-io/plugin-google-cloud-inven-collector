"""KubernetesEngine Node Pool Manager (v1 API)."""

import logging
from typing import List, Dict, Any, Tuple

from spaceone.inventory.connector.kubernetes_engine.cluster_v1 import (
    GKEClusterV1Connector,
)
from spaceone.inventory.connector.kubernetes_engine.node_pool_v1 import (
    GKENodePoolV1Connector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager

from spaceone.inventory.model.kubernetes_engine.node_pool.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)

from spaceone.inventory.model.kubernetes_engine.node_pool.cloud_service import (
    NodePoolResource,
    NodePoolResponse,
    NodePool,
)
from spaceone.inventory.model.kubernetes_engine.cluster.data import convert_datetime
from spaceone.inventory.libs.schema.cloud_service import ErrorResourceResponse

_LOGGER = logging.getLogger(__name__)


class GKENodePoolV1Manager(GoogleCloudManager):
    """GKE Node Pool Manager (v1 API)."""

    connector_name = "GKENodePoolV1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    cloud_service_group = "KubernetesEngine"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.params = kwargs  # params를 인스턴스 변수로 저장
        self.api_version = "v1"

    def list_node_pools(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """GKE 노드풀 목록을 조회합니다 (v1 API).

        Args:
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            GKE 노드풀 목록.

        Raises:
            Exception: GKE API 호출 중 오류 발생 시.
        """
        # params를 인스턴스 변수로 저장
        self.params = params
        
        try:
            cluster_connector: GKEClusterV1Connector = self.locator.get_connector(
                "GKEClusterV1Connector", **params
            )
            node_pool_connector: GKENodePoolV1Connector = self.locator.get_connector(
                self.connector_name, **params
            )

            # params에서 project_id 가져오기 (우선순위: secret_data > params 직접)
            project_id = params.get("secret_data", {}).get("project_id") or params.get("project_id") or params.get("projectId")
            
            if not project_id:
                _LOGGER.warning("project_id not found in params, will try to extract from cluster names")
            
            # 모든 클러스터를 조회하여 각 클러스터의 노드풀을 수집
            clusters = cluster_connector.list_clusters()
            all_node_groups = []

            _LOGGER.info(f"Found {len(clusters)} GKE clusters for node pool collection")

            for cluster in clusters:
                cluster_name = cluster.get("name")
                location = cluster.get("location")
                
                if cluster_name and location:
                    try:
                        node_pools = node_pool_connector.list_node_pools(
                            cluster_name, location
                        )
                        _LOGGER.info(f"Found {len(node_pools)} node pools in cluster {cluster_name}")
                        
                        for node_pool in node_pools:
                            # 클러스터 정보를 노드풀에 추가
                            node_pool["clusterName"] = cluster_name
                            node_pool["clusterLocation"] = location
                            
                            # project_id 설정 (우선순위: params > cluster > 클러스터 이름에서 추출)
                            if project_id:
                                node_pool["projectId"] = project_id
                            elif cluster.get("projectId"):
                                node_pool["projectId"] = cluster.get("projectId")
                            else:
                                # 클러스터 이름에서 project_id 추출 (예: projects/mkkang-project/locations/asia-northeast3/clusters/mkkang-cluster-1)
                                try:
                                    if "/projects/" in cluster_name:
                                        extracted_project_id = cluster_name.split("/projects/")[1].split("/")[0]
                                        node_pool["projectId"] = extracted_project_id
                                        _LOGGER.info(f"Extracted project_id from cluster name: {extracted_project_id}")
                                    else:
                                        node_pool["projectId"] = "unknown"
                                        _LOGGER.warning(f"Could not extract project_id from cluster name: {cluster_name}")
                                except Exception as e:
                                    node_pool["projectId"] = "unknown"
                                    _LOGGER.warning(f"Failed to extract project_id from cluster name {cluster_name}: {e}")
                            
                            all_node_groups.append(node_pool)
                    except Exception as e:
                        _LOGGER.warning(
                            f"Failed to get node pools for cluster {cluster_name}: {e}"
                        )

            _LOGGER.info(f"Total {len(all_node_groups)} GKE node pools found (v1)")
            return all_node_groups
        except Exception as e:
            _LOGGER.error(f"Failed to list GKE node pools (v1): {e}")
            return []

    def get_node_group(
        self, cluster_name: str, location: str, node_pool_name: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """특정 GKE 노드 그룹 정보를 조회합니다 (v1 API).

        Args:
            cluster_name: 클러스터 이름.
            location: 클러스터 위치.
            node_pool_name: 노드풀 이름.
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            GKE 노드 그룹 정보 딕셔너리.

        Raises:
            Exception: GKE API 호출 중 오류 발생 시.
        """
        try:
            node_pool_connector: GKENodePoolV1Connector = self.locator.get_connector(
                self.connector_name, **params
            )

            node_pool = node_pool_connector.get_node_pool(cluster_name, location, node_pool_name)
            if node_pool:
                node_pool["clusterName"] = cluster_name
                node_pool["clusterLocation"] = location
                _LOGGER.info(f"Retrieved node group {node_pool_name} (v1)")
                return node_pool
            return {}
        except Exception as e:
            _LOGGER.error(f"Failed to get node group {node_pool_name} (v1): {e}")
            return {}

    def list_node_group_operations(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """GKE 노드 그룹 작업 목록을 조회합니다 (v1 API).

        Args:
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            GKE 노드 그룹 작업 목록.

        Raises:
            Exception: GKE API 호출 중 오류 발생 시.
        """
        try:
            cluster_connector: GKEClusterV1Connector = self.locator.get_connector(
                "GKEClusterV1Connector", **params
            )

            operations = cluster_connector.list_operations()
            # 노드 그룹 관련 작업만 필터링
            node_group_operations = [
                op for op in operations 
                if op.get("operationType") and "nodepool" in op.get("operationType", "").lower()
            ]
            _LOGGER.info(f"Found {len(node_group_operations)} GKE node group operations (v1)")
            return node_group_operations
        except Exception as e:
            _LOGGER.error(f"Failed to list GKE node group operations (v1): {e}")
            return []

    def get_node_pool_metrics(
        self, cluster_name: str, location: str, node_pool_name: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """GKE 노드풀 메트릭을 조회합니다 (v1 API).

        Args:
            cluster_name: 클러스터 이름.
            location: 클러스터 위치.
            node_pool_name: 노드풀 이름.
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            GKE 노드 그룹 메트릭 정보.

        Raises:
            Exception: GKE API 호출 중 오류 발생 시.
        """
        try:
            # 임시 메트릭 데이터 반환
            metrics = {
                "cpu_usage": "0.0",
                "memory_usage": "0.0",
                "disk_usage": "0.0",
                "node_count": "0",
            }
            _LOGGER.info(f"Retrieved metrics for node pool {node_pool_name} (v1)")
            return metrics
        except Exception as e:
            _LOGGER.error(f"Failed to get metrics for node pool {node_pool_name} (v1): {e}")
            return {}

    def get_node_pool_nodes(
        self, cluster_name: str, location: str, node_pool_name: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """GKE 노드풀의 노드 목록을 조회합니다 (v1 API).
        Compute Engine API를 통해 노드 정보를 조회합니다.

        Args:
            cluster_name: 클러스터 이름.
            location: 클러스터 위치.
            node_pool_name: 노드풀 이름.
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            GKE 노드 목록.

        Raises:
            Exception: 데이터 수집 중 오류 발생 시.
        """
        try:
            # Compute Engine 도메인의 커넥터들을 직접 호출
            vm_connector = self.locator.get_connector("VMInstanceConnector", **params)
            instance_group_connector = self.locator.get_connector("InstanceGroupConnector", **params)
            
            # project_id를 직접 추출하여 사용
            project_id = params.get("secret_data", {}).get("project_id")
            if not project_id:
                _LOGGER.warning("project_id not found in params, cannot proceed with node collection")
                return []
            
            # GKE 클러스터 정보를 통해 정확한 location 타입 판단
            # 실제 API 호출 결과를 기반으로 location 타입 판단
            # 먼저 regional instance groups로 시도
            is_regional = False
            instance_groups = []
            
            try:
                # regional instance groups 조회 시도
                all_instance_groups = instance_group_connector.list_instance_groups()
                
                # GKE 노드풀 이름 패턴 매칭 (예: gke-mkkang-cluster-1-default-pool-xxxxx)
                filtered_groups = []
                for group in all_instance_groups:
                    if (node_pool_name in group.get("name", "") or 
                        f"gke-{cluster_name.split('/')[-1]}-{node_pool_name}" in group.get("name", "")):
                        # regional 그룹인지 확인 (zone 필드가 없으면 regional)
                        if "zone" not in group:
                            filtered_groups.append(group)
                
                if filtered_groups:
                    instance_groups = filtered_groups
                    is_regional = True
                    _LOGGER.info(f"Found {len(instance_groups)} regional instance groups for node pool {node_pool_name}")
                    _LOGGER.info(f"Location '{location}' confirmed as region for node pool {node_pool_name}")
                else:
                    _LOGGER.info(f"No regional instance groups found for node pool {node_pool_name}, trying zonal")
                        
            except Exception as e:
                _LOGGER.debug(f"Failed to list regional instance groups: {e}")
                _LOGGER.info(f"Regional API failed, trying zonal for location '{location}'")
            
            # regional에서 찾지 못한 경우 zonal 시도
            if not is_regional:
                try:
                    all_instance_groups = instance_group_connector.list_instance_groups()
                    
                    # GKE 노드풀 이름 패턴 매칭
                    filtered_groups = []
                    for group in all_instance_groups:
                        if (node_pool_name in group.get("name", "") or 
                            f"gke-{cluster_name.split('/')[-1]}-{node_pool_name}" in group.get("name", "")):
                            # zonal 그룹인지 확인 (zone 필드가 있으면 zonal)
                            if "zone" in group and location in group.get("zone", ""):
                                filtered_groups.append(group)
                    
                    if filtered_groups:
                        instance_groups = filtered_groups
                        _LOGGER.info(f"Found {len(instance_groups)} zonal instance groups for node pool {node_pool_name}")
                        _LOGGER.info(f"Location '{location}' confirmed as zone for node pool {node_pool_name}")
                except Exception as e:
                    _LOGGER.debug(f"Failed to list zonal instance groups: {e}")
                    _LOGGER.warning(f"Both regional and zonal APIs failed for location '{location}'")
            
            # 인스턴스 그룹에서 실제 인스턴스 정보 조회
            nodes = []
            instance_groups_info = []  # 인스턴스 그룹 정보를 저장할 리스트
            
            for group in instance_groups:
                group_name = group.get("name")
                _LOGGER.info(f"Processing instance group: {group_name}")
                
                # 인스턴스 그룹 정보 저장
                group_info = {
                    "name": group_name,
                    "type": "regional" if is_regional else "zonal",
                    "location": location,
                    "selfLink": group.get("selfLink", ""),
                    "creationTimestamp": group.get("creationTimestamp", ""),
                    "description": group.get("description", ""),
                    "network": group.get("network", ""),
                    "subnetwork": group.get("subnetwork", ""),
                    "zone": group.get("zone", ""),
                    "region": group.get("region", ""),
                    "size": group.get("size", 0),
                    "namedPorts": group.get("namedPorts", []),
                    "instances": []
                }
                
                try:
                    if is_regional:
                        # regional instance group의 경우 region 내의 모든 zone에서 인스턴스 조회
                        # regional 클러스터는 보통 3개의 zone에 분산됨
                        zones_in_region = self._get_zones_in_region(vm_connector, location)
                        _LOGGER.info(f"Zones in region {location}: {zones_in_region}")
                        
                        for zone in zones_in_region:
                            try:
                                # InstanceGroupConnector의 list_instances 메서드에 project_id를 직접 전달
                                instances = self._get_instances_from_group(
                                    instance_group_connector, group_name, zone, project_id
                                )
                                for instance in instances:
                                    node_info = self._extract_node_info(instance, zone)
                                    nodes.append(node_info)
                                    group_info["instances"].append(node_info)
                                    _LOGGER.info(f"Found node {node_info['name']} in zone {zone}")
                            except Exception as e:
                                _LOGGER.debug(f"Failed to get instances from regional group {group_name} in zone {zone}: {e}")
                    else:
                        # zonal instance group의 경우 해당 zone에서만 인스턴스 조회
                        instances = self._get_instances_from_group(
                            instance_group_connector, group_name, location, project_id
                        )
                        for instance in instances:
                            node_info = self._extract_node_info(instance, location)
                            nodes.append(node_info)
                            group_info["instances"].append(node_info)
                            _LOGGER.info(f"Found node {node_info['name']} in zone {location}")
                            
                except Exception as e:
                    _LOGGER.warning(f"Failed to get instances from group {group_name}: {e}")
                
                instance_groups_info.append(group_info)
            
            _LOGGER.info(f"Retrieved {len(nodes)} nodes via Compute Engine API for node pool {node_pool_name}")
            
            # 노드 정보와 인스턴스 그룹 정보를 함께 반환
            return {
                "nodes": nodes,
                "instance_groups": instance_groups_info,
                "total_nodes": len(nodes),
                "total_groups": len(instance_groups_info)
            }
            
        except Exception as e:
            _LOGGER.error(f"Failed to get nodes for node pool {node_pool_name} (v1): {e}")
            return []

    def _get_instances_from_group(self, instance_group_connector, group_name, location, project_id):
        """
        InstanceGroupConnector를 사용하여 특정 그룹의 인스턴스 목록을 조회합니다.
        GKE 클러스터의 실제 구조에 맞게 location을 처리합니다.
        """
        try:
            # self.params에서 secret_data를 가져와서 사용
            secret_data = self.params.get("secret_data", {})
            if not secret_data:
                _LOGGER.warning("secret_data not found in self.params")
                return []
            
            _LOGGER.info(f"Starting search for instance group {group_name} in location {location}")
            
            # GKE 클러스터의 location 구조 분석
            # asia-northeast3 -> region (3개의 zone에 분산)
            # asia-northeast3-a -> zone (단일 zone)
            
            # 1. 먼저 주어진 location에서 시도 (region이든 zone이든)
            instances = self._try_get_instances(instance_group_connector, group_name, location)
            if instances:
                _LOGGER.info(f"Found instances directly in location {location}")
                return instances
            
            # 2. location이 region인 경우 (예: asia-northeast3), 해당 region의 모든 zone에서 시도
            if len(location.split('-')) <= 2:  # region 형태
                region = location
                zones_in_region = self._get_zones_in_region(region)
                _LOGGER.info(f"Location {location} is a region. Trying to find instance group {group_name} in zones: {zones_in_region}")
                
                for zone in zones_in_region:
                    _LOGGER.info(f"Searching in zone: {zone}")
                    instances = self._try_get_instances(instance_group_connector, group_name, zone)
                    if instances:
                        _LOGGER.info(f"Found {len(instances)} instances in zone {zone}")
                        return instances
                    else:
                        _LOGGER.info(f"No instances found in zone {zone}")
            
            # 3. location이 zone인 경우 (예: asia-northeast3-a), 해당 zone에서만 시도
            else:  # zone 형태
                _LOGGER.info(f"Location {location} is a zone. Instance group should be in this zone.")
                # zone에서 찾지 못했다면 더 이상 시도하지 않음
                _LOGGER.warning(f"Instance group {group_name} not found in zone {location}")
                return []
            
            _LOGGER.warning(f"Instance group {group_name} not found in any location")
            return []
            
        except Exception as e:
            _LOGGER.warning(f"Failed to get instances from group {group_name} in location {location}: {e}")
            return []
    
    def _try_get_instances(self, instance_group_connector, group_name, location):
        """
        특정 location에서 인스턴스 그룹의 인스턴스를 조회합니다.
        """
        try:
            # location이 region인지 zone인지 판단
            is_region = len(location.split('-')) <= 2  # asia-northeast3 형태
            
            if is_region:
                # regional instance group 조회
                instances = instance_group_connector.list_instances(
                    instance_group=group_name,
                    loc=location,
                    loc_type="region"
                )
                if instances:
                    _LOGGER.info(f"Found {len(instances)} instances in regional instance group {group_name} at {location}")
                    return instances
                    
            else:
                # zonal instance group 조회
                instances = instance_group_connector.list_instances(
                    instance_group=group_name,
                    loc=location,
                    loc_type="zone"
                )
                if instances:
                    _LOGGER.info(f"Found {len(instances)} instances in zonal instance group {group_name} at {location}")
                    return instances
            
            return []
            
        except Exception as e:
            _LOGGER.debug(f"Failed to get instances from {location} for group {group_name}: {e}")
            return []
    
    def _get_zones_in_region(self, region):
        """
        특정 region에 속한 zone 목록을 반환합니다.
        """
        # 일반적인 GCP region-zone 패턴
        zone_patterns = {
            "asia-northeast3": ["asia-northeast3-a", "asia-northeast3-b", "asia-northeast3-c"],
            "us-central1": ["us-central1-a", "us-central1-b", "us-central1-c"],
            "europe-west1": ["europe-west1-a", "europe-west1-b", "europe-west1-c"],
            "us-east1": ["us-east1-a", "us-east1-b", "us-east1-c"],
            "europe-west4": ["europe-west4-a", "europe-west4-b", "europe-west4-c"],
        }
        
        return zone_patterns.get(region, [])



    def _extract_node_info(self, instance, zone):
        """
        Compute Engine 인스턴스 정보에서 노드 정보를 추출합니다.
        """
        try:
            return {
                "name": instance.get("name", ""),
                "status": instance.get("status", ""),
                "machineType": instance.get("machineType", "").split("/")[-1],
                "zone": zone,
                "internalIP": instance.get("networkInterfaces", [{}])[0].get("networkIP", ""),
                "externalIP": instance.get("networkInterfaces", [{}])[0].get("accessConfigs", [{}])[0].get("natIP", ""),
                "createTime": instance.get("creationTimestamp", ""),
                "labels": instance.get("labels", {}),
                "taints": [],  # GKE taint 정보는 별도로 조회 필요
            }
        except Exception as e:
            _LOGGER.warning(f"Failed to extract node info from instance: {e}")
            return {
                "name": "unknown",
                "status": "unknown",
                "machineType": "unknown",
                "zone": zone,
                "internalIP": "",
                "externalIP": "",
                "createTime": "",
                "labels": {},
                "taints": [],
            }

    def collect_cloud_service(
        self, params: Dict[str, Any]
    ) -> Tuple[List[Any], List[ErrorResourceResponse]]:
        """GKE 노드 그룹 정보를 수집합니다 (v1 API).

        Args:
            params: 수집에 필요한 파라미터 딕셔너리.

        Returns:
            수집된 클라우드 서비스 목록과 오류 응답 목록의 튜플.

        Raises:
            Exception: 데이터 수집 중 오류 발생 시.
        """
        _LOGGER.info("** GKE Node Pool V1 START **")

        collected_cloud_services = []
        error_responses = []

        try:
            project_id = params["secret_data"]["project_id"]
            # GKE 노드 그룹 목록 조회
            node_groups = self.list_node_pools(params)
            _LOGGER.info(f"Processing {len(node_groups)} node groups")

            if not node_groups:
                _LOGGER.warning("No node groups found to process")
                return collected_cloud_services, error_responses

            for node_group in node_groups:
                try:
                    cluster_name = node_group.get("clusterName")
                    location = node_group.get("clusterLocation")
                    node_pool_name = node_group.get("name")

                    if not all([cluster_name, location, node_pool_name]):
                        _LOGGER.warning(f"Skipping node group due to missing required fields: {node_group.get('name', 'unknown')}")
                        continue

                    # project_id 검증 및 로깅
                    if not project_id or project_id == "unknown":
                        _LOGGER.warning(f"Node group {node_pool_name} has invalid project_id: {project_id}")
                        # project_id가 없어도 계속 진행 (다른 정보는 수집 가능)
                        project_id = project_id or "unknown"

                    _LOGGER.info(f"Processing node group: {node_pool_name} in cluster: {cluster_name} (project: {project_id})")

                    # 메트릭 정보 조회
                    metrics = self.get_node_pool_metrics(
                        cluster_name, location, node_pool_name, params
                    )

                    # 노드 정보 조회
                    nodes_info = self.get_node_pool_nodes(
                        cluster_name, location, node_pool_name, params
                    )

                    # 기본 노드 풀 데이터 준비 (NodePool 모델에 맞게 수정)
                    node_pool_data = {
                        "name": str(node_pool_name),
                        "cluster_name": str(cluster_name),
                        "location": str(location),
                        "project_id": str(project_id),
                        "version": str(node_group.get("version", "")),
                        "status": str(node_group.get("status", "")),
                        "initial_node_count": int(node_group.get("initialNodeCount", 0)) if node_group.get("initialNodeCount") else 0,
                        "create_time": convert_datetime(node_group.get("createTime")),
                        "update_time": convert_datetime(node_group.get("updateTime")),
                        "api_version": "v1",
                        "self_link": node_group.get("selfLink", ""),
                    }

                    # config 정보 추가
                    if "config" in node_group:
                        config = node_group["config"]
                        node_pool_data["config"] = {
                            "machine_type": str(config.get("machineType", "")),
                            "disk_size_gb": int(config.get("diskSizeGb", 0)) if config.get("diskSizeGb") else 0,
                            "disk_type": str(config.get("diskType", "")),
                            "image_type": str(config.get("imageType", "")),
                            "oauth_scopes": config.get("oauthScopes", []),
                            "service_account": str(config.get("serviceAccount", "")),
                            "metadata": config.get("metadata", {}),
                            "labels": config.get("labels", {}),
                            "tags": config.get("tags", []),
                            "preemptible": config.get("preemptible", False),
                            "spot": config.get("spot", False),
                            "local_ssd_count": int(config.get("localSsdCount", 0)) if config.get("localSsdCount") else 0,
                            "min_cpu_platform": str(config.get("minCpuPlatform", "")),
                        }

                    # autoscaling 정보 추가
                    if "autoscaling" in node_group:
                        autoscaling = node_group["autoscaling"]
                        node_pool_data["autoscaling"] = {
                            "enabled": bool(autoscaling.get("enabled", False)),
                            "min_node_count": int(autoscaling.get("minNodeCount", 0)) if autoscaling.get("minNodeCount") else 0,
                            "max_node_count": int(autoscaling.get("maxNodeCount", 0)) if autoscaling.get("maxNodeCount") else 0,
                            "total_min_node_count": int(autoscaling.get("totalMinNodeCount", 0)) if autoscaling.get("totalMinNodeCount") else 0,
                            "total_max_node_count": int(autoscaling.get("totalMaxNodeCount", 0)) if autoscaling.get("totalMaxNodeCount") else 0,
                            "location_policy": str(autoscaling.get("locationPolicy", "")),
                        }

                    # management 정보 추가
                    if "management" in node_group:
                        management = node_group["management"]
                        node_pool_data["management"] = {
                            "auto_repair": bool(management.get("autoRepair", False)),
                            "auto_upgrade": bool(management.get("autoUpgrade", False)),
                            "upgrade_options": management.get("upgradeOptions", {}),
                        }

                    # 메트릭 정보 추가
                    if metrics:
                        node_pool_data["metrics"] = metrics

                    # 노드 정보 추가
                    if nodes_info:
                        node_pool_data["nodes"] = nodes_info["nodes"]
                        node_pool_data["instance_groups"] = nodes_info["instance_groups"]
                        node_pool_data["total_nodes"] = nodes_info["total_nodes"]
                        node_pool_data["total_groups"] = nodes_info["total_groups"]

                    # NodePool 모델 생성
                    node_pool_data_model = NodePool(node_pool_data, strict=False)

                    # NodePoolResource 생성
                    node_pool_resource = NodePoolResource(
                        {
                            "name": node_pool_data.get("name"),
                            "data": node_pool_data_model,
                            "reference": {
                                "resource_id": f"{cluster_name}/{location}/{node_pool_name}",
                                "external_link": f"https://console.cloud.google.com/kubernetes/nodepool/detail/{location}/{cluster_name}/{node_pool_name}/details?project={project_id}",
                            },
                            "region_code": location,
                            "account": project_id,
                        }
                    )

                    ##################################
                    # 4. Make Collected Region Code
                    ##################################
                    self.set_region_code(location)

                    # NodePoolResponse 생성
                    node_pool_response = NodePoolResponse(
                        {"resource": node_pool_resource}
                    )

                    collected_cloud_services.append(node_pool_response)
                    _LOGGER.info(f"Successfully processed node group: {node_pool_name}")

                except Exception as e:
                    _LOGGER.error(f"[collect_cloud_service] => {e}", exc_info=True)
                    error_responses.append(
                        self.generate_error_response(e, self.cloud_service_group, "NodeGroup")
                    )

            _LOGGER.info(f"Successfully collected {len(collected_cloud_services)} node group resources")

        except Exception as e:
            _LOGGER.error(f"Failed to collect cloud services: {e}", exc_info=True)
            error_responses.append(
                self.generate_error_response(e, self.cloud_service_group, "NodeGroup")
            )

        _LOGGER.info("** GKE Node Pool V1 END **")
        return collected_cloud_services, error_responses
