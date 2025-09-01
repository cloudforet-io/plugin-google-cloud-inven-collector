import logging
from typing import Any, Dict, List, Tuple

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

logger = logging.getLogger(__name__)


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
            params: 커넥터에 전달할 파라미터
                - secret_data: Google Cloud 인증 정보
                - options: 추가 옵션

        Returns:
            Dataproc 클러스터 리소스의 리스트

        Raises:
            Exception: 커넥터 초기화 실패 시
        """
        if not params or "secret_data" not in params:
            raise ValueError("secret_data is required in params")

        cluster_connector: DataprocClusterConnector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            clusters = cluster_connector.list_clusters()
            logger.info(
                f"📊 Successfully found {len(clusters)} Dataproc clusters "
                f"(parallel processing enabled)"
            )
            return clusters
        except Exception as e:
            logger.error(f"Failed to list Dataproc clusters: {e}")
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
                logger.info("Retrieved Dataproc cluster successfully")
            return cluster or {}
        except Exception as e:
            logger.error(f"Failed to get Dataproc cluster: {e}")
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
            logger.info(
                f"⚡ Found {len(jobs)} Dataproc jobs "
                f"(parallel processing with optimized timeouts)"
            )
            return jobs
        except Exception as e:
            logger.error(f"Failed to list Dataproc jobs: {e}")
            return []

    def list_workflow_templates(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Dataproc 워크플로 템플릿 목록을 조회합니다.

        Args:
            params (dict): 커넥터에 전달할 파라미터.

        Returns:
            list: Dataproc 워크플로 템플릿 리소스의 리스트.
        """
        cluster_connector: DataprocClusterConnector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            templates = cluster_connector.list_workflow_templates()
            logger.info(f"Found {len(templates)} Dataproc workflow templates")
            return templates
        except Exception as e:
            logger.error(f"Failed to list Dataproc workflow templates: {e}")
            return []

    def list_autoscaling_policies(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Dataproc 오토스케일링 정책 목록을 조회합니다.

        Args:
            params (dict): 커넥터에 전달할 파라미터.

        Returns:
            list: Dataproc 오토스케일링 정책 리소스의 리스트.
        """
        cluster_connector: DataprocClusterConnector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            policies = cluster_connector.list_autoscaling_policies()
            logger.info(f"Found {len(policies)} Dataproc autoscaling policies")
            return policies
        except Exception as e:
            logger.error(f"Failed to list Dataproc autoscaling policies: {e}")
            return []

    def collect_cloud_service(
        self, params: Dict[str, Any]
    ) -> Tuple[List[DataprocClusterResponse], List[Dict[str, Any]]]:
        """
        Dataproc 클러스터 정보를 수집하여 Cloud Service 리소스로 변환합니다.

        Args:
            params: 수집 프로세스를 위한 파라미터
                - secret_data: Google Cloud 인증 정보
                - options: 추가 수집 옵션

        Returns:
            수집된 Cloud Service 응답 리스트와 에러 응답 리스트의 튜플

        Raises:
            ValueError: 필수 파라미터가 누락된 경우
        """
        logger.debug("** Dataproc Cluster START **")

        if not params or "secret_data" not in params:
            raise ValueError("secret_data is required in params")

        collected_cloud_services = []
        error_responses = []

        secret_data = params["secret_data"]
        project_id = secret_data.get("project_id")

        if not project_id:
            raise ValueError("project_id is required in secret_data")

        # Dataproc 클러스터 목록 조회
        try:
            clusters = self.list_clusters(params)
            if not clusters:
                logger.info("No Dataproc clusters found")
                return collected_cloud_services, error_responses
        except Exception as e:
            logger.error(f"Failed to retrieve cluster list: {e}")
            error_responses.append(
                self.generate_error_response(e, self.cloud_service_group, "Cluster")
            )
            return collected_cloud_services, error_responses

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

                # Job 정보 수집 최적화 - 성능 개선을 위해 선택적으로 수집
                cluster_data["jobs"] = []
                # Job 수집은 별도 옵션이 있을 때만 수행 (성능 최적화)
                if params.get("options", {}).get("include_jobs", False):
                    try:
                        # 클러스터 위치에서 리전 추출
                        cluster_region = (
                            location.rsplit("-", 1)[0]
                            if location and "-" in location
                            else location
                        )
                        if cluster_region:
                            jobs = self.list_jobs(
                                region=cluster_region,
                                cluster_name=cluster_name,
                                params=params,
                            )
                            if jobs:
                                # 최근 작업 수집 (성능 최적화를 위해 제한)
                                job_limit = min(5, len(jobs))  # 최대 5개로 축소
                                for job in jobs[:job_limit]:
                                    job_data = {
                                        "reference": job.get("reference", {}),
                                        "placement": job.get("placement", {}),
                                        "status": job.get("status", {}),
                                        "labels": job.get("labels", {}),
                                        "jobUuid": job.get("jobUuid", ""),
                                    }
                                    cluster_data["jobs"].append(job_data)
                    except Exception as e:
                        logger.warning(f"Failed to collect jobs for cluster: {e}")
                        # jobs는 이미 빈 배열로 초기화됨
                else:
                    # Job 수집 생략 - 성능 최적화
                    logger.debug("Job collection skipped for performance optimization")

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
                logger.error(f"[collect_cloud_service] => {e}", exc_info=True)
                error_responses.append(
                    self.generate_error_response(e, self.cloud_service_group, "Cluster")
                )

        logger.debug("** Dataproc Cluster END **")
        return collected_cloud_services, error_responses
