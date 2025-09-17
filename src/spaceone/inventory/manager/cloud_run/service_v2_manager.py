import logging
import time

from spaceone.inventory.connector.cloud_run.cloud_run_v1 import CloudRunV1Connector
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
        cloud_run_v1_conn: CloudRunV1Connector = self.locator.get_connector(
            "CloudRunV1Connector", **params
        )

        all_services = []
        parent = f"projects/{project_id}"

        try:
            locations = cloud_run_v1_conn.list_locations(parent)
            _LOGGER.info(f"V1 API: Found {len(locations)} locations for services")
        except Exception as e:
            _LOGGER.warning(
                f"V1 API: Failed to get locations, falling back to empty list: {e}"
            )
            locations = []

        try:
            for location in locations:
                location_id = location.get("locationId", "")
                if location_id:
                    try:
                        parent = f"projects/{project_id}/locations/{location_id}"
                        services = cloud_run_v2_conn.list_services(parent)
                        for service in services:
                            service["_location"] = location_id
                            # Get revisions for each service
                            service_name = service.get("name")
                            if service_name:
                                try:
                                    revisions = (
                                        cloud_run_v2_conn.list_service_revisions(
                                            service_name
                                        )
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
            _LOGGER.warning(f"Failed to process locations: {str(e)}")

        for service in all_services:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                service_id = service.get("name", "")
                service_name = (
                    self.get_param_in_url(service_id, "services") if service_id else ""
                )
                full_name = service.get("name", service_name)
                location_id = service.get("_location", "")
                region = self.parse_region_from_zone(location_id) if location_id else ""

                ##################################
                # 2. Make Base Data
                ##################################
                service_uri = service.get("uri", "")
                status = service.get("status", {})
                latest_ready_revision_name = status.get("latestReadyRevisionName", "")
                latest_created_revision_name = status.get(
                    "latestCreatedRevisionName", ""
                )

                if not latest_ready_revision_name:
                    latest_ready_revision = service.get("latestReadyRevision", "")
                    if latest_ready_revision and "/revisions/" in latest_ready_revision:
                        latest_ready_revision_name = latest_ready_revision.split(
                            "/revisions/"
                        )[-1]

                if not latest_created_revision_name:
                    latest_created_revision = service.get("latestCreatedRevision", "")
                    if (
                        latest_created_revision
                        and "/revisions/" in latest_created_revision
                    ):
                        latest_created_revision_name = latest_created_revision.split(
                            "/revisions/"
                        )[-1]

                terminal_condition = service.get("terminalCondition", {})
                if not terminal_condition:
                    terminal_condition = status.get("terminalCondition", {})
                if not terminal_condition:
                    conditions = service.get("conditions", [])
                    for condition in conditions:
                        if condition.get("type") == "Ready":
                            terminal_condition = condition
                            break

                template = service.get("template", {})
                ingress = service.get("ingress", "")

                deployment_type = "Service"
                if template.get("containers"):
                    containers = template.get("containers", [])
                    if containers and any(
                        "function" in str(container).lower() for container in containers
                    ):
                        deployment_type = "Function"

                authentication = "No Authentication Required"
                if template.get("serviceAccount"):
                    authentication = "Authentication Required"

                deployer = service.get("creator", "")
                if not deployer:
                    deployer = service.get("lastModifier", "")

                last_deployment_time = service.get("updateTime", "")

                google_cloud_monitoring_filters = [
                    {"key": "resource.labels.service_name", "value": service_name},
                ]

                service.update(
                    {
                        "name": service_name,
                        "full_name": full_name,
                        "project": project_id,
                        "location": location_id,
                        "region": region,
                        "uri": service_uri,
                        "latest_ready_revision_name": latest_ready_revision_name,
                        "latest_created_revision_name": latest_created_revision_name,
                        "terminal_condition": terminal_condition,
                        "deployment_type": deployment_type,
                        "requests_per_second": 0,
                        "authentication": authentication,
                        "ingress": ingress,
                        "last_deployment_time": last_deployment_time,
                        "deployer": deployer,
                        "google_cloud_monitoring": self.set_google_cloud_monitoring(
                            project_id,
                            "run.googleapis.com",
                            service_name,
                            google_cloud_monitoring_filters,
                        ),
                        "google_cloud_logging": self.set_google_cloud_logging(
                            "CloudRun", "Service", project_id, service_name
                        ),
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
                                "resource_id": f"https://run.googleapis.com/v2/{service_data.full_name}",
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
