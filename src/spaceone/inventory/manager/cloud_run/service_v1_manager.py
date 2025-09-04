import logging
import time

from spaceone.inventory.connector.cloud_run.cloud_run_v1 import CloudRunV1Connector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.cloud_run.service_v1.cloud_service import (
    ServiceV1Resource,
    ServiceV1Response,
)
from spaceone.inventory.model.cloud_run.service_v1.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_run.service_v1.data import ServiceV1

_LOGGER = logging.getLogger(__name__)


class CloudRunServiceV1Manager(GoogleCloudManager):
    connector_name = "CloudRunV1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug("** Cloud Run Service V1 START **")
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
            CloudServiceResponse/ErrorResourceResponse
        """

        collected_cloud_services = []
        error_responses = []
        service_id = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        cloud_run_v1_conn: CloudRunV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        # Get lists that relate with services through Google Cloud API
        # V1은 namespace 기반이므로 단일 namespace로 모든 리소스 조회 가능
        try:
            namespace = f"namespaces/{project_id}"
            services = cloud_run_v1_conn.list_services(namespace)
            
            for service in services:
                # V1에서는 location 정보가 metadata에 포함되어 있을 수 있음
                location_id = (
                    service.get("metadata", {}).get("labels", {}).get("cloud.googleapis.com/location") or
                    service.get("metadata", {}).get("namespace", "").split("/")[-1] or
                    "us-central1"  # default location
                )
                service["_location"] = location_id
                
                # Get revisions for each service - 단순화된 revision 정보만 저장
                try:
                    revisions = cloud_run_v1_conn.list_revisions(namespace)
                    # Filter revisions for this service
                    service_name = service.get("metadata", {}).get("name", "")
                    service_revisions = [
                        rev for rev in revisions 
                        if rev.get("metadata", {}).get("labels", {}).get("serving.knative.dev/service") == service_name
                    ]
                    
                    # 복잡한 중첩 구조 대신 필요한 정보만 추출하여 단순화
                    simplified_revisions = []
                    for rev in service_revisions:
                        metadata = rev.get("metadata", {})
                        status = rev.get("status", {})
                        simplified_revision = {
                            "name": metadata.get("name"),
                            "uid": metadata.get("uid"),
                            "generation": metadata.get("generation"),
                            "create_time": metadata.get("creationTimestamp"),
                            "update_time": status.get("lastTransitionTime"),
                            "service": metadata.get("labels", {}).get("serving.knative.dev/service"),
                            "conditions": [
                                {
                                    "type": cond.get("type"),
                                    "status": cond.get("status"),
                                    "reason": cond.get("reason")
                                }
                                for cond in status.get("conditions", [])
                                if isinstance(cond, dict)
                            ]
                        }
                        simplified_revisions.append(simplified_revision)
                    
                    service["revisions"] = simplified_revisions
                    service["revision_count"] = len(simplified_revisions)
                except Exception as e:
                    _LOGGER.warning(f"Failed to get revisions for service: {str(e)}")
                    service["revisions"] = []
                    service["revision_count"] = 0
        except Exception as e:
            _LOGGER.warning(f"Failed to query services from namespace: {str(e)}")
            services = []

        for service in services:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                service_id = service.get("metadata", {}).get("name", "")
                location_id = service.get("_location", "")
                region = self.parse_region_from_zone(location_id) if location_id else ""

                ##################################
                # 2. Make Base Data
                ##################################
                service.update(
                    {
                        "project": project_id,
                        "location": location_id,
                        "region": region,
                    }
                )

                ##################################
                # 3. Make Return Resource
                ##################################
                service_data = ServiceV1(service, strict=False)

                service_resource = ServiceV1Resource(
                    {
                        "name": service_id,
                        "account": project_id,
                        "region_code": location_id,
                        "data": service_data,
                        "reference": ReferenceModel(
                            {
                                "resource_id": service_data.name,
                                "external_link": f"https://console.cloud.google.com/run/detail/{location_id}/{service_id}?project={project_id}",
                            }
                        ),
                    },
                    strict=False,
                )

                collected_cloud_services.append(ServiceV1Response({"resource": service_resource}))

            except Exception as e:
                _LOGGER.error(f"Failed to process service {service_id}: {str(e)}")
                error_response = self.generate_resource_error_response(
                    e, "ServiceV1", "CloudRun", service_id
                )
                error_responses.append(error_response)

        _LOGGER.debug(f"** Cloud Run Service V1 END ** ({time.time() - start_time:.2f}s)")

        return collected_cloud_services, error_responses
