import logging
import google.oauth2.service_account
import googleapiclient.discovery

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["GKENodePoolV1Connector"]
_LOGGER = logging.getLogger(__name__)


class GKENodePoolV1Connector(GoogleCloudConnector):
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

    def list_node_pools(self, cluster_name, location, **query):
        """
        GKE 노드풀 목록을 조회합니다 (v1 API).
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
            _LOGGER.error(f"Failed to list node pools for cluster {cluster_name} (v1): {e}")
            
        return node_pool_list

    def get_node_pool(self, cluster_name, location, node_pool_name):
        """
        특정 GKE 노드풀 정보를 조회합니다 (v1 API).
        """
        try:
            request = self.client.projects().locations().clusters().nodePools().get(
                name=f"projects/{self.project_id}/locations/{location}/clusters/{cluster_name}/nodePools/{node_pool_name}"
            )
            return request.execute()
        except Exception as e:
            _LOGGER.error(f"Failed to get GKE node pool {node_pool_name} (v1): {e}")
            return None

    def list_nodes(self, cluster_name, location, node_pool_name, **query):
        """
        GKE 노드 목록을 조회합니다 (v1 API).
        """
        node_list = []
        query.update({
            "parent": f"projects/{self.project_id}/locations/{location}/clusters/{cluster_name}/nodePools/{node_pool_name}"
        })
        
        try:
            request = self.client.projects().locations().clusters().nodePools().nodes().list(**query)
            while request is not None:
                response = request.execute()
                if "nodes" in response:
                    node_list.extend(response.get("nodes", []))
                
                # 페이지네이션 처리 - list_next가 있는지 확인
                try:
                    request = self.client.projects().locations().clusters().nodePools().nodes().list_next(
                        previous_request=request, previous_response=response
                    )
                except AttributeError:
                    # list_next가 없는 경우 첫 페이지만 처리
                    break
        except Exception as e:
            _LOGGER.error(f"Failed to list nodes for node pool {node_pool_name} (v1): {e}")
            
        return node_list

    def get_node(self, cluster_name, location, node_pool_name, node_name):
        """
        특정 GKE 노드 정보를 조회합니다 (v1 API).
        """
        try:
            request = self.client.projects().locations().clusters().nodePools().nodes().get(
                name=f"projects/{self.project_id}/locations/{location}/clusters/{cluster_name}/nodePools/{node_pool_name}/nodes/{node_name}"
            )
            return request.execute()
        except Exception as e:
            _LOGGER.error(f"Failed to get GKE node {node_name} (v1): {e}")
            return None
