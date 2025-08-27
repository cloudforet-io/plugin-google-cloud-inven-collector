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


class CloudBuildConnectionManager(GoogleCloudManager):
    connector_name = "CloudBuildV2Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "CloudBuild"
        self.cloud_service_type = "Connection"

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

        self.cloud_build_v2_connector = CloudBuildV2Connector(**params)

        # Location별 connections 조회
        try:
            locations = self.cloud_build_v2_connector.list_locations(f"projects/{project_id}")
            for location in locations:
                location_id = location.get("locationId")
                if location_id:
                    try:
                        parent = f"projects/{project_id}/locations/{location_id}"
                        connections = self.cloud_build_v2_connector.list_connections(parent)
                        if connections:
                            _LOGGER.debug(f"Found {len(connections)} connections in {location_id}")
                            for connection in connections:
                                try:
                                    cloud_service = self._make_cloud_build_connection_info(connection, project_id, location_id)
                                    collected_cloud_services.append(ConnectionResponse({"resource": cloud_service}))
                                except Exception as e:
                                    _LOGGER.error(f"Failed to process connection {connection.get('name', 'unknown')}: {str(e)}")
                                    error_response = self.generate_resource_error_response(e, self.cloud_service_group, "Connection", connection.get('name', 'unknown'))
                                    error_responses.append(error_response)
                    except Exception as e:
                        _LOGGER.debug(f"Failed to query connections in {location_id}: {str(e)}")
                        continue
        except Exception as e:
            _LOGGER.error(f"Failed to list locations: {str(e)}")

        _LOGGER.debug(
            f"** [{self.cloud_service_group}] {self.cloud_service_type} END ** "
            f"({time.time() - start_time:.2f}s)"
        )

        return collected_cloud_services, error_responses

    def _make_cloud_build_connection_info(self, connection: dict, project_id: str, location_id: str) -> ConnectionResource:
        """Cloud Build Connection 정보를 생성합니다."""
        connection_name = connection.get("name", "")
        
        if "/" in connection_name:
            connection_short_name = connection_name.split("/")[-1]
        else:
            connection_short_name = connection_name
        
        formatted_connection_data = {
            "name": connection.get("name"),
            "createTime": connection.get("createTime"),
            "updateTime": connection.get("updateTime"),
            "githubConfig": connection.get("githubConfig", {}),
            "githubEnterpriseConfig": connection.get("githubEnterpriseConfig", {}),
            "gitlabConfig": connection.get("gitlabConfig", {}),
            "bitbucketDataCenterConfig": connection.get("bitbucketDataCenterConfig", {}),
            "bitbucketCloudConfig": connection.get("bitbucketCloudConfig", {}),
            "installationState": connection.get("installationState", {}),
            "disabled": connection.get("disabled", False),
            "reconciling": connection.get("reconciling", False),
            "annotations": connection.get("annotations", {}),
            "etag": connection.get("etag"),
            "uid": connection.get("uid"),
        }
        
        connection_data = Connection(formatted_connection_data, strict=False)
        
        return ConnectionResource({
            "name": connection_short_name,
            "account": project_id,
            "region_code": location_id,
            "data": connection_data,
            "reference": ReferenceModel({
                "resource_id": connection_data.name,
                "external_link": f"https://console.cloud.google.com/cloud-build/repositories/2nd-gen/connections/{location_id}/{connection_short_name}?project={project_id}"
            })
        })
