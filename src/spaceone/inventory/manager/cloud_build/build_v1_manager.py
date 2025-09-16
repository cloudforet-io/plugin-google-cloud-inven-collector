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
from spaceone.inventory.model.cloud_build.cloud_build.cloud_service import (
    BuildResource,
    BuildResponse,
)
from spaceone.inventory.model.cloud_build.cloud_build.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_build.cloud_build.data import Build

_LOGGER = logging.getLogger(__name__)


class CloudBuildBuildV1Manager(GoogleCloudManager):
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

        # Get locations using V2 API
        regional_builds = []
        parent = f"projects/{project_id}"

        try:
            locations = cloud_build_v2_conn.list_locations(parent)
            _LOGGER.info(f"V2 API: Found {len(locations)} locations for builds")
        except Exception as e:
            _LOGGER.warning(
                f"V2 API: Failed to get locations, falling back to empty list: {e}"
            )
            locations = []

        for location in locations:
            location_id = location.get("locationId", "")
            if location_id:
                try:
                    parent = f"projects/{project_id}/locations/{location_id}"
                    location_builds = cloud_build_v1_conn.list_location_builds(parent)
                    for build in location_builds:
                        build["_location"] = location_id
                    regional_builds.extend(location_builds)
                except Exception as e:
                    _LOGGER.error(
                        f"Failed to query builds in location {location_id}: {str(e)}"
                    )
                    continue

        # Combine all builds
        all_builds = builds + regional_builds
        _LOGGER.info(f"cloud build all_builds length: {len(all_builds)}")

        for build in all_builds:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                build_id = build.get("id")
                build_full_name = build.get("name", "")  # Original full path

                # Name을 첫 8자리로 변경 (04788528-aa29-4bd1-aa61-b301ea0edb8c → 04788528)
                build_name_short = (
                    build_id[:8] if build_id and len(build_id) >= 8 else build_id
                )

                # Build Trigger ID 추출 - 실제 trigger ID를 가져오거나 빈 문자열로 설정
                build_trigger_id = build.get("buildTriggerId", "")
                if not build_trigger_id:
                    # substitutions에서 TRIGGER_ID를 확인
                    build_trigger_id = build.get("substitutions", {}).get(
                        "TRIGGER_ID", ""
                    )
                if not build_trigger_id:
                    # substitutions에서 TRIGGER_NAME을 확인
                    build_trigger_id = build.get("substitutions", {}).get(
                        "TRIGGER_NAME", ""
                    )
                # 여전히 없으면 빈 문자열로 설정
                if not build_trigger_id:
                    build_trigger_id = ""

                location_id = build.get("_location", "global")
                region = (
                    self.parse_region_from_zone(location_id)
                    if location_id != "global"
                    else "global"
                )

                # Set up monitoring filters for Cloud Build
                google_cloud_monitoring_filters = [
                    {"key": "resource.labels.build_id", "value": build_id},
                ]

                ##################################
                # 2. Make Base Data
                ##################################
                build.update(
                    {
                        "project": project_id,
                        "location": location_id,
                        "region": region,
                        "name": build_name_short,  # 첫 8자리만 표시
                        "full_name": build_full_name,  # Set full path for Build ID column
                        "build_trigger_id": build_trigger_id,  # 빌드 ID만 표시
                        "google_cloud_monitoring": self.set_google_cloud_monitoring(
                            project_id,
                            "logging.googleapis.com",
                            build_id,
                            google_cloud_monitoring_filters,
                        ),
                        "google_cloud_logging": self.set_google_cloud_logging(
                            "CloudBuild", "Build", project_id, build_id
                        ),
                    }
                )

                ##################################
                # 3. Make Return Resource
                ##################################
                build_data = Build(build, strict=False)

                build_resource = BuildResource(
                    {
                        "name": build_name_short,
                        "account": project_id,
                        "region_code": location_id,
                        "data": build_data,
                        "reference": ReferenceModel(
                            {
                                "resource_id": f"https://cloudbuild.googleapis.com/v1/{build_data.full_name}",
                                # "external_link": f"https://console.cloud.google.com/cloud-build/builds?project={project_id}",
                                "external_link": f"https://console.cloud.google.com/cloud-build/builds;region={region}/{build_data.id}?project={project_id}",
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
