import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["CloudBuildV2Connector"]
_LOGGER = logging.getLogger(__name__)


class CloudBuildV2Connector(GoogleCloudConnector):
    google_client_service = "cloudbuild"
    version = "v2"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_locations(self, parent, **query):
        locations = []
        query.update({"name": parent})
        request = self.client.projects().locations().list(**query)

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
                _LOGGER.warning(f"Failed to list locations: {e}")
                break

        return locations

    def list_connections(self, parent, **query):
        connections = []
        query.update({"parent": parent})
        request = self.client.projects().locations().connections().list(**query)

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
                _LOGGER.warning(f"Failed to list connections: {e}")
                break

        return connections

    def list_repositories(self, parent, **query):
        repositories = []
        query.update({"parent": parent})
        request = (
            self.client.projects()
            .locations()
            .connections()
            .repositories()
            .list(**query)
        )

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
                _LOGGER.warning(f"Failed to list repositories: {e}")
                break

        return repositories
