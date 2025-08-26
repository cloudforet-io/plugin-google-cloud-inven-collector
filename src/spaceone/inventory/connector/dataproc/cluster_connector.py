import logging

import google.oauth2.service_account
import googleapiclient.discovery

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["DataprocClusterConnector"]
_LOGGER = logging.getLogger(__name__)


class DataprocClusterConnector(GoogleCloudConnector):
    google_client_service = "dataproc"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def verify(self, options, secret_data):
        self.get_connect(secret_data)
        return "ACTIVE"

    def get_connect(self, secret_data):
        """
        Google Cloud Dataproc에 연결을 초기화합니다.

        Args:
            secret_data (dict): Google Cloud 인증을 위한 크리덴셜.
                                - project_id: Google Cloud 프로젝트 ID.
                                - google.oauth2.service_account에 필요한 기타 크리덴셜.

        Returns:
            None
        """
        self.project_id = secret_data.get("project_id")
        credentials = (
            google.oauth2.service_account.Credentials.from_service_account_info(
                secret_data
            )
        )
        self.client = googleapiclient.discovery.build(
            "dataproc", "v1", credentials=credentials
        )

    def list_clusters(self, region=None, **query):
        """
        Dataproc 클러스터 목록을 조회합니다.

        Args:
            region (str, optional): 클러스터를 필터링할 리전. None일 경우 모든 리전에서 검색합니다.
            **query: API에 전달할 추가 쿼리 파라미터.

        Returns:
            list: 클러스터 리소스의 리스트.
        """
        cluster_list = []

        if region:
            # 특정 리전의 클러스터 조회
            try:
                request = (
                    self.client.projects()
                    .regions()
                    .clusters()
                    .list(projectId=self.project_id, region=region, **query)
                )
                response = request.execute()
                if "clusters" in response:
                    cluster_list.extend(response.get("clusters", []))
            except Exception as e:
                _LOGGER.error(
                    f"Failed to list Dataproc clusters in region {region}: {e}"
                )
        else:
            # 모든 리전의 클러스터 조회
            regions = self._get_available_regions()
            for region_name in regions:
                try:
                    request = (
                        self.client.projects()
                        .regions()
                        .clusters()
                        .list(projectId=self.project_id, region=region_name, **query)
                    )
                    response = request.execute()
                    if "clusters" in response:
                        cluster_list.extend(response.get("clusters", []))
                except Exception as e:
                    _LOGGER.debug(f"No Dataproc clusters in region {region_name}: {e}")
                    continue

        return cluster_list

    def get_cluster(self, cluster_name, region):
        """
        특정 Dataproc 클러스터 정보를 조회합니다.

        Args:
            cluster_name (str): 클러스터의 이름.
            region (str): 클러스터가 위치한 리전.

        Returns:
            dict or None: 발견된 경우 클러스터 리소스, 그렇지 않으면 None.
        """
        try:
            request = (
                self.client.projects()
                .regions()
                .clusters()
                .get(projectId=self.project_id, region=region, clusterName=cluster_name)
            )
            return request.execute()
        except Exception as e:
            _LOGGER.error(
                f"Failed to get Dataproc cluster {cluster_name} in region {region}: {e}"
            )
            return None

    def list_jobs(self, region=None, cluster_name=None, **query):
        """
        Dataproc 작업 목록을 조회합니다.

        Args:
            region (str, optional): 작업을 필터링할 리전. None일 경우 모든 리전에서 검색합니다.
            cluster_name (str, optional): 작업을 필터링할 클러스터의 이름.
            **query: API에 전달할 추가 쿼리 파라미터.

        Returns:
            list: 작업 리소스의 리스트.
        """
        job_list = []

        # 클러스터 필터링
        if cluster_name:
            query["clusterName"] = cluster_name

        if region:
            try:
                request = (
                    self.client.projects()
                    .regions()
                    .jobs()
                    .list(projectId=self.project_id, region=region, **query)
                )
                response = request.execute()
                if "jobs" in response:
                    job_list.extend(response.get("jobs", []))
            except Exception as e:
                _LOGGER.error(f"Failed to list Dataproc jobs in region {region}: {e}")
        else:
            # 모든 리전의 작업 조회
            regions = self._get_available_regions()
            for region_name in regions:
                try:
                    request = (
                        self.client.projects()
                        .regions()
                        .jobs()
                        .list(projectId=self.project_id, region=region_name, **query)
                    )
                    response = request.execute()
                    if "jobs" in response:
                        job_list.extend(response.get("jobs", []))
                except Exception as e:
                    _LOGGER.debug(f"No Dataproc jobs in region {region_name}: {e}")
                    continue

        return job_list

    def _get_available_regions(self):
        """
        사용 가능한 Dataproc 리전 목록을 반환합니다.

        Returns:
            list: Dataproc을 사용할 수 있는 Google Cloud 리전의 정적 리스트.
        """
        return [
            "asia-east1",
            "asia-east2",
            "asia-northeast1",
            "asia-northeast2",
            "asia-northeast3",
            "asia-south1",
            "asia-south2",
            "asia-southeast1",
            "asia-southeast2",
            "australia-southeast1",
            "australia-southeast2",
            "europe-north1",
            "europe-west1",
            "europe-west2",
            "europe-west3",
            "europe-west4",
            "europe-west6",
            "europe-central2",
            "northamerica-northeast1",
            "northamerica-northeast2",
            "southamerica-east1",
            "southamerica-west1",
            "us-central1",
            "us-east1",
            "us-east4",
            "us-west1",
            "us-west2",
            "us-west3",
            "us-west4",
        ]
