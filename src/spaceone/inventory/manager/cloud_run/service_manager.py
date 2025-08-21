import logging
import time

from spaceone.inventory.connector.cloud_run.cloud_run_v1 import CloudRunV1Connector
from spaceone.inventory.connector.cloud_run.cloud_run_v2 import CloudRunV2Connector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.cloud_run.service.cloud_service import (
    ServiceResource,
    ServiceResponse,
)
from spaceone.inventory.model.cloud_run.service.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_run.service.data import Service

_LOGGER = logging.getLogger(__name__)


class CloudRunServiceManager(GoogleCloudManager):
    connector_name = ["CloudRunV1Connector", "CloudRunV2Connector"]
    cloud_service_types = CLOUD_SERVICE_TYPES

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "CloudRun"
        self.cloud_service_type = "Service"
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
        self.cloud_run_v2_connector = CloudRunV2Connector(**params)

        # Cloud Run v1 API를 사용하여 location 목록 조회
        locations = self.cloud_run_v1_connector.list_locations()
        location_ids = [location.get('locationId') for location in locations if location.get('locationId')]
        
        # 각 location에서 Cloud Run Services 조회
        for location_id in location_ids:
            parent = f"projects/{project_id}/locations/{location_id}"
            
            try:                
                # Cloud Run v2 Services 조회
                services = self.cloud_run_v2_connector.list_services(parent)
                if services:
                    _LOGGER.debug(f"Found {len(services)} services in {location_id}")
                    for service in services:
                        try:
                            # 각 Service의 Revisions 조회
                            service_name = service.get("name")
                            if service_name:
                                revisions = self.cloud_run_v2_connector.list_revisions(service_name)
                                service["revisions"] = revisions
                                service["revision_count"] = len(revisions)
                            
                            cloud_service = self._make_cloud_run_service_info(service, project_id, location_id)
                            collected_cloud_services.append(ServiceResponse({"resource": cloud_service}))
                        except Exception as e:
                            _LOGGER.error(f"Failed to process service {service.get('name', 'unknown')}: {str(e)}")
                            error_response = self.generate_resource_error_response(e, self.cloud_service_group, "Service", service.get('name', 'unknown'))
                            error_responses.append(error_response)
                        
            except Exception as e:
                # 특정 location에서 API 호출이 실패해도 다른 location은 계속 확인
                _LOGGER.debug(f"Failed to query {location_id}: {str(e)}")
                continue

        _LOGGER.debug(
            f"** [{self.cloud_service_group}] {self.cloud_service_type} END ** "
            f"({time.time() - start_time:.2f}s)"
        )

        return collected_cloud_services, error_responses

    def _make_cloud_run_service_info(self, service: dict, project_id: str, location_id: str) -> ServiceResource:
        """Cloud Run Service 정보를 생성합니다."""
        service_name = service.get("name", "")
        
        if "/" in service_name:
            service_short_name = service_name.split("/")[-1]
        else:
            service_short_name = service_name
        
        formatted_service_data = {
            "name": service.get("name"),
            "uid": service.get("uid"),
            "generation": service.get("generation"),
            "labels": service.get("labels", {}),
            "annotations": service.get("annotations", {}),
            "createTime": service.get("createTime"),
            "updateTime": service.get("updateTime"),
            "deleteTime": service.get("deleteTime"),
            "expireTime": service.get("expireTime"),
            "creator": service.get("creator"),
            "lastModifier": service.get("lastModifier"),
            "client": service.get("client"),
            "ingress": service.get("ingress"),
            "launchStage": service.get("launchStage"),
            # "template": service.get("template", {}),
            "traffic": service.get("traffic", []),
            "urls": service.get("urls", []),
            "observedGeneration": service.get("observedGeneration"),
            "terminalCondition": service.get("terminalCondition"),
            "conditions": service.get("conditions", []),
            "latestReadyRevisionName": service.get("latestReadyRevisionName"),
            "latestCreatedRevisionName": service.get("latestCreatedRevisionName"),
            # "trafficStatuses": service.get("trafficStatuses", []),
            "uri": service.get("uri"),
            "etag": service.get("etag"),
            "revisions": [
                {
                    "name": revision.get("name"),
                    "uid": revision.get("uid"),
                    "service": revision.get("service"),
                    "generation": revision.get("generation"),
                    "createTime": revision.get("createTime"),
                    "updateTime": revision.get("updateTime"),
                    "conditions": revision.get("conditions", []),
                }
                for revision in service.get("revisions", [])
            ],
            "revision_count": len(service.get("revisions", [])),
        }
        
        service_data = Service(formatted_service_data, strict=False)
        
        return ServiceResource({
            "name": service_short_name,
            "account": project_id,
            "region_code": location_id,
            "data": service_data,
            "reference": ReferenceModel({
                "resource_id": service_data.uid,
                "external_link": f"https://console.cloud.google.com/run/detail/{service_data.name}"
            })
        })




