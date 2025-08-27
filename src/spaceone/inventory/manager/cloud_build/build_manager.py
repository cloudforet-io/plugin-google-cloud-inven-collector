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
    connector_name = ["CloudBuildV1Connector", "CloudBuildV2Connector"]
    cloud_service_types = CLOUD_SERVICE_TYPES

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "CloudBuild"
        self.cloud_service_type = "Build"

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
        
        self.cloud_build_v1_connector = CloudBuildV1Connector(**params)
        self.cloud_build_v2_connector = CloudBuildV2Connector(**params)

        # 1. 전역 builds 조회 (global builds)
        try:
            builds = self.cloud_build_v1_connector.list_builds()
            if builds:
                _LOGGER.debug(f"Found {len(builds)} global builds")
                for build in builds:
                    try:
                        # Build location 추출
                        build_location = "global"
                        if "location" in build:
                            build_location = build.get("location", "global")
                        
                        cloud_service = self._make_cloud_build_info(build, project_id, build_location)
                        collected_cloud_services.append(BuildResponse({"resource": cloud_service}))
                    except Exception as e:
                        _LOGGER.error(f"Failed to process build {build.get('id', 'unknown')}: {str(e)}")
                        error_response = self.generate_resource_error_response(e, self.cloud_service_group, "Build", build.get('id', 'unknown'))
                        error_responses.append(error_response)
        except Exception as e:
            _LOGGER.error(f"Failed to query global builds: {str(e)}")

        # 2. 각 리전별 builds 조회 (regional builds)
        try:
            locations = self.cloud_build_v2_connector.list_locations(f"projects/{project_id}")
            for location in locations:
                location_id = location.get("locationId", "")
                if location_id:
                    try:
                        parent = f"projects/{project_id}/locations/{location_id}"
                        regional_builds = self.cloud_build_v1_connector.list_location_builds(parent)
                        if regional_builds:
                            _LOGGER.debug(f"Found {len(regional_builds)} builds in {location_id}")
                            for build in regional_builds:
                                try:
                                    cloud_service = self._make_cloud_build_info(build, project_id, location_id)
                                    collected_cloud_services.append(BuildResponse({"resource": cloud_service}))
                                except Exception as e:
                                    _LOGGER.error(f"Failed to process regional build {build.get('id', 'unknown')}: {str(e)}")
                                    error_response = self.generate_resource_error_response(e, self.cloud_service_group, "Build", build.get('id', 'unknown'))
                                    error_responses.append(error_response)
                    except Exception as e:
                        _LOGGER.error(f"Failed to query builds in location {location_id}: {str(e)}")
                        continue
        except Exception as e:
            _LOGGER.error(f"Failed to query locations: {str(e)}")

        _LOGGER.debug(
            f"** [{self.cloud_service_group}] {self.cloud_service_type} END ** "
            f"({time.time() - start_time:.2f}s)"
        )

        return collected_cloud_services, error_responses

    def _make_cloud_build_info(self, build: dict, project_id: str, location_id: str) -> BuildResource:
        """Cloud Build 정보를 생성합니다."""
        build_id = build.get("id", "")
        build_name = build.get("name", build_id)
        
        formatted_build_data = {
            "id": build.get("id"),
            "name": build.get("name"),
            "status": build.get("status"),
            "source": build.get("source", {}),
            "steps": build.get("steps", []),
            "results": build.get("results", {}),
            "createTime": build.get("createTime"),
            "startTime": build.get("startTime"),
            "finishTime": build.get("finishTime"),
            "timeout": build.get("timeout"),
            "images": build.get("images", []),
            "artifacts": build.get("artifacts", {}),
            "logsBucket": build.get("logsBucket"),
            "sourceProvenance": build.get("sourceProvenance", {}),
            "buildTriggerId": build.get("buildTriggerId"),
            "options": build.get("options", {}),
            "logUrl": build.get("logUrl"),
            "substitutions": build.get("substitutions", {}),
            "tags": build.get("tags", []),
            "timing": build.get("timing", {}),
            "approval": build.get("approval", {}),
            "serviceAccount": build.get("serviceAccount"),
            "availableSecrets": build.get("availableSecrets", {}),
            "warnings": build.get("warnings", []),
            "failureInfo": build.get("failureInfo", {}),
        }
        
        build_data = Build(formatted_build_data, strict=False)
        
        return BuildResource({
            "name": build_name,
            "account": project_id,
            "region_code": location_id,
            "data": build_data,
            "reference": ReferenceModel({
                "resource_id": build_data.id,
                "external_link": f"https://console.cloud.google.com/cloud-build/builds/{build_data.id}?project={project_id}"
            })
        })
