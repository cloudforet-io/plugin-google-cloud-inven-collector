import logging
from typing import Any, Dict, List, Tuple

from spaceone.inventory.connector.kubernetes_engine.cluster_v1 import (
    GKEClusterV1Connector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.cloud_service import ErrorResourceResponse
from spaceone.inventory.model.kubernetes_engine.cluster.cloud_service import (
    GKEClusterResource,
    GKEClusterResponse,
)
from spaceone.inventory.model.kubernetes_engine.cluster.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.kubernetes_engine.cluster.data import (
    GKECluster,
    convert_datetime,
)

_LOGGER = logging.getLogger(__name__)


class GKEClusterV1Manager(GoogleCloudManager):
    connector_name = "GKEClusterV1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    cloud_service_group = "KubernetesEngine"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_clusters(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """GKE 클러스터 목록을 조회합니다 (v1 API).

        Args:
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            GKE 클러스터 목록.

        Raises:
            Exception: GKE API 호출 중 오류 발생 시.
        """
        cluster_connector: GKEClusterV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            clusters = cluster_connector.list_clusters()
            _LOGGER.info(f"Found {len(clusters)} GKE clusters (v1)")
            return clusters
        except Exception as e:
            _LOGGER.error(f"Failed to list GKE clusters (v1): {e}")
            return []

    # 노드풀 관련 기능은 별도의 NodePoolManager에서 처리
    # def list_node_pools(self, cluster_name: str, location: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
    #     """GKE 노드풀 목록을 조회합니다 (v1 API).
    #
    #     이 메서드는 제거되었습니다. 노드풀 정보는 GKENodePoolManager를 사용하세요.
    #     """
    #     _LOGGER.warning("list_node_pools method is deprecated. Use GKENodePoolManager instead.")
    #     return []

    def get_cluster(
        self, name: str, location: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """특정 GKE 클러스터 정보를 조회합니다 (v1 API).

        Args:
            name: 클러스터 이름.
            location: 클러스터 위치.
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            GKE 클러스터 정보 딕셔너리.

        Raises:
            Exception: GKE API 호출 중 오류 발생 시.
        """
        cluster_connector: GKEClusterV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            cluster = cluster_connector.get_cluster(name, location)
            if cluster:
                _LOGGER.info(f"Retrieved cluster {name} (v1)")
            return cluster or {}
        except Exception as e:
            _LOGGER.error(f"Failed to get cluster {name} (v1): {e}")
            return {}

    def list_operations(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """GKE 작업 목록을 조회합니다 (v1 API).

        Args:
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            GKE 작업 목록.

        Raises:
            Exception: GKE API 호출 중 오류 발생 시.
        """
        cluster_connector: GKEClusterV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            operations = cluster_connector.list_operations()
            _LOGGER.info(f"Found {len(operations)} GKE operations (v1)")
            return operations
        except Exception as e:
            _LOGGER.error(f"Failed to list GKE operations (v1): {e}")
            return []

    def get_resource_limits(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """GKE 리소스 제한 정보를 조회합니다.

        Args:
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            GKE 리소스 제한 목록.

        Raises:
            Exception: GKE API 호출 중 오류 발생 시.
        """
        try:
            cluster_connector: GKEClusterV1Connector = self.locator.get_connector(
                self.connector_name, **params
            )

            # Container Engine 관련 할당량 조회
            resource_limits = cluster_connector.get_container_engine_quotas()
            _LOGGER.info(f"Found {len(resource_limits)} GKE resource limits")
            return resource_limits
        except Exception as e:
            _LOGGER.error(f"Failed to get GKE resource limits: {e}")
            return []

    def collect_cloud_service(
        self, params: Dict[str, Any]
    ) -> Tuple[List[Any], List[ErrorResourceResponse]]:
        """GKE 클러스터 정보를 수집합니다 (v1 API).

        Args:
            params: 수집에 필요한 파라미터 딕셔너리.

        Returns:
            수집된 클라우드 서비스 목록과 오류 응답 목록의 튜플.

        Raises:
            Exception: 데이터 수집 중 오류 발생 시.
        """
        _LOGGER.debug("** GKE Cluster V1 START **")

        collected_cloud_services = []
        error_responses = []

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        # GKE 클러스터 목록 조회
        clusters = self.list_clusters(params)

        # GKE 리소스 제한 정보 조회
        resource_limits = self.get_resource_limits(params)

        for cluster in clusters:
            try:
                # NodePool 정보는 별도의 NodePoolManager에서 처리

                # 기본 클러스터 데이터 준비
                cluster_data = {
                    "name": str(cluster.get("name", "")),
                    "description": str(cluster.get("description", "")),
                    "location": str(cluster.get("location", "")),
                    "projectId": str(
                        project_id
                    ),  # secret_data에서 가져온 project_id 사용
                    "status": str(cluster.get("status", "")),
                    "currentMasterVersion": str(
                        cluster.get("currentMasterVersion", "")
                    ),
                    "currentNodeVersion": str(cluster.get("currentNodeVersion", "")),
                    "currentNodeCount": str(cluster.get("currentNodeCount", "")),
                    "createTime": convert_datetime(cluster.get("createTime")),
                    "resourceLabels": {
                        k: str(v) for k, v in cluster.get("resourceLabels", {}).items()
                    },
                    "api_version": "v1",
                }

                # 네트워크 설정 추가
                if "networkConfig" in cluster:
                    network_config = cluster["networkConfig"]
                    cluster_data.update(
                        {
                            "networkConfig": {
                                "network": str(network_config.get("network", "")),
                                "subnetwork": str(network_config.get("subnetwork", "")),
                                "enableIntraNodeVisibility": str(
                                    network_config.get("enableIntraNodeVisibility", "")
                                ),
                                "enableL4ilbSubsetting": str(
                                    network_config.get("enableL4ilbSubsetting", "")
                                ),
                            },
                            "network": str(network_config.get("network", "")),
                            "subnetwork": str(network_config.get("subnetwork", "")),
                        }
                    )

                # 클러스터 IP 설정 추가
                if "clusterIpv4Cidr" in cluster:
                    cluster_data["clusterIpv4Cidr"] = str(cluster["clusterIpv4Cidr"])
                if "servicesIpv4Cidr" in cluster:
                    cluster_data["servicesIpv4Cidr"] = str(cluster["servicesIpv4Cidr"])

                # 마스터 인증 추가
                if "masterAuth" in cluster:
                    master_auth = cluster["masterAuth"]
                    cluster_data["masterAuth"] = {
                        "username": str(master_auth.get("username", "")),
                        "password": str(master_auth.get("password", "")),
                        "clusterCaCertificate": str(
                            master_auth.get("clusterCaCertificate", "")
                        ),
                    }

                # 워크로드 정책 추가
                if "workloadPolicyConfig" in cluster:
                    workload_policy = cluster["workloadPolicyConfig"]
                    cluster_data["workloadPolicyConfig"] = {
                        "allowNetAdmin": str(workload_policy.get("allowNetAdmin", "")),
                    }

                # 리소스 사용량 내보내기 추가
                if "resourceUsageExportConfig" in cluster:
                    export_config = cluster["resourceUsageExportConfig"]
                    cluster_data["resourceUsageExportConfig"] = {
                        "enableNetworkEgressMetering": str(
                            export_config.get("enableNetworkEgressMetering", "")
                        ),
                    }

                # 인증자 그룹 추가
                if "authenticatorGroupsConfig" in cluster:
                    auth_config = cluster["authenticatorGroupsConfig"]
                    cluster_data["authenticatorGroupsConfig"] = {
                        "securityGroup": str(auth_config.get("securityGroup", "")),
                    }

                # 모니터링 추가
                if "monitoringConfig" in cluster:
                    monitoring_config = cluster["monitoringConfig"]
                    cluster_data["monitoringConfig"] = {
                        "monitoringService": str(
                            monitoring_config.get("monitoringService", "")
                        ),
                        "loggingService": str(
                            monitoring_config.get("loggingService", "")
                        ),
                    }

                # 애드온 추가
                if "addonsConfig" in cluster:
                    addons_config = cluster["addonsConfig"]
                    cluster_data["addonsConfig"] = {
                        "httpLoadBalancing": str(
                            addons_config.get("httpLoadBalancing", {})
                        ),
                        "horizontalPodAutoscaling": str(
                            addons_config.get("horizontalPodAutoscaling", {})
                        ),
                        "kubernetesDashboard": str(
                            addons_config.get("kubernetesDashboard", {})
                        ),
                        "networkPolicyConfig": str(
                            addons_config.get("networkPolicyConfig", {})
                        ),
                    }

                # NodePool 정보는 별도의 NodePoolManager에서 처리

                # ResourceLimit 정보 추가
                if resource_limits:
                    cluster_data["resourceLimits"] = resource_limits
                    _LOGGER.info(
                        f"Added {len(resource_limits)} resource limits to cluster {cluster_data.get('name')}"
                    )

                # Stackdriver 정보 추가
                cluster_name = cluster.get("name")
                cluster_location = cluster.get("location")

                if not cluster_name:
                    _LOGGER.warning(
                        f"Cluster missing name, skipping monitoring setup: {cluster}"
                    )
                    cluster_name = "unknown"

                # Google Cloud Monitoring 리소스 ID: {project_id}:{location}:{cluster_name}
                monitoring_resource_id = (
                    f"{project_id}:{cluster_location or 'unknown'}:{cluster_name}"
                )

                google_cloud_monitoring_filters = [
                    {"key": "resource.labels.cluster_name", "value": cluster_name},
                    {
                        "key": "resource.labels.location",
                        "value": cluster_location or "unknown",
                    },
                ]
                cluster_data["google_cloud_monitoring"] = (
                    self.set_google_cloud_monitoring(
                        project_id,
                        "kubernetes.io/container",
                        monitoring_resource_id,
                        google_cloud_monitoring_filters,
                    )
                )
                cluster_data["google_cloud_logging"] = self.set_google_cloud_logging(
                    "KubernetesEngine", "Cluster", project_id, monitoring_resource_id
                )

                # GKECluster 모델 생성
                gke_cluster_data = GKECluster(cluster_data, strict=False)

                # resourceLabels를 tags 형식으로 변환
                tags = self.convert_labels_format(cluster.get("resourceLabels", {}))

                # GKEClusterResource 생성
                cluster_resource = GKEClusterResource(
                    {
                        "name": cluster_data.get("name"),
                        "data": gke_cluster_data,
                        "reference": {
                            "resource_id": cluster.get("selfLink"),
                            "external_link": f"https://console.cloud.google.com/kubernetes/clusters/details/{cluster.get('location')}/{cluster.get('name')}?project={project_id}",
                        },
                        "region_code": cluster.get("location"),
                        "account": project_id,
                        "tags": tags,
                    }
                )

                ##################################
                # 4. Make Collected Region Code
                ##################################
                self.set_region_code(cluster.get("location"))

                # GKEClusterResponse 생성
                cluster_response = GKEClusterResponse({"resource": cluster_resource})

                collected_cloud_services.append(cluster_response)

            except Exception as e:
                _LOGGER.error(f"[collect_cloud_service] => {e}", exc_info=True)
                error_responses.append(
                    ErrorResourceResponse(
                        {
                            "message": str(e),
                            "resource": {
                                "cloud_service_group": self.cloud_service_group,
                                "cloud_service_type": "Cluster",
                            },
                        }
                    )
                )

        _LOGGER.debug("** GKE Cluster V1 END **")
        return collected_cloud_services, error_responses
