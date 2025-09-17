import logging
import google.oauth2.service_account
import googleapiclient.discovery

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["GKEClusterV1Connector"]
_LOGGER = logging.getLogger(__name__)


class GKEClusterV1Connector(GoogleCloudConnector):
    google_client_service = "container"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def verify(self, options, secret_data):
        self.get_connect(secret_data)
        return "ACTIVE"

    def get_connect(self, secret_data):
        """
        cred(dict)
            - type: ..
            - project_id: ...
            - token_uri: ...
            - ...
        """
        self.project_id = secret_data.get("project_id")
        credentials = (
            google.oauth2.service_account.Credentials.from_service_account_info(
                secret_data
            )
        )
        self.client = googleapiclient.discovery.build(
            "container", "v1", credentials=credentials
        )

    def list_clusters(self, **query):
        """
        GKE 클러스터 목록을 조회합니다 (v1 API).
        """
        cluster_list = []
        query.update({"parent": f"projects/{self.project_id}/locations/-"})
        
        try:
            request = self.client.projects().locations().clusters().list(**query)
            while request is not None:
                response = request.execute()
                if "clusters" in response:
                    cluster_list.extend(response.get("clusters", []))
                
                # 페이지네이션 처리 - list_next가 있는지 확인
                try:
                    request = self.client.projects().locations().clusters().list_next(
                        previous_request=request, previous_response=response
                    )
                except AttributeError:
                    # list_next가 없는 경우 첫 페이지만 처리
                    break
        except Exception as e:
            _LOGGER.warning(f"Failed to list GKE clusters (v1): {e}")
            
        return cluster_list

    def get_cluster(self, name, location):
        """
        특정 GKE 클러스터 정보를 조회합니다 (v1 API).
        """
        try:
            request = self.client.projects().locations().clusters().get(
                name=f"projects/{self.project_id}/locations/{location}/clusters/{name}"
            )
            return request.execute()
        except Exception as e:
            _LOGGER.warning(f"Failed to get GKE cluster {name} (v1): {e}")
            return None

    def list_node_pools(self, cluster_name, location, **query):
        """
        특정 클러스터의 노드풀 목록을 조회합니다 (v1 API).
        """
        node_pool_list = []
        query.update({
            "parent": f"projects/{self.project_id}/locations/{location}/clusters/{cluster_name}"
        })
        
        try:
            request = self.client.projects().locations().clusters().nodePools().list(**query)
            while request is not None:
                response = request.execute()
                if "nodePools" in response:
                    node_pool_list.extend(response.get("nodePools", []))
                
                # 페이지네이션 처리 - list_next가 있는지 확인
                try:
                    request = self.client.projects().locations().clusters().nodePools().list_next(
                        previous_request=request, previous_response=response
                    )
                except AttributeError:
                    # list_next가 없는 경우 첫 페이지만 처리
                    break
        except Exception as e:
            _LOGGER.warning(f"Failed to list node pools for cluster {cluster_name} (v1): {e}")
            
        return node_pool_list

    def list_operations(self, **query):
        """
        GKE 작업 목록을 조회합니다 (v1 API).
        """
        operation_list = []
        query.update({"parent": f"projects/{self.project_id}/locations/-"})
        
        try:
            request = self.client.projects().locations().operations().list(**query)
            while request is not None:
                response = request.execute()
                if "operations" in response:
                    operation_list.extend(response.get("operations", []))
                
                # 페이지네이션 처리 - list_next가 있는지 확인
                try:
                    request = self.client.projects().locations().operations().list_next(
                        previous_request=request, previous_response=response
                    )
                except AttributeError:
                    # list_next가 없는 경우 첫 페이지만 처리
                    break
        except Exception as e:
            _LOGGER.warning(f"Failed to list GKE operations (v1): {e}")
            
        return operation_list

    def list_workloads(self, cluster_name, location, **query):
        """
        GKE 워크로드 목록을 조회합니다 (v1 API).
        """
        workload_list = []
        query.update({
            "parent": f"projects/{self.project_id}/locations/{location}/clusters/{cluster_name}"
        })
        
        try:
            # GKE v1에서는 워크로드 정보를 직접 조회할 수 없으므로
            # 클러스터 정보에서 워크로드 관련 설정을 추출
            cluster_info = self.get_cluster(cluster_name, location)
            if cluster_info and "workloadPolicyConfig" in cluster_info:
                workload_list.append(cluster_info["workloadPolicyConfig"])
        except Exception as e:
            _LOGGER.warning(f"Failed to list workloads for cluster {cluster_name} (v1): {e}")
            
        return workload_list

    def get_container_engine_quotas(self):
        """
        Container Engine (GKE) 관련 할당량 정보를 조회합니다.
        """
        container_engine_quotas = []
        
        try:
            # Service Usage API 클라이언트 생성
            service_usage_client = googleapiclient.discovery.build(
                "serviceusage", "v1", credentials=self.credentials
            )
            
            # Container Engine API 서비스 확인
            service_name = "container.googleapis.com"
            service_info = self.get_service(service_name, service_usage_client)
            
            if service_info and service_info.get("state") == "ENABLED":
                _LOGGER.info("Container Engine service is enabled")
                
                # Container Engine 관련 할당량 제한 조회
                quota_limits = self.list_quota_limits(service_name, service_usage_client)
                
                for quota_limit in quota_limits:
                    quota_info = {
                        "service_name": service_name,
                        "quota_limit_name": quota_limit.get("name", ""),
                        "metric": quota_limit.get("metric", ""),
                        "unit": quota_limit.get("unit", ""),
                        "values": quota_limit.get("values", {}),
                        "display_name": quota_limit.get("displayName", ""),
                        "description": quota_limit.get("description", ""),
                    }
                    container_engine_quotas.append(quota_info)
                
                _LOGGER.info(f"Found {len(container_engine_quotas)} Container Engine quota limits")
            else:
                _LOGGER.warning("Container Engine service is not enabled")
                
        except Exception as e:
            _LOGGER.error(f"Failed to get Container Engine quotas: {e}")
            
        return container_engine_quotas

    def get_service(self, service_name, service_usage_client):
        """
        특정 서비스 정보를 조회합니다.
        """
        try:
            request = service_usage_client.services().get(
                name=f"projects/{self.project_id}/services/{service_name}"
            )
            return request.execute()
        except Exception as e:
            _LOGGER.warning(f"Failed to get service {service_name}: {e}")
            return None

    def list_quota_limits(self, service_name, service_usage_client, **query):
        """
        특정 서비스의 할당량 제한을 조회합니다.
        """
        quota_list = []
        query.update({
            "parent": f"projects/{self.project_id}/services/{service_name}"
        })
        
        try:
            # Service Usage API의 quotaLimits 리소스 접근 시도
            services_resource = service_usage_client.services()
            
            # quotaLimits 속성이 존재하는지 확인
            if not hasattr(services_resource, 'quotaLimits'):
                _LOGGER.warning(f"quotaLimits resource not available for service {service_name}")
                return quota_list
            
            request = services_resource.quotaLimits().list(**query)
            while request is not None:
                response = request.execute()
                if "quotaLimits" in response:
                    quota_list.extend(response.get("quotaLimits", []))
                
                # 페이지네이션 처리
                try:
                    request = services_resource.quotaLimits().list_next(
                        previous_request=request, previous_response=response
                    )
                except AttributeError:
                    break
        except AttributeError as e:
            _LOGGER.warning(f"quotaLimits resource not available for service {service_name}: {e}")
        except Exception as e:
            _LOGGER.warning(f"Failed to list quota limits for service {service_name}: {e}")
            
        return quota_list
