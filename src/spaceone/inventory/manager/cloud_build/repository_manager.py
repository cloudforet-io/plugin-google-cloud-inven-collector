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
from spaceone.inventory.model.cloud_build.repository.cloud_service import (
    RepositoryResource,
    RepositoryResponse,
)
from spaceone.inventory.model.cloud_build.repository.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_build.repository.data import Repository

_LOGGER = logging.getLogger(__name__)


class CloudBuildRepositoryManager(GoogleCloudManager):
    connector_name = ["CloudBuildV1Connector", "CloudBuildV2Connector"]
    cloud_service_types = CLOUD_SERVICE_TYPES

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "CloudBuild"
        self.cloud_service_type = "Repository"

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

        # Location별 connections를 통해 repositories 조회
        try:
            locations = self.cloud_build_v2_connector.list_locations(f"projects/{project_id}")
            for location in locations:
                location_id = location.get("locationId")
                if location_id:
                    try:
                        parent = f"projects/{project_id}/locations/{location_id}"
                        connections = self.cloud_build_v2_connector.list_connections(parent)
                        
                        for connection in connections:
                            connection_name = connection.get("name", "")
                            if connection_name:
                                try:
                                    repositories = self.cloud_build_v2_connector.list_repositories(connection_name)
                                    if repositories:
                                        _LOGGER.debug(f"Found {len(repositories)} repositories in connection {connection_name}")
                                        for repository in repositories:
                                            try:
                                                cloud_service = self._make_cloud_build_repository_info(repository, project_id, location_id)
                                                collected_cloud_services.append(RepositoryResponse({"resource": cloud_service}))
                                            except Exception as e:
                                                _LOGGER.error(f"Failed to process repository {repository.get('name', 'unknown')}: {str(e)}")
                                                error_response = self.generate_resource_error_response(e, self.cloud_service_group, "Repository", repository.get('name', 'unknown'))
                                                error_responses.append(error_response)
                                except Exception as e:
                                    _LOGGER.debug(f"Failed to query repositories in connection {connection_name}: {str(e)}")
                                    continue
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

    def _make_cloud_build_repository_info(self, repository: dict, project_id: str, location_id: str) -> RepositoryResource:
        """Cloud Build Repository 정보를 생성합니다."""
        repository_name = repository.get("name", "")
        
        if "/" in repository_name:
            repository_short_name = repository_name.split("/")[-1]
        else:
            repository_short_name = repository_name
        
        formatted_repository_data = {
            "name": repository.get("name"),
            "remoteUri": repository.get("remoteUri"),
            "createTime": repository.get("createTime"),
            "updateTime": repository.get("updateTime"),
            "annotations": repository.get("annotations", {}),
            "etag": repository.get("etag"),
            "uid": repository.get("uid"),
            "webhookId": repository.get("webhookId"),
        }
        
        repository_data = Repository(formatted_repository_data, strict=False)
        
        return RepositoryResource({
            "name": repository_short_name,
            "account": project_id,
            "region_code": location_id,
            "data": repository_data,
            "reference": ReferenceModel({
                "resource_id": repository_data.name,
                "external_link": f"https://console.cloud.google.com/cloud-build/repositories/2nd-gen/repositories/{location_id}/{repository_short_name}?project={project_id}"
            })
        })
