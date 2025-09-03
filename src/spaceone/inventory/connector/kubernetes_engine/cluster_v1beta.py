import logging
import google.oauth2.service_account
import googleapiclient.discovery

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["GKEClusterV1BetaConnector"]
_LOGGER = logging.getLogger(__name__)


class GKEClusterV1BetaConnector(GoogleCloudConnector):
    google_client_service = "container"
    version = "v1beta1"

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
            "container", "v1beta1", credentials=credentials
        )

    def list_clusters(self, **query):
        """
        GKE 클러스터 목록을 조회합니다 (v1beta1 API).
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
            _LOGGER.error(f"Failed to list GKE clusters (v1beta1): {e}")
            
        return cluster_list

    def get_cluster(self, name, location):
        """
        특정 GKE 클러스터 정보를 조회합니다 (v1beta1 API).
        """
        try:
            request = self.client.projects().locations().clusters().get(
                name=f"projects/{self.project_id}/locations/{location}/clusters/{name}"
            )
            return request.execute()
        except Exception as e:
            _LOGGER.error(f"Failed to get GKE cluster {name} (v1beta1): {e}")
            return None

    def list_node_pools(self, cluster_name, location, **query):
        """
        특정 클러스터의 노드풀 목록을 조회합니다 (v1beta1 API).
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
            _LOGGER.error(f"Failed to list node pools for cluster {cluster_name} (v1beta1): {e}")
            
        return node_pool_list

    def list_operations(self, **query):
        """
        GKE 작업 목록을 조회합니다 (v1beta1 API).
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
            _LOGGER.error(f"Failed to list GKE operations (v1beta1): {e}")
            
        return operation_list

    def list_workloads(self, cluster_name, location, **query):
        """
        GKE 워크로드 목록을 조회합니다 (v1beta1 API).
        """
        workload_list = []
        query.update({
            "parent": f"projects/{self.project_id}/locations/{location}/clusters/{cluster_name}"
        })
        
        try:
            # v1beta1에서는 추가적인 워크로드 관련 API가 있을 수 있음
            cluster_info = self.get_cluster(cluster_name, location)
            if cluster_info and "workloadPolicyConfig" in cluster_info:
                workload_list.append(cluster_info["workloadPolicyConfig"])
        except Exception as e:
            _LOGGER.error(f"Failed to list workloads for cluster {cluster_name} (v1beta1): {e}")
            
        return workload_list

    def list_fleets(self, **query):
        """
        GKE Fleet 목록을 조회합니다 (v1beta1 API).
        """
        fleet_list = []
        query.update({"parent": f"projects/{self.project_id}/locations/-"})
        
        try:
            # v1beta1에서 Fleet API 사용 가능한지 확인
            if hasattr(self.client.projects().locations(), 'fleets'):
                request = self.client.projects().locations().fleets().list(**query)
                while request is not None:
                    response = request.execute()
                    if "fleets" in response:
                        fleet_list.extend(response.get("fleets", []))
                    
                    # 페이지네이션 처리 - list_next가 있는지 확인
                    try:
                        request = self.client.projects().locations().fleets().list_next(
                            previous_request=request, previous_response=response
                        )
                    except AttributeError:
                        # list_next가 없는 경우 첫 페이지만 처리
                        break
            else:
                _LOGGER.debug("Fleet API not available in this v1beta1 version")
        except Exception as e:
            _LOGGER.error(f"Failed to list GKE fleets (v1beta1): {e}")
            
        return fleet_list

    def list_memberships(self, **query):
        """
        GKE Membership 목록을 조회합니다 (v1beta1 API).
        """
        membership_list = []
        query.update({"parent": f"projects/{self.project_id}/locations/-"})
        
        try:
            # v1beta1에서 Membership API 사용 가능한지 확인
            if hasattr(self.client.projects().locations(), 'memberships'):
                request = self.client.projects().locations().memberships().list(**query)
                while request is not None:
                    response = request.execute()
                    if "memberships" in response:
                        membership_list.extend(response.get("memberships", []))
                    
                    # 페이지네이션 처리 - list_next가 있는지 확인
                    try:
                        request = self.client.projects().locations().memberships().list_next(
                            previous_request=request, previous_response=response
                        )
                    except AttributeError:
                        # list_next가 없는 경우 첫 페이지만 처리
                        break
            else:
                _LOGGER.debug("Membership API not available in this v1beta1 version")
        except Exception as e:
            _LOGGER.error(f"Failed to list GKE memberships (v1beta1): {e}")
            
        return membership_list
