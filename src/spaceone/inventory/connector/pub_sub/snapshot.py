import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["SnapshotConnector"]
_LOGGER = logging.getLogger(__name__)


class SnapshotConnector(GoogleCloudConnector):
    google_client_service = "pubsub"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_snapshots(self, **query):
        snapshots = []
        query.update({"project": self._make_project_fmt()})
        request = self.client.projects().snapshots().list(**query)

        while request is not None:
            response = request.execute()
            snapshots = response.get("snapshots", [])
            request = (
                self.client.projects()
                .snapshots()
                .list_next(previous_request=request, previous_response=response)
            )
        return snapshots

    def _make_project_fmt(self):
        return f"projects/{self.project_id}"
