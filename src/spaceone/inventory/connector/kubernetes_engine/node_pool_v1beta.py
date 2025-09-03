import logging
import google.oauth2.service_account
import googleapiclient.discovery

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["GKENodePoolV1BetaConnector"]
_LOGGER = logging.getLogger(__name__)


class GKENodePoolV1BetaConnector(GoogleCloudConnector):
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
        self.secret_data = secret_data  # secret_data를 인스턴스 변수로 저장
        self.credentials = (
            google.oauth2.service_account.Credentials.from_service_account_info(
                secret_data
            )
        )
        self.client = googleapiclient.discovery.build(
            "container", "v1beta1", credentials=self.credentials
        )

    def list_node_pools(self, cluster_name, location, **query):
        """
        GKE 노드풀 목록을 조회합니다 (v1beta1 API).
        """
        # secret_data가 없으면 get_connect 호출
        if not hasattr(self, 'secret_data'):
            _LOGGER.warning("secret_data not found, cannot list node pools")
            return []
            
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

    def get_node_pool(self, cluster_name, location, node_pool_name):
        """
        특정 GKE 노드풀 정보를 조회합니다 (v1beta1 API).
        """
        # secret_data가 없으면 get_connect 호출
        if not hasattr(self, 'secret_data'):
            _LOGGER.warning("secret_data not found, cannot get node pool")
            return None
            
        try:
            request = self.client.projects().locations().clusters().nodePools().get(
                name=f"projects/{self.project_id}/locations/{location}/clusters/{cluster_name}/nodePools/{node_pool_name}"
            )
            return request.execute()
        except Exception as e:
            _LOGGER.error(f"Failed to get GKE node pool {node_pool_name} (v1beta1): {e}")
            return None
