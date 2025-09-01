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
    connector_name = "CloudRunV2Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug("** Cloud Run Service START **")
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
            "CloudRunV1Connector", **params
        )
        cloud_run_v2_conn: CloudRunV2Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        # Get lists that relate with services through Google Cloud API
        all_services = []
        try:
            locations = cloud_run_v1_conn.list_locations()
            for location in locations:
                location_id = location.get("locationId", "")
                # Cloud Run v2 doesn't support global location
                if location_id and location_id != "global":
                    try:
                        parent = f"projects/{project_id}/locations/{location_id}"
                        services = cloud_run_v2_conn.list_services(parent)
                        for service in services:
                            service["_location"] = location_id
                            # Get revisions for each service
                            service_name = service.get("name")
                            if service_name:
                                try:
                                    revisions = cloud_run_v2_conn.list_revisions(
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
            _LOGGER.warning(f"Failed to get locations: {str(e)}")

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

        _LOGGER.debug(f"** Cloud Run Service END ** ({time.time() - start_time:.2f}s)")

        return collected_cloud_services, error_responses
