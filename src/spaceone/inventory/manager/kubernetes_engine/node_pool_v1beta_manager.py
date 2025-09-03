
"""KubernetesEngine Node Group Manager (v1beta1 API)."""

import logging
from typing import List, Dict, Any, Tuple

from spaceone.inventory.connector.kubernetes_engine.cluster_v1beta import (
    GKEClusterV1BetaConnector,
)
from spaceone.inventory.connector.kubernetes_engine.node_pool_v1beta import (
    GKENodePoolV1BetaConnector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager

from spaceone.inventory.model.kubernetes_engine.cluster.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)

from spaceone.inventory.model.kubernetes_engine.cluster.cloud_service import (
    GKEClusterResource as GKENodeGroupResource,
    GKEClusterResponse as GKENodeGroupResponse,
)
from spaceone.inventory.model.kubernetes_engine.cluster.data import (
    GKECluster as GKENodeGroup,
)
from spaceone.inventory.libs.schema.cloud_service import ErrorResourceResponse

_LOGGER = logging.getLogger(__name__)


class GKENodePoolV1BetaManager(GoogleCloudManager):
    """GKE Node Pool Manager (v1beta1 API)."""

    connector_name = "GKENodePoolV1BetaConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    cloud_service_group = "KubernetesEngine"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.params = kwargs  # params를 인스턴스 변수로 저장
        self.api_version = "v1beta1"

    def list_node_pools(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """GKE 노드풀 목록을 조회합니다 (v1beta1 API).

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
            cluster_connector: GKEClusterV1BetaConnector = self.locator.get_connector(
                "GKEClusterV1BetaConnector", **params
            )
            node_pool_connector: GKENodePoolV1BetaConnector = self.locator.get_connector(
                self.connector_name, **params
            )

            # params에서 project_id 가져오기 (우선순위: secret_data > params 직접)
            project_id = params.get("secret_data", {}).get("project_id") or params.get("project_id") or params.get("projectId")
            
            if not project_id:
                _LOGGER.warning("project_id not found in params, will try to extract from cluster names (v1beta1)")
            
            # 모든 클러스터를 조회하여 각 클러스터의 노드풀을 수집
            clusters = cluster_connector.list_clusters()
            all_node_groups = []

            _LOGGER.info(f"Found {len(clusters)} GKE clusters for node pool collection (v1beta1)")

            for cluster in clusters:
                cluster_name = cluster.get("name")
                location = cluster.get("location")
                
                if cluster_name and location:
                    try:
                        node_pools = node_pool_connector.list_node_pools(
                            cluster_name, location
                        )
                        _LOGGER.info(f"Found {len(node_pools)} node pools in cluster {cluster_name} (v1beta1)")
                        
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
                                        _LOGGER.info(f"Extracted project_id from cluster name: {extracted_project_id} (v1beta1)")
                                    else:
                                        node_pool["projectId"] = "unknown"
                                        _LOGGER.warning(f"Could not extract project_id from cluster name: {cluster_name} (v1beta1)")
                                except Exception as e:
                                    node_pool["projectId"] = "unknown"
                                    _LOGGER.warning(f"Failed to extract project_id from cluster name {cluster_name} (v1beta1): {e}")
                            
                            all_node_groups.append(node_pool)
                    except Exception as e:
                        _LOGGER.warning(
                            f"Failed to get node pools for cluster {cluster_name}: {e}"
                        )

            _LOGGER.info(f"Total {len(all_node_groups)} GKE node pools found (v1beta1)")
            return all_node_groups
        except Exception as e:
            _LOGGER.error(f"Failed to list GKE node pools (v1beta1): {e}")
            return []

    def get_node_pool(
        self, cluster_name: str, location: str, node_pool_name: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """특정 GKE 노드풀 정보를 조회합니다 (v1beta1 API).

        Args:
            cluster_name: 클러스터 이름.
            location: 클러스터 위치.
            node_pool_name: 노드풀 이름.
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            GKE 노드풀 정보 딕셔너리.

        Raises:
            Exception: GKE API 호출 중 오류 발생 시.
        """
        try:
            node_pool_connector: GKENodePoolV1BetaConnector = self.locator.get_connector(
                self.connector_name, **params
            )

            node_pool = node_pool_connector.get_node_pool(cluster_name, location, node_pool_name)
            if node_pool:
                node_pool["clusterName"] = cluster_name
                node_pool["clusterLocation"] = location
                _LOGGER.info(f"Retrieved node pool {node_pool_name} (v1beta1)")
                return node_pool
            return {}
        except Exception as e:
            _LOGGER.error(f"Failed to get node pool {node_pool_name} (v1beta1): {e}")
            return {}

    def list_node_pool_operations(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """GKE 노드풀 작업 목록을 조회합니다 (v1beta1 API).

        Args:
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            GKE 노드풀 작업 목록.

        Raises:
            Exception: GKE API 호출 중 오류 발생 시.
        """
        try:
            cluster_connector: GKEClusterV1BetaConnector = self.locator.get_connector(
                "GKEClusterV1BetaConnector", **params
            )

            operations = cluster_connector.list_operations()
            # 노드풀 관련 작업만 필터링
            node_pool_operations = [
                op for op in operations 
                if op.get("operationType") and "nodepool" in op.get("operationType", "").lower()
            ]
            _LOGGER.info(f"Found {len(node_pool_operations)} GKE node pool operations (v1beta1)")
            return node_pool_operations
        except Exception as e:
            _LOGGER.error(f"Failed to list GKE node pool operations (v1beta1): {e}")
            return []

    def list_fleets(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """GKE Fleet 목록을 조회합니다 (v1beta1 API).

        Args:
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            GKE Fleet 목록.

        Raises:
            Exception: GKE API 호출 중 오류 발생 시.
        """
        try:
            cluster_connector: GKEClusterV1BetaConnector = self.locator.get_connector(
                "GKEClusterV1BetaConnector", **params
            )

            fleets = cluster_connector.list_fleets()
            _LOGGER.info(f"Found {len(fleets)} GKE fleets (v1beta1)")
            return fleets
        except Exception as e:
            _LOGGER.error(f"Failed to list GKE fleets (v1beta1): {e}")
            return []

    def list_memberships(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """GKE Membership 목록을 조회합니다 (v1beta1 API).

        Args:
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            GKE Membership 목록.

        Raises:
            Exception: GKE API 호출 중 오류 발생 시.
        """
        try:
            cluster_connector: GKEClusterV1BetaConnector = self.locator.get_connector(
                "GKEClusterV1BetaConnector", **params
            )

            memberships = cluster_connector.list_memberships()
            _LOGGER.info(f"Found {len(memberships)} GKE memberships (v1beta1)")
            return memberships
        except Exception as e:
            _LOGGER.error(f"Failed to list GKE memberships (v1beta1): {e}")
            return []

    def get_node_pool_metrics(
        self, cluster_name: str, location: str, node_pool_name: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """GKE 노드풀 메트릭을 조회합니다 (v1beta1 API).

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
            _LOGGER.info(f"Retrieved metrics for node pool {node_pool_name} (v1beta1)")
            return metrics
        except Exception as e:
            _LOGGER.error(f"Failed to get metrics for node pool {node_pool_name} (v1beta1): {e}")
            return {}

    def get_node_pool_nodes(
        self, cluster_name: str, location: str, node_pool_name: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """GKE 노드풀의 노드 목록을 조회합니다 (v1beta1 API).
        Compute Engine API를 통해 노드 정보를 조회합니다.

        Args:
            cluster_name: 클러스터 이름.
            location: 클러스터 위치.
            node_pool_name: 노드풀 이름.
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            GKE 노드 목록과 인스턴스 그룹 정보를 포함한 딕셔너리.

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
                return {"nodes": [], "instance_groups": [], "total_nodes": 0, "total_groups": 0}
            
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
                    _LOGGER.info(f"Found {len(instance_groups)} regional instance groups for node pool {node_pool_name} (v1beta1)")
                    _LOGGER.info(f"Location '{location}' confirmed as region for node pool {node_pool_name} (v1beta1)")
                else:
                    _LOGGER.info(f"No regional instance groups found for node pool {node_pool_name}, trying zonal (v1beta1)")
                        
            except Exception as e:
                _LOGGER.debug(f"Failed to list regional instance groups (v1beta1): {e}")
                _LOGGER.info(f"Regional API failed, trying zonal for location '{location}' (v1beta1)")
            
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
                        _LOGGER.info(f"Found {len(instance_groups)} zonal instance groups for node pool {node_pool_name} (v1beta1)")
                        _LOGGER.info(f"Location '{location}' confirmed as zone for node pool {node_pool_name} (v1beta1)")
                except Exception as e:
                    _LOGGER.debug(f"Failed to list zonal instance groups (v1beta1): {e}")
                    _LOGGER.warning(f"Both regional and zonal APIs failed for location '{location}' (v1beta1)")
            
            # 인스턴스 그룹에서 실제 인스턴스 정보 조회
            nodes = []
            instance_groups_info = []  # 인스턴스 그룹 정보를 저장할 리스트
            
            for group in instance_groups:
                group_name = group.get("name")
                _LOGGER.info(f"Processing instance group: {group_name} (v1beta1)")
                
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
                        _LOGGER.info(f"Zones in region {location}: {zones_in_region} (v1beta1)")
                        
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
                                    _LOGGER.info(f"Found node {node_info['name']} in zone {zone} (v1beta1)")
                            except Exception as e:
                                _LOGGER.debug(f"Failed to get instances from regional group {group_name} in zone {zone} (v1beta1): {e}")
                    else:
                        # zonal instance group의 경우 해당 zone에서만 인스턴스 조회
                        instances = self._get_instances_from_group(
                            instance_group_connector, group_name, location, project_id
                        )
                        for instance in instances:
                            node_info = self._extract_node_info(instance, location)
                            nodes.append(node_info)
                            group_info["instances"].append(node_info)
                            _LOGGER.info(f"Found node {node_info['name']} in zone {location} (v1beta1)")
                            
                except Exception as e:
                    _LOGGER.warning(f"Failed to get instances from group {group_name} (v1beta1): {e}")
                
                instance_groups_info.append(group_info)
            
            _LOGGER.info(f"Retrieved {len(nodes)} nodes via Compute Engine API for node pool {node_pool_name} (v1beta1)")
            
            # 노드 정보와 인스턴스 그룹 정보를 함께 반환
            return {
                "nodes": nodes,
                "instance_groups": instance_groups_info,
                "total_nodes": len(nodes),
                "total_groups": len(instance_groups_info)
            }
            
        except Exception as e:
            _LOGGER.error(f"Failed to get nodes for node pool {node_pool_name} (v1beta1): {e}")
            return {"nodes": [], "instance_groups": [], "total_nodes": 0, "total_groups": 0}

    def _get_zones_in_region(self, vm_connector, region):
        """
        특정 region에 속한 zone 목록을 조회합니다.
        """
        try:
            zones = vm_connector.list_zones()
            zones_in_region = []
            for zone in zones:
                if region in zone.get("name", ""):
                    zones_in_region.append(zone.get("name"))
            _LOGGER.debug(f"Found zones in region {region}: {zones_in_region}")
            return zones_in_region
        except Exception as e:
            _LOGGER.warning(f"Failed to get zones in region {region}: {e}")
            # 기본적으로 알려진 zone 패턴 사용
            if region == "asia-northeast3":
                return ["asia-northeast3-a", "asia-northeast3-b", "asia-northeast3-c"]
            elif region == "us-central1":
                return ["us-central1-a", "us-central1-b", "us-central1-c"]
            elif region == "europe-west1":
                return ["europe-west1-a", "europe-west1-b", "europe-west1-c"]
            else:
                return []

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
            
            _LOGGER.info(f"Starting search for instance group {group_name} in location {location} (v1beta1)")
            
            # GKE 클러스터의 location 구조 분석
            # asia-northeast3 -> region (3개의 zone에 분산)
            # asia-northeast3-a -> zone (단일 zone)
            
            # 1. 먼저 주어진 location에서 시도 (region이든 zone이든)
            instances = self._try_get_instances(instance_group_connector, group_name, location)
            if instances:
                _LOGGER.info(f"Found instances directly in location {location} (v1beta1)")
                return instances
            
            # 2. location이 region인 경우 (예: asia-northeast3), 해당 region의 모든 zone에서 시도
            if len(location.split('-')) <= 2:  # region 형태
                region = location
                zones_in_region = self._get_zones_in_region(region)
                _LOGGER.info(f"Location {location} is a region. Trying to find instance group {group_name} in zones: {zones_in_region} (v1beta1)")
                
                for zone in zones_in_region:
                    _LOGGER.info(f"Searching in zone: {zone} (v1beta1)")
                    instances = self._try_get_instances(instance_group_connector, group_name, zone)
                    if instances:
                        _LOGGER.info(f"Found {len(instances)} instances in zone {zone} (v1beta1)")
                        return instances
                    else:
                        _LOGGER.info(f"No instances found in zone {zone} (v1beta1)")
            
            # 3. location이 zone인 경우 (예: asia-northeast3-a), 해당 zone에서만 시도
            else:  # zone 형태
                _LOGGER.info(f"Location {location} is a zone. Instance group should be in this zone. (v1beta1)")
                # zone에서 찾지 못했다면 더 이상 시도하지 않음
                _LOGGER.warning(f"Instance group {group_name} not found in zone {location} (v1beta1)")
                return []
            
            _LOGGER.warning(f"Instance group {group_name} not found in any location (v1beta1)")
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
                    _LOGGER.info(f"Found {len(instances)} instances in regional instance group {group_name} at {location} (v1beta1)")
                    return instances
                    
            else:
                # zonal instance group 조회
                instances = instance_group_connector.list_instances(
                    instance_group=group_name,
                    loc=location,
                    loc_type="zone"
                )
                if instances:
                    _LOGGER.info(f"Found {len(instances)} instances in zonal instance group {group_name} at {location} (v1beta1)")
                    return instances
            
            return []
            
        except Exception as e:
            _LOGGER.info(f"Failed to get instances from {location} for group {group_name}: {e}")
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

    def collect_cloud_service(
        self, params: Dict[str, Any]
    ) -> Tuple[List[Any], List[ErrorResourceResponse]]:
        """GKE 노드 그룹 정보를 수집합니다 (v1beta1 API).

        Args:
            params: 수집에 필요한 파라미터 딕셔너리.

        Returns:
            수집된 클라우드 서비스 목록과 오류 응답 목록의 튜플.

        Raises:
            Exception: 데이터 수집 중 오류 발생 시.
        """
        _LOGGER.info("** GKE Node Pool V1Beta START **")

        collected_cloud_services = []
        error_responses = []

        try:
            project_id = params["secret_data"]["project_id"]
            # GKE 노드 그룹 목록 조회
            node_groups = self.list_node_pools(params)
            _LOGGER.info(f"Processing {len(node_groups)} node groups (v1beta1)")

            if not node_groups:
                _LOGGER.warning("No node groups found to process (v1beta1)")
                return collected_cloud_services, error_responses

            for node_group in node_groups:
                try:
                    cluster_name = node_group.get("clusterName")
                    location = node_group.get("clusterLocation")
                    node_pool_name = node_group.get("name")
                    project_id = node_group.get("projectId")

                    if not all([cluster_name, location, node_pool_name]):
                        _LOGGER.warning(f"Skipping node group due to missing required fields: {node_group.get('name', 'unknown')} (v1beta1)")
                        continue

                    # project_id 검증 및 로깅
                    if not project_id or project_id == "unknown":
                        _LOGGER.warning(f"Node group {node_pool_name} has invalid project_id: {project_id} (v1beta1)")
                        # project_id가 없어도 계속 진행 (다른 정보는 수집 가능)
                        project_id = project_id or "unknown"

                    _LOGGER.info(f"Processing node group: {node_pool_name} in cluster: {cluster_name} (project: {project_id}) (v1beta1)")

                    # 메트릭 정보 조회
                    metrics = self.get_node_pool_metrics(
                        cluster_name, location, node_pool_name, params
                    )

                    # 노드 정보 조회
                    nodes_info = self.get_node_pool_nodes(
                        cluster_name, location, node_pool_name, params
                    )
                    nodes = nodes_info["nodes"]
                    instance_groups = nodes_info["instance_groups"]

                    # 기본 노드 그룹 데이터 준비
                    node_group_data = {
                        "name": str(node_pool_name),
                        "clusterName": str(cluster_name),
                        "location": str(location),
                        "projectId": str(project_id),
                        "version": str(node_group.get("version", "")),
                        "status": str(node_group.get("status", "")),
                        "initialNodeCount": str(node_group.get("initialNodeCount", "")),
                        "createTime": node_group.get("createTime"),
                        "updateTime": node_group.get("updateTime"),
                        "api_version": "v1beta1",
                    }

                    # config 정보 추가
                    if "config" in node_group:
                        config = node_group["config"]
                        node_group_data["config"] = {
                            "machineType": str(config.get("machineType", "")),
                            "diskSizeGb": str(config.get("diskSizeGb", "")),
                            "diskType": str(config.get("diskType", "")),
                            "imageType": str(config.get("imageType", "")),
                            "initialNodeCount": str(config.get("initialNodeCount", "")),
                            "oauthScopes": config.get("oauthScopes", []),
                            "serviceAccount": str(config.get("serviceAccount", "")),
                            "metadata": config.get("metadata", {}),
                            "labels": config.get("labels", {}),
                            "tags": config.get("tags", {}),
                        }

                    # autoscaling 정보 추가
                    if "autoscaling" in node_group:
                        autoscaling = node_group["autoscaling"]
                        node_group_data["autoscaling"] = {
                            "enabled": str(autoscaling.get("enabled", "")),
                            "minNodeCount": str(autoscaling.get("minNodeCount", "")),
                            "maxNodeCount": str(autoscaling.get("maxNodeCount", "")),
                            "autoprovisioned": str(autoscaling.get("autoprovisioned", "")),
                        }

                    # management 정보 추가
                    if "management" in node_group:
                        management = node_group["management"]
                        node_group_data["management"] = {
                            "autoRepair": str(management.get("autoRepair", "")),
                            "autoUpgrade": str(management.get("autoUpgrade", "")),
                            "upgradeOptions": management.get("upgradeOptions", {}),
                        }

                    # 메트릭 정보 추가
                    if metrics:
                        node_group_data["metrics"] = metrics

                    # 노드 정보 추가
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

                    # 인스턴스 그룹 정보 추가
                    if instance_groups:
                        node_group_data["instance_groups"] = []
                        for group in instance_groups:
                            group_info = {
                                "name": str(group.get("name")),
                                "type": str(group.get("type")),
                                "location": str(group.get("location")),
                                "selfLink": str(group.get("selfLink")),
                                "creationTimestamp": str(group.get("creationTimestamp")),
                                "description": str(group.get("description")),
                                "network": str(group.get("network")),
                                "subnetwork": str(group.get("subnetwork")),
                                "zone": str(group.get("zone")),
                                "region": str(group.get("region")),
                                "size": str(group.get("size")),
                                "namedPorts": group.get("namedPorts"),
                                "instances": []
                            }
                            for instance in group.get("instances", []):
                                instance_info = {
                                    "name": str(instance.get("name")),
                                    "status": str(instance.get("status")),
                                    "machineType": str(instance.get("machineType")),
                                    "zone": str(instance.get("zone")),
                                    "internalIP": str(instance.get("internalIP")),
                                    "externalIP": str(instance.get("externalIP")),
                                    "createTime": instance.get("createTime"),
                                    "labels": instance.get("labels"),
                                    "taints": instance.get("taints"),
                                }
                                node_info["instances"].append(instance_info)
                            node_group_data["instance_groups"].append(group_info)

                    # GKENodeGroup 모델 생성
                    gke_node_group_data = GKENodeGroup(node_group_data, strict=False)

                    # GKENodeGroupResource 생성
                    node_group_resource = GKENodeGroupResource(
                        {
                            "name": node_group_data.get("name"),
                            "data": gke_node_group_data,
                            "reference": {
                                "resource_id": f"{cluster_name}/{location}/{node_pool_name}",
                                "external_link": f"https://console.cloud.google.com/kubernetes/clusters/details/{location}/{cluster_name}/nodepools/{node_pool_name}?project={project_id}",
                            },
                            "region_code": location,
                            "account": project_id,
                        }
                    )

                    ##################################
                    # 4. Make Collected Region Code
                    ##################################
                    self.set_region_code(location)

                    # GKENodeGroupResponse 생성
                    node_group_response = GKENodeGroupResponse(
                        {"resource": node_group_resource}
                    )

                    collected_cloud_services.append(node_group_response)
                    _LOGGER.info(f"Successfully processed node group: {node_pool_name} (v1beta1)")

                except Exception as e:
                    _LOGGER.error(f"[collect_cloud_service] => {e}", exc_info=True)
                    error_responses.append(
                        self.generate_error_response(e, self.cloud_service_group, "NodeGroup")
                    )

            _LOGGER.info(f"Successfully collected {len(collected_cloud_services)} node group resources (v1beta1)")

        except Exception as e:
            _LOGGER.error(f"Failed to collect cloud services (v1beta1): {e}", exc_info=True)
            error_responses.append(
                self.generate_error_response(e, self.cloud_service_group, "NodeGroup")
            )

        _LOGGER.info("** GKE Node Pool V1Beta END **")
        return collected_cloud_services, error_responses
