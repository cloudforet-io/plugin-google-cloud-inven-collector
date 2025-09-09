import logging
import time

from spaceone.inventory.conf.cloud_service_conf import REGION_INFO
from spaceone.inventory.connector.cloud_run.cloud_run_v2 import CloudRunV2Connector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.cloud_run.service_v2.cloud_service import (
    ServiceResource,
    ServiceResponse,
)
from spaceone.inventory.model.cloud_run.service_v2.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_run.service_v2.data import Service

_LOGGER = logging.getLogger(__name__)


class CloudRunServiceV2Manager(GoogleCloudManager):
    connector_name = "CloudRunV2Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug("** Cloud Run Service V2 START **")
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
        cloud_run_v2_conn: CloudRunV2Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        # Get lists that relate with services through Google Cloud API
        all_services = []
        try:
            # REGION_INFO에서 모든 위치 사용 (global 제외)
            for region_id in REGION_INFO.keys():
                if region_id == "global":
                    continue
                location_id = region_id
                try:
                    parent = f"projects/{project_id}/locations/{location_id}"
                    services = cloud_run_v2_conn.list_services(parent)
                    for service in services:
                        service["_location"] = location_id
                        # Get revisions for each service
                        service_name = service.get("name")
                        if service_name:
                            try:
                                revisions = cloud_run_v2_conn.list_service_revisions(
                                    service_name
                                )
                                service["revisions"] = revisions
                                service["revision_count"] = len(revisions)
                            except Exception as e:
                                _LOGGER.warning(
                                    f"Failed to get revisions for service {service_name}: {str(e)}"
                                )
                                service["revisions"] = []
                                service["revision_count"] = 0
                    all_services.extend(services)
                except Exception as e:
                    _LOGGER.debug(
                        f"Failed to query services in location {location_id}: {str(e)}"
                    )
                    continue
        except Exception as e:
            _LOGGER.warning(f"Failed to iterate REGION_INFO: {str(e)}")

        for service in all_services:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                service_id = service.get("name", "")
                service_name = (
                    self.get_param_in_url(service_id, "services") if service_id else ""
                )
                location_id = service.get("_location", "")
                region = self.parse_region_from_zone(location_id) if location_id else ""

                ##################################
                # 2. Make Base Data
                ##################################
                # Extract URL from service
                service_uri = service.get("uri", "")

                # Extract status information
                status = service.get("status", {})
                latest_ready_revision_name = status.get("latestReadyRevisionName", "")
                latest_created_revision_name = status.get(
                    "latestCreatedRevisionName", ""
                )

                # If latest_ready_revision_name is empty, try to get from latestReadyRevision
                if not latest_ready_revision_name:
                    latest_ready_revision = service.get("latestReadyRevision", "")
                    if latest_ready_revision and "/revisions/" in latest_ready_revision:
                        latest_ready_revision_name = latest_ready_revision.split(
                            "/revisions/"
                        )[-1]

                # If latest_created_revision_name is empty, try to get from latestCreatedRevision
                if not latest_created_revision_name:
                    latest_created_revision = service.get("latestCreatedRevision", "")
                    if (
                        latest_created_revision
                        and "/revisions/" in latest_created_revision
                    ):
                        latest_created_revision_name = latest_created_revision.split(
                            "/revisions/"
                        )[-1]

                # Extract terminal condition for status
                terminal_condition = service.get("terminalCondition", {})
                if not terminal_condition:
                    # Fallback: check status.terminalCondition
                    terminal_condition = status.get("terminalCondition", {})
                if not terminal_condition:
                    # Fallback: check conditions array for terminal condition
                    conditions = service.get("conditions", [])
                    for condition in conditions:
                        if condition.get("type") == "Ready":
                            terminal_condition = condition
                            break

                # Extract additional information
                template = service.get("template", {})
                ingress = service.get("ingress", "")

                # Determine deployment type based on template
                deployment_type = "Service"  # Default
                if template.get("containers"):
                    # Check if it's a function deployment
                    containers = template.get("containers", [])
                    if containers and any(
                        "function" in str(container).lower() for container in containers
                    ):
                        deployment_type = "Function"

                # Extract authentication info
                authentication = "No Authentication Required"
                if template.get("serviceAccount"):
                    authentication = "Authentication Required"

                # Extract deployer information
                deployer = service.get("creator", "")
                if not deployer:
                    deployer = service.get("lastModifier", "")

                # Extract last deployment time
                last_deployment_time = service.get("updateTime", "")

                service.update(
                    {
                        "name": service_name,  # Set name for SpaceONE display
                        "project": project_id,
                        "location": location_id,
                        "region": region,
                        "uri": service_uri,
                        "latest_ready_revision_name": latest_ready_revision_name,
                        "latest_created_revision_name": latest_created_revision_name,
                        "terminal_condition": terminal_condition,
                        "deployment_type": deployment_type,
                        "requests_per_second": 0,  # Default value, could be calculated from metrics
                        "authentication": authentication,
                        "ingress": ingress,
                        "last_deployment_time": last_deployment_time,
                        "deployer": deployer,
                    }
                )

                ##################################
                # 3. Make Return Resource
                ##################################
                service_data = Service(service, strict=False)

                service_resource = ServiceResource(
                    {
                        "name": service_name,
                        "account": project_id,
                        "region_code": location_id,
                        "data": service_data,
                        "reference": ReferenceModel(
                            {
                                "resource_id": service_data.name,
                                "external_link": f"https://console.cloud.google.com/run/detail/{location_id}/{service_name}?project={project_id}",
                            }
                        ),
                    },
                    strict=False,
                )

                collected_cloud_services.append(
                    ServiceResponse({"resource": service_resource})
                )

            except Exception as e:
                _LOGGER.error(f"Failed to process service {service_id}: {str(e)}")
                error_response = self.generate_resource_error_response(
                    e, "CloudRun", "Service", service_id
                )
                error_responses.append(error_response)

        _LOGGER.debug(
            f"** Cloud Run Service V2 END ** ({time.time() - start_time:.2f}s)"
        )

        return collected_cloud_services, error_responses
