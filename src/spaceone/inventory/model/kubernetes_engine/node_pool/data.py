import logging
import time

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.kubernetes_engine.node_pool.cloud_service import *
from spaceone.inventory.model.kubernetes_engine.node_pool.cloud_service_type import CLOUD_SERVICE_TYPES
from spaceone.inventory.connector.kubernetes_engine_connector import KubernetesEngineConnector
from spaceone.inventory.libs.schema.base import make_error_response

_LOGGER = logging.getLogger(__name__)


class NodePoolManager(GoogleCloudManager):
    connector_name = "KubernetesEngineConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    cloud_service_group = "KubernetesEngine"
    cloud_service_type = "NodePool"
    provider = "google_cloud"

    def collect_cloud_service(self, params):
        _LOGGER.debug(f"** NodePool START **")
        start_time = time.time()
        
        """
        Args:
            params:
                - options
                - schema
                - secret_data
                - filter
                - zones
        Response:
            CloudServiceResponse
        """
        collected_cloud_services = []
        error_responses = []
        
        project_id = params["secret_data"]["project_id"]
        
        ##################################
        # 0. Gather All Related Resources
        # List all related resources through connector
        ##################################
        
        try:
            self.connector: KubernetesEngineConnector = self.locator.get_connector(
                self.connector_name, **params
            )
            
            # Get clusters first to iterate through their node pools
            clusters = self.connector.list_clusters()
            
            for cluster in clusters:
                cluster_name = cluster.get("name", "")
                location = cluster.get("location", "")
                
                # Get node pools for this cluster
                node_pools = self.connector.list_node_pools(cluster_name, location)
                
                for node_pool_vo in node_pools:
                    try:
                        ##################################
                        # 1. Set Basic Information
                        ##################################
                        node_pool_name = node_pool_vo.get("name", "")
                        region_code = self._get_region_from_zone(location)
                        
                        ##################################
                        # 2. Make Base Data
                        ##################################
                        node_pool_data = NodePool(node_pool_vo, strict=False)
                        
                        # Set additional fields
                        node_pool_data.cluster_name = cluster_name
                        node_pool_data.location = location
                        node_pool_data.project_id = project_id
                        node_pool_data.api_version = params.get("api_version", "v1")
                        
                        ##################################
                        # 3. Make Return Resource
                        ##################################
                        node_pool_resource = NodePoolResource({
                            "name": node_pool_name,
                            "account": project_id,
                            "region_code": region_code,
                            "data": node_pool_data,
                            "tags": self._get_tags_from_labels(node_pool_vo.get("config", {}).get("labels", {})),
                            "reference": ReferenceModel(node_pool_data.reference(region_code)),
                        })
                        
                        ##################################
                        # 4. Make Collected Region Code
                        ##################################
                        self.set_region_code(region_code)
                        
                        ##################################
                        # 5. Make Resource Response Object
                        # List of InstanceResponse Object
                        ##################################
                        collected_cloud_services.append(
                            NodePoolResponse({"resource": node_pool_resource})
                        )
                        
                    except Exception as e:
                        _LOGGER.error(f"[collect_cloud_service] => {e}", exc_info=True)
                        error_responses.append(
                            make_error_response(
                                error=e,
                                provider=self.provider,
                                cloud_service_group=self.cloud_service_group,
                                cloud_service_type=self.cloud_service_type,
                            )
                        )
                        
        except Exception as e:
            _LOGGER.error(f"[collect_cloud_service] => {e}", exc_info=True)
            error_responses.append(
                make_error_response(
                    error=e,
                    provider=self.provider,
                    cloud_service_group=self.cloud_service_group,
                    cloud_service_type=self.cloud_service_type,
                )
            )
            
        _LOGGER.debug(f"** NodePool Finished {time.time() - start_time} Seconds **")
        return collected_cloud_services, error_responses

    def _get_region_from_zone(self, location):
        """Zone 또는 Region에서 Region 코드를 추출합니다."""
        if not location:
            return "global"
        
        # Zone 형태인 경우 (예: us-central1-a)
        if location.count('-') >= 2:
            parts = location.split('-')
            return f"{parts[0]}-{parts[1]}"
        
        # 이미 Region 형태인 경우 (예: us-central1)
        return location

    def _get_tags_from_labels(self, labels):
        """GCP Labels를 SpaceONE Tags 형식으로 변환합니다."""
        if not labels:
            return {}
        
        tags = {}
        for key, value in labels.items():
            tags[key] = str(value)
        
        return tags
