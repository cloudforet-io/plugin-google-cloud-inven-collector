import logging
import time

from spaceone.inventory.connector.cloud_run.cloud_run_v1 import CloudRunV1Connector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.cloud_run.domain_mapping.cloud_service import (
    DomainMappingResource,
    DomainMappingResponse,
)
from spaceone.inventory.model.cloud_run.domain_mapping.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_run.domain_mapping.data import DomainMapping

_LOGGER = logging.getLogger(__name__)


class CloudRunDomainMappingManager(GoogleCloudManager):
    connector_name = "CloudRunV1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "CloudRun"
        self.cloud_service_type = "DomainMapping"
        self.cloud_run_v1_connector = None
        self.cloud_run_v2_connector = None

    def collect_cloud_service(self, params):
        """
        Args:
            params:
                - options
                - schema
                - secret_data
                - filter
                - zones
        Response:
            CloudServiceResponse/ErrorResourceResponse
        """
        _LOGGER.debug(
            f"** [{self.cloud_service_group}] {self.cloud_service_type} START **"
        )

        start_time = time.time()

        collected_cloud_services = []
        error_responses = []

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]
        
        self.cloud_run_v1_connector = CloudRunV1Connector(**params)

        # Cloud Run Domain Mappings 조회 (전역 리소스)
        try:                
            # Cloud Run Domain Mappings 조회
            domain_mappings = self.cloud_run_v1_connector.list_domain_mappings(f"namespaces/{project_id}")
            if domain_mappings:
                _LOGGER.debug(f"Found {len(domain_mappings)} domain mappings")
                for domain_mapping in domain_mappings:
                    try:
                        cloud_service = self._make_cloud_run_domain_mapping_info(domain_mapping, project_id, "global")
                        collected_cloud_services.append(DomainMappingResponse({"resource": cloud_service}))
                    except Exception as e:
                        _LOGGER.error(f"Failed to process domain mapping {domain_mapping.get('name', 'unknown')}: {str(e)}")
                        error_response = self.generate_resource_error_response(e, self.cloud_service_group, "DomainMapping", domain_mapping.get('name', 'unknown'))
                        error_responses.append(error_response)
                    
        except Exception as e:
            _LOGGER.error(f"Failed to query domain mappings: {str(e)}")

        _LOGGER.debug(
            f"** [{self.cloud_service_group}] {self.cloud_service_type} END ** "
            f"({time.time() - start_time:.2f}s)"
        )

        return collected_cloud_services, error_responses

    def _make_cloud_run_domain_mapping_info(self, domain_mapping: dict, project_id: str, location_id: str) -> DomainMappingResource:
        """Cloud Run Domain Mapping 정보를 생성합니다."""
        domain_mapping_name = domain_mapping.get("metadata", {}).get("name", "")
        
        if "/" in domain_mapping_name:
            domain_mapping_short_name = domain_mapping_name.split("/")[-1]
        else:
            domain_mapping_short_name = domain_mapping_name
        
        formatted_domain_mapping_data = {
            "apiVersion": domain_mapping.get("apiVersion"),
            "kind": domain_mapping.get("kind"),
            "metadata": {
                "name": domain_mapping.get("metadata", {}).get("name"),
                "namespace": domain_mapping.get("metadata", {}).get("namespace"),
                "uid": domain_mapping.get("metadata", {}).get("uid"),
                "creationTimestamp": domain_mapping.get("metadata", {}).get("creationTimestamp"),
                "clusterName": domain_mapping.get("metadata", {}).get("clusterName"),
            },
            "spec": {
                "routeName": domain_mapping.get("spec", {}).get("routeName"),
                "certificateMode": domain_mapping.get("spec", {}).get("certificateMode"),
            },
            "status": {
                "conditions":{
                    "type": domain_mapping.get("status", {}).get("conditions", {}).get("type"),
                    "status": domain_mapping.get("status", {}).get("conditions", {}).get("status"),
                    "reason": domain_mapping.get("status", {}).get("conditions", {}).get("reason"),
                    "message": domain_mapping.get("status", {}).get("conditions", {}).get("message"),
                    "lastTransitionTime": domain_mapping.get("status", {}).get("conditions", {}).get("lastTransitionTime"),
                },
                "observedGeneration": domain_mapping.get("status", {}).get("observedGeneration"),
                "url": domain_mapping.get("status", {}).get("url"),
            },
        }
        
        domain_mapping_data = DomainMapping(formatted_domain_mapping_data, strict=False)
        
        return DomainMappingResource({
            "name": domain_mapping_short_name,
            "account": project_id,
            "region_code": location_id,
            "data": domain_mapping_data,
            "reference": ReferenceModel({
                "resource_id": domain_mapping_data.uid,
                "external_link": f"https://console.cloud.google.com/run/domains/details/{domain_mapping_data.name}"
            })
        })
