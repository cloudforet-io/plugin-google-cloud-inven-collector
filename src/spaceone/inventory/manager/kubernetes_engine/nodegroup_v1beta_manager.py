"""KubernetesEngine Node Group Manager (v1beta1 API)."""

import logging
from typing import List, Dict, Any, Tuple

from spaceone.inventory.connector.kubernetes_engine.cluster_v1beta import (
    GKEClusterV1BetaConnector,
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


class GKENodeGroupV1BetaManager(GoogleCloudManager):
    """GKE Node Group Manager (v1beta1 API)."""

    connector_name = "GKEClusterV1BetaConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    cloud_service_group = "KubernetesEngine"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_node_groups(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """GKE 노드 그룹 목록을 조회합니다 (v1beta1 API).

        Args:
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            GKE 노드 그룹 목록.

        Raises:
            Exception: GKE API 호출 중 오류 발생 시.
        """
        cluster_connector: GKEClusterV1BetaConnector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            # 모든 클러스터를 조회하여 각 클러스터의 노드풀을 수집
            clusters = cluster_connector.list_clusters()
            all_node_groups = []

            for cluster in clusters:
                cluster_name = cluster.get("name")
                location = cluster.get("location")
                
                if cluster_name and location:
                    try:
                        node_pools = cluster_connector.list_node_pools(
                            cluster_name, location
                        )
                        for node_pool in node_pools:
                            # 클러스터 정보를 노드풀에 추가
                            node_pool["clusterName"] = cluster_name
                            node_pool["clusterLocation"] = location
                            node_pool["projectId"] = cluster.get("projectId")
                            all_node_groups.append(node_pool)
                    except Exception as e:
                        _LOGGER.warning(
                            f"Failed to get node pools for cluster {cluster_name}: {e}"
                        )

            _LOGGER.info(f"Found {len(all_node_groups)} GKE node groups (v1beta1)")
            return all_node_groups
        except Exception as e:
            _LOGGER.error(f"Failed to list GKE node groups (v1beta1): {e}")
            return []

    def get_node_group(
        self, cluster_name: str, location: str, node_pool_name: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """특정 GKE 노드 그룹 정보를 조회합니다 (v1beta1 API).

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
        cluster_connector: GKEClusterV1BetaConnector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            node_pools = cluster_connector.list_node_pools(cluster_name, location)
            for node_pool in node_pools:
                if node_pool.get("name") == node_pool_name:
                    node_pool["clusterName"] = cluster_name
                    node_pool["clusterLocation"] = location
                    _LOGGER.info(f"Retrieved node group {node_pool_name} (v1beta1)")
                    return node_pool
            return {}
        except Exception as e:
            _LOGGER.error(f"Failed to get node group {node_pool_name} (v1beta1): {e}")
            return {}

    def list_node_group_operations(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """GKE 노드 그룹 작업 목록을 조회합니다 (v1beta1 API).

        Args:
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            GKE 노드 그룹 작업 목록.

        Raises:
            Exception: GKE API 호출 중 오류 발생 시.
        """
        cluster_connector: GKEClusterV1BetaConnector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            operations = cluster_connector.list_operations()
            # 노드 그룹 관련 작업만 필터링
            node_group_operations = [
                op for op in operations 
                if op.get("operationType") and "nodepool" in op.get("operationType", "").lower()
            ]
            _LOGGER.info(f"Found {len(node_group_operations)} GKE node group operations (v1beta1)")
            return node_group_operations
        except Exception as e:
            _LOGGER.error(f"Failed to list GKE node group operations (v1beta1): {e}")
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
        cluster_connector: GKEClusterV1BetaConnector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
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
        cluster_connector: GKEClusterV1BetaConnector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            memberships = cluster_connector.list_memberships()
            _LOGGER.info(f"Found {len(memberships)} GKE memberships (v1beta1)")
            return memberships
        except Exception as e:
            _LOGGER.error(f"Failed to list GKE memberships (v1beta1): {e}")
            return []

    def get_node_group_metrics(
        self, cluster_name: str, location: str, node_pool_name: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """GKE 노드 그룹 메트릭을 조회합니다 (v1beta1 API).

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
        # TODO: 실제 메트릭 API 구현
        try:
            # 임시 메트릭 데이터 반환
            metrics = {
                "cpu_usage": "0.0",
                "memory_usage": "0.0",
                "disk_usage": "0.0",
                "node_count": "0",
            }
            _LOGGER.info(f"Retrieved metrics for node group {node_pool_name} (v1beta1)")
            return metrics
        except Exception as e:
            _LOGGER.error(f"Failed to get metrics for node group {node_pool_name} (v1beta1): {e}")
            return {}

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
        _LOGGER.debug("** GKE Node Group V1Beta START **")

        collected_cloud_services = []
        error_responses = []

        # secret_data = params["secret_data"]  # 향후 사용 예정

        # GKE 노드 그룹 목록 조회
        node_groups = self.list_node_groups(params)

        for node_group in node_groups:
            try:
                cluster_name = node_group.get("clusterName")
                location = node_group.get("clusterLocation")
                node_pool_name = node_group.get("name")
                project_id = node_group.get("projectId")

                if not all([cluster_name, location, node_pool_name, project_id]):
                    continue

                # 메트릭 정보 조회
                metrics = self.get_node_group_metrics(
                    cluster_name, location, node_pool_name, params
                )

                # Fleet 및 Membership 정보 조회 (v1beta1 전용)
                fleet_info = None
                membership_info = None

                try:
                    fleets = self.list_fleets(params)
                    if fleets:
                        fleet_info = fleets[0]  # 첫 번째 fleet 정보 사용
                except Exception as e:
                    _LOGGER.debug(f"Failed to get fleet info: {e}")

                try:
                    memberships = self.list_memberships(params)
                    if memberships:
                        membership_info = memberships[0]  # 첫 번째 membership 정보 사용
                except Exception as e:
                    _LOGGER.debug(f"Failed to get membership info: {e}")

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

                # v1beta1 전용 정보 추가
                if fleet_info:
                    node_group_data["fleetInfo"] = {
                        "name": str(fleet_info.get("name", "")),
                        "displayName": str(fleet_info.get("displayName", "")),
                        "state": str(fleet_info.get("state", {})),
                    }

                if membership_info:
                    node_group_data["membershipInfo"] = {
                        "name": str(membership_info.get("name", "")),
                        "endpoint": membership_info.get("endpoint", {}),
                        "state": str(membership_info.get("state", {})),
                    }

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

            except Exception as e:
                _LOGGER.error(f"[collect_cloud_service] => {e}", exc_info=True)
                error_responses.append(
                    self.generate_error_response(e, self.cloud_service_group, "NodeGroup")
                )

        _LOGGER.debug("** GKE Node Group V1Beta END **")
        return collected_cloud_services, error_responses
