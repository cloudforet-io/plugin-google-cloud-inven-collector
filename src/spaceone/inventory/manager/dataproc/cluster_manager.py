import logging
from typing import Any, Dict, List

from spaceone.inventory.connector.dataproc.cluster_connector import (
    DataprocClusterConnector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.model.dataproc.cluster.cloud_service import (
    DataprocClusterResource,
    DataprocClusterResponse,
)
from spaceone.inventory.model.dataproc.cluster.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.dataproc.cluster.data import (
    DataprocCluster,
)

_LOGGER = logging.getLogger(__name__)


class DataprocClusterManager(GoogleCloudManager):
    connector_name = "DataprocClusterConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    cloud_service_group = "Dataproc"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_clusters(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Dataproc 클러스터 목록을 조회합니다.

        Args:
            params (dict): 커넥터에 전달할 파라미터.

        Returns:
            list: Dataproc 클러스터 리소스의 리스트.
        """
        cluster_connector: DataprocClusterConnector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            clusters = cluster_connector.list_clusters()
            _LOGGER.info(f"Found {len(clusters)} Dataproc clusters")
            return clusters
        except Exception as e:
            _LOGGER.error(f"Failed to list Dataproc clusters: {e}")
            return []

    def get_cluster(
        self, cluster_name: str, region: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        특정 Dataproc 클러스터 정보를 조회합니다.

        Args:
            cluster_name (str): 클러스터의 이름.
            region (str): 클러스터가 위치한 리전.
            params (dict): 커넥터에 전달할 파라미터.

        Returns:
            dict: 발견된 경우 클러스터 리소스, 그렇지 않으면 빈 딕셔너리.
        """
        cluster_connector: DataprocClusterConnector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            cluster = cluster_connector.get_cluster(cluster_name, region)
            if cluster:
                _LOGGER.info(f"Retrieved Dataproc cluster {cluster_name}")
            return cluster or {}
        except Exception as e:
            _LOGGER.error(f"Failed to get Dataproc cluster {cluster_name}: {e}")
            return {}

    def list_jobs(
        self,
        region: str = None,
        cluster_name: str = None,
        params: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        Dataproc 작업 목록을 조회합니다.

        Args:
            region (str, optional): 작업을 필터링할 리전.
            cluster_name (str, optional): 작업을 필터링할 클러스터의 이름.
            params (dict, optional): 커넥터에 전달할 파라미터.

        Returns:
            list: Dataproc 작업 리소스의 리스트.
        """
        if params is None:
            params = {}

        cluster_connector: DataprocClusterConnector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            jobs = cluster_connector.list_jobs(region=region, cluster_name=cluster_name)
            _LOGGER.info(f"Found {len(jobs)} Dataproc jobs")
            return jobs
        except Exception as e:
            _LOGGER.error(f"Failed to list Dataproc jobs: {e}")
            return []

    def collect_cloud_service(self, params):
        """
        Dataproc 클러스터 정보를 수집하여 Cloud Service 리소스로 변환합니다.

        Args:
            params (dict): 수집 프로세스를 위한 파라미터.

        Returns:
            tuple: 수집된 Cloud Service 응답 리스트와 에러 응답 리스트를 담은 튜플.
        """
        _LOGGER.debug("** Dataproc Cluster START **")

        collected_cloud_services = []
        error_responses = []

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        # Dataproc 클러스터 목록 조회
        clusters = self.list_clusters(params)

        for cluster in clusters:
            try:
                # 클러스터 위치 정보 추출
                location = ""
                if "placement" in cluster and "zoneUri" in cluster["placement"]:
                    zone_uri = cluster["placement"]["zoneUri"]
                    location = zone_uri.split("/")[-1] if zone_uri else ""
                elif "config" in cluster and "gceClusterConfig" in cluster["config"]:
                    # zone 정보가 있으면 해당 지역을 추출
                    zone_uri = cluster["config"]["gceClusterConfig"].get("zoneUri", "")
                    if zone_uri:
                        location = zone_uri.split("/")[-1]

                # 클러스터명 추출
                cluster_name = cluster.get("clusterName", "")

                # 기본 클러스터 데이터 준비
                cluster_data = {
                    "clusterName": str(cluster.get("clusterName", "")),
                    "projectId": str(cluster.get("projectId", project_id)),
                    "clusterUuid": str(cluster.get("clusterUuid", "")),
                    "status": cluster.get("status", {}),
                    "labels": {k: str(v) for k, v in cluster.get("labels", {}).items()},
                    "location": location,
                }

                # 설정 정보 추가
                if "config" in cluster:
                    config = cluster["config"]
                    cluster_data["config"] = {
                        "configBucket": str(config.get("configBucket", "")),
                        "tempBucket": str(config.get("tempBucket", "")),
                    }

                    # GCE 클러스터 설정
                    if "gceClusterConfig" in config:
                        gce_config = config["gceClusterConfig"]
                        cluster_data["config"]["gceClusterConfig"] = {
                            "zoneUri": str(gce_config.get("zoneUri", "")),
                            "networkUri": str(gce_config.get("networkUri", "")),
                            "subnetworkUri": str(gce_config.get("subnetworkUri", "")),
                            "internalIpOnly": str(gce_config.get("internalIpOnly", "")),
                            "serviceAccount": str(gce_config.get("serviceAccount", "")),
                            "serviceAccountScopes": gce_config.get(
                                "serviceAccountScopes", []
                            ),
                        }

                    # 인스턴스 그룹 설정
                    if "instanceGroupConfig" in config:
                        instance_config = config["instanceGroupConfig"]
                        cluster_data["config"]["instanceGroupConfig"] = {
                            "numInstances": str(
                                instance_config.get("numInstances", "")
                            ),
                            "instanceNames": instance_config.get("instanceNames", []),
                            "imageUri": str(instance_config.get("imageUri", "")),
                            "machineTypeUri": str(
                                instance_config.get("machineTypeUri", "")
                            ),
                            "diskConfig": instance_config.get("diskConfig", {}),
                        }

                    # 마스터 설정
                    if "masterConfig" in config:
                        master_config = config["masterConfig"]
                        cluster_data["config"]["masterConfig"] = {
                            "numInstances": str(master_config.get("numInstances", "")),
                            "instanceNames": master_config.get("instanceNames", []),
                            "imageUri": str(master_config.get("imageUri", "")),
                            "machineTypeUri": str(
                                master_config.get("machineTypeUri", "")
                            ),
                            "diskConfig": master_config.get("diskConfig", {}),
                        }

                    # 워커 설정
                    if "workerConfig" in config:
                        worker_config = config["workerConfig"]
                        cluster_data["config"]["workerConfig"] = {
                            "numInstances": str(worker_config.get("numInstances", "")),
                            "instanceNames": worker_config.get("instanceNames", []),
                            "imageUri": str(worker_config.get("imageUri", "")),
                            "machineTypeUri": str(
                                worker_config.get("machineTypeUri", "")
                            ),
                            "diskConfig": worker_config.get("diskConfig", {}),
                        }

                    # 소프트웨어 설정
                    if "softwareConfig" in config:
                        software_config = config["softwareConfig"]
                        cluster_data["config"]["softwareConfig"] = {
                            "imageVersion": str(
                                software_config.get("imageVersion", "")
                            ),
                            "properties": software_config.get("properties", {}),
                            "optionalComponents": software_config.get(
                                "optionalComponents", []
                            ),
                        }

                # 메트릭 정보 추가
                if "metrics" in cluster:
                    cluster_data["metrics"] = cluster["metrics"]

                # DataprocCluster 모델 생성
                dataproc_cluster_data = DataprocCluster(cluster_data, strict=False)

                # DataprocClusterResource 생성
                cluster_resource = DataprocClusterResource(
                    {
                        "name": cluster_data.get("clusterName"),
                        "data": dataproc_cluster_data,
                        "reference": {
                            "resource_id": cluster.get("clusterUuid"),
                            "external_link": f"https://console.cloud.google.com/dataproc/clusters/details/{location}/{cluster_name}?project={project_id}",
                        },
                        "region_code": location,
                        "account": project_id,
                    }
                )

                ##################################
                # 4. Make Collected Region Code
                ##################################
                self.set_region_code(location)

                # DataprocClusterResponse 생성
                cluster_response = DataprocClusterResponse(
                    {"resource": cluster_resource}
                )

                collected_cloud_services.append(cluster_response)

            except Exception as e:
                _LOGGER.error(f"[collect_cloud_service] => {e}", exc_info=True)
                error_responses.append(
                    self.generate_error_response(e, self.cloud_service_group, "Cluster")
                )

        _LOGGER.debug("** Dataproc Cluster END **")
        return collected_cloud_services, error_responses
