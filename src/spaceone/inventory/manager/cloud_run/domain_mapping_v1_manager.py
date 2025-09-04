import logging
import time

from spaceone.inventory.connector.cloud_run.cloud_run_v1 import CloudRunV1Connector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.cloud_run.domain_mapping_v1.cloud_service import (
    DomainMappingResource,
    DomainMappingResponse,
)
from spaceone.inventory.model.cloud_run.domain_mapping_v1.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_run.domain_mapping_v1.data import DomainMapping

_LOGGER = logging.getLogger(__name__)


class CloudRunDomainMappingV1Manager(GoogleCloudManager):
    connector_name = "CloudRunV1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug("** Cloud Run DomainMapping START **")
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
        domain_mapping_id = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        cloud_run_v1_conn: CloudRunV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        # Get lists that relate with domain mappings through Google Cloud API
        # Domain mappings are global resources in Cloud Run v1
        try:
            domain_mappings = cloud_run_v1_conn.list_domain_mappings(
                f"namespaces/{project_id}"
            )
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get domain mappings for project {project_id}: {str(e)}"
            )
            domain_mappings = []

        for domain_mapping in domain_mappings:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                domain_mapping_id = domain_mapping.get("metadata", {}).get("name", "")
                location_id = domain_mapping.get("_location", "")
                region = self.parse_region_from_zone(location_id) if location_id else ""

                ##################################
                # 2. Make Base Data
                ##################################
                domain_mapping.update(
                    {
                        "project": project_id,
                        "location": location_id,
                        "region": region,
                    }
                )

                ##################################
                # 3. Make Return Resource
                ##################################
                domain_mapping_data = DomainMapping(domain_mapping, strict=False)

                domain_mapping_resource = DomainMappingResource(
                    {
                        "name": domain_mapping_id,
                        "account": project_id,
                        "region_code": location_id,
                        "data": domain_mapping_data,
                        "reference": ReferenceModel(
                            {
                                "resource_id": domain_mapping_data.name,
                                "external_link": f"https://console.cloud.google.com/run/domains/details/{location_id}/{domain_mapping_id}?project={project_id}",
                            }
                        ),
                    },
                    strict=False,
                )

                collected_cloud_services.append(
                    DomainMappingResponse({"resource": domain_mapping_resource})
                )

            except Exception as e:
                _LOGGER.error(
                    f"Failed to process domain mapping {domain_mapping_id}: {str(e)}"
                )
                error_response = self.generate_resource_error_response(
                    e, "CloudRun", "DomainMapping", domain_mapping_id
                )
                error_responses.append(error_response)

        _LOGGER.debug(
            f"** Cloud Run DomainMapping END ** ({time.time() - start_time:.2f}s)"
        )

        return collected_cloud_services, error_responses
