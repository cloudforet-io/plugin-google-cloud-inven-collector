import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["CloudRunV1Connector"]

_LOGGER = logging.getLogger(__name__)


class CloudRunV1Connector(GoogleCloudConnector):
    google_client_service = "run"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_locations(self, **query):
        locations = []
        query.update({"name": f"projects/{self.project_id}"})
        request = self.client.projects().locations().list(**query)

        while request is not None:
            try:
                response = request.execute()
                locations.extend(response.get("locations", []))
                request = (
                    self.client.projects().locations().list_next(request, response)
                )
            except Exception as e:
                _LOGGER.error(f"Failed to list locations: {e}")
                break

        return locations

    def list_domain_mappings(self, parent, **query):
        domain_mappings = []
        query.update({"parent": parent})

        while True:
            try:
                response = (
                    self.client.namespaces().domainmappings().list(**query).execute()
                )
                domain_mappings.extend(response.get("items", []))

                continue_token = response.get("metadata", {}).get("continue")
                if continue_token:
                    query["continue"] = continue_token
                else:
                    break
            except Exception as e:
                _LOGGER.error(f"Failed to list domain mappings: {e}")
                break

        return domain_mappings
