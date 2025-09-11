import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["CloudBuildV2Connector"]
_LOGGER = logging.getLogger(__name__)


class CloudBuildV2Connector(GoogleCloudConnector):
    google_client_service = "cloudbuild"
    version = "v2"

    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
            _LOGGER.info("CloudBuildV2Connector initialized successfully")
        except Exception as e:
            _LOGGER.warning(f"Failed to initialize CloudBuildV2Connector: {str(e)}")
            raise

    def list_locations(self, name, **query):
        locations = []
        query.update({"name": name})
        _LOGGER.info(f"V2 API: Getting locations for name: {name}")
        try:
            request = self.client.projects().locations().list(**query)
        except Exception as e:
            _LOGGER.warning(f"V2 API: Failed to create request for locations: {e}")
            return locations

        while request is not None:
            try:
                response = request.execute()
                raw_locations = response.get("locations", [])
                # global 위치는 제외
                filtered_locations = [
                    loc for loc in raw_locations if loc.get("locationId") != "global"
                ]
                locations.extend(filtered_locations)
                request = (
                    self.client.projects().locations().list_next(request, response)
                )
            except Exception as e:
                _LOGGER.warning(f"V2 API: Failed to list locations: {e}")
                break

        return locations

    def list_connections(self, parent, **query):
        connections = []
        query.update({"parent": parent})
        try:
            request = self.client.projects().locations().connections().list(**query)
        except Exception as e:
            _LOGGER.warning(f"V2 API: Failed to create request for connections: {e}")
            return connections

        while request is not None:
            try:
                response = request.execute()
                connections.extend(response.get("connections", []))
                request = (
                    self.client.projects()
                    .locations()
                    .connections()
                    .list_next(request, response)
                )
            except Exception as e:
                _LOGGER.warning(f"V2 API: Failed to list connections: {e}")
                break

        return connections

    def list_repositories(self, parent, **query):
        repositories = []
        query.update({"parent": parent})
        _LOGGER.info(f"V2 API: Getting repositories for parent: {parent}")
        try:
            request = (
                self.client.projects()
                .locations()
                .connections()
                .repositories()
                .list(**query)
            )
        except Exception as e:
            _LOGGER.warning(f"V2 API: Failed to create request for repositories: {e}")
            return repositories

        while request is not None:
            try:
                response = request.execute()
                repositories.extend(response.get("repositories", []))
                request = (
                    self.client.projects()
                    .locations()
                    .connections()
                    .repositories()
                    .list_next(request, response)
                )
            except Exception as e:
                _LOGGER.warning(f"V2 API: Failed to list repositories: {e}")
                break

        return repositories
