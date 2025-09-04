import logging
import time

from spaceone.inventory.connector.cloud_build.cloud_build_v2 import (
    CloudBuildV2Connector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.cloud_build.connection.cloud_service import (
    ConnectionResource,
    ConnectionResponse,
)
from spaceone.inventory.model.cloud_build.connection.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_build.connection.data import Connection

_LOGGER = logging.getLogger(__name__)


class CloudBuildConnectionV2Manager(GoogleCloudManager):
    connector_name = "CloudBuildV2Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug("** Cloud Build Connection START **")
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
        connection_id = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        cloud_build_v2_conn: CloudBuildV2Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        # Get lists that relate with connections through Google Cloud API
        all_connections = []
        try:
            parent = f"projects/{project_id}"
            locations = cloud_build_v2_conn.list_locations(parent)
            for location in locations:
                location_id = location.get("locationId", "")
                if location_id:
                    try:
                        parent = f"projects/{project_id}/locations/{location_id}"
                        connections = cloud_build_v2_conn.list_connections(parent)
                        for connection in connections:
                            connection["_location"] = location_id
                        all_connections.extend(connections)
                    except Exception as e:
                        _LOGGER.debug(
                            f"Failed to query connections in location {location_id}: {str(e)}"
                        )
                        continue
        except Exception as e:
            _LOGGER.warning(f"Failed to get locations: {str(e)}")

        _LOGGER.info(f"cloud build all_connections length: {len(all_connections)}")
        for connection in all_connections:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                connection_id = connection.get("name", "")
                connection_name = (
                    self.get_param_in_url(connection_id, "connections")
                    if connection_id
                    else ""
                )
                location_id = connection.get("_location", "")
                region = self.parse_region_from_zone(location_id) if location_id else ""

                ##################################
                # 2. Make Base Data
                ##################################
                connection.update(
                    {
                        "project": project_id,
                        "location": location_id,
                        "region": region,
                    }
                )

                ##################################
                # 3. Make Return Resource
                ##################################
                connection_data = Connection(connection, strict=False)

                connection_resource = ConnectionResource(
                    {
                        "name": connection_name,
                        "account": project_id,
                        "region_code": location_id,
                        "data": connection_data,
                        "reference": ReferenceModel(
                            {
                                "resource_id": connection_data.name,
                                "external_link": f"https://console.cloud.google.com/cloud-build/repositories/2nd-gen?project={project_id}",
                            }
                        ),
                    },
                    strict=False,
                )

                collected_cloud_services.append(
                    ConnectionResponse({"resource": connection_resource})
                )

            except Exception as e:
                _LOGGER.error(f"Failed to process connection {connection_id}: {str(e)}")
                error_response = self.generate_resource_error_response(
                    e, "CloudBuild", "Connection", connection_id
                )
                error_responses.append(error_response)

        _LOGGER.debug(
            f"** Cloud Build Connection END ** ({time.time() - start_time:.2f}s)"
        )

        return collected_cloud_services, error_responses
