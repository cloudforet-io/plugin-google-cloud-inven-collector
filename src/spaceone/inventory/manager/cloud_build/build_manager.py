import logging
import time

from spaceone.inventory.connector.cloud_build.cloud_build_v1 import (
    CloudBuildV1Connector,
)
from spaceone.inventory.connector.cloud_build.cloud_build_v2 import (
    CloudBuildV2Connector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.cloud_build.build.cloud_service import (
    BuildResource,
    BuildResponse,
)
from spaceone.inventory.model.cloud_build.build.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_build.build.data import Build

_LOGGER = logging.getLogger(__name__)


class CloudBuildBuildManager(GoogleCloudManager):
    connector_name = "CloudBuildV1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug("** Cloud Build Build START **")
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
        build_id = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        cloud_build_v1_conn: CloudBuildV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )
        cloud_build_v2_conn: CloudBuildV2Connector = self.locator.get_connector(
            "CloudBuildV2Connector", **params
        )

        # Get lists that relate with builds through Google Cloud API
        builds = cloud_build_v1_conn.list_builds()

        # Get locations and regional builds
        regional_builds = []
        try:
            parent = f"projects/{project_id}"
            locations = cloud_build_v2_conn.list_locations(parent)
            for location in locations:
                location_id = location.get("locationId", "")
                if location_id:
                    try:
                        parent = f"projects/{project_id}/locations/{location_id}"
                        location_builds = cloud_build_v1_conn.list_location_builds(
                            parent
                        )
                        for build in location_builds:
                            build["_location"] = location_id
                        regional_builds.extend(location_builds)
                    except Exception as e:
                        _LOGGER.error(
                            f"Failed to query builds in location {location_id}: {str(e)}"
                        )
                        continue
        except Exception as e:
            _LOGGER.warning(f"Failed to get locations: {str(e)}")

        # Combine all builds
        all_builds = builds + regional_builds
        _LOGGER.info(f"cloud build all_builds length: {len(all_builds)}")

        for build in all_builds:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                build_id = build.get("id")
                build_name = build.get("name", build_id)
                location_id = build.get("_location", "global")
                region = (
                    self.parse_region_from_zone(location_id)
                    if location_id != "global"
                    else "global"
                )

                ##################################
                # 2. Make Base Data
                ##################################
                build.update(
                    {
                        "project": project_id,
                        "location": location_id,
                        "region": region,
                    }
                )

                ##################################
                # 3. Make Return Resource
                ##################################
                build_data = Build(build, strict=False)

                build_resource = BuildResource(
                    {
                        "name": build_name,
                        "account": project_id,
                        "region_code": location_id,
                        "data": build_data,
                        "reference": ReferenceModel(
                            {
                                "resource_id": build_data.id,
                                "external_link": f"https://console.cloud.google.com/cloud-build/builds?project={project_id}",
                            }
                        ),
                    },
                    strict=False,
                )

                collected_cloud_services.append(
                    BuildResponse({"resource": build_resource})
                )

            except Exception as e:
                _LOGGER.error(f"Failed to process build {build_id}: {str(e)}")
                error_response = self.generate_resource_error_response(
                    e, "CloudBuild", "Build", build_id
                )
                error_responses.append(error_response)

        _LOGGER.debug(f"** Cloud Build Build END ** ({time.time() - start_time:.2f}s)")

        return collected_cloud_services, error_responses
