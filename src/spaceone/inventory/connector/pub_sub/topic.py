import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["TopicConnector"]
_LOGGER = logging.getLogger(__name__)


class TopicConnector(GoogleCloudConnector):
    google_client_service = "pubsub"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_topics(self, **query):
        topics = []
        query.update({"project": self._make_project_fmt()})
        request = self.client.projects().topics().list(**query)

        while request is not None:
            response = request.execute()
            topics = response.get("topics", [])
            request = (
                self.client.projects()
                .topics()
                .list_next(previous_request=request, previous_response=response)
            )
        return topics

    def list_snapshot_names(self, topic_name):
        snapshots = []
        query = {"topic": topic_name}
        snapshot_service = self.client.projects().topics().snapshots()
        request = snapshot_service.list(**query)

        while request is not None:
            response = request.execute()
            snapshots = response.get("snapshots", [])
            request = snapshot_service.list_next(
                previous_request=request, previous_response=response
            )
        return snapshots

    def list_subscription_names(self, topic_name):
        subscriptions = []
        query = {"topic": topic_name}
        subscription_service = self.client.projects().topics().subscriptions()
        request = subscription_service.list(**query)

        while request is not None:
            response = request.execute()
            subscriptions = response.get("subscriptions", [])
            request = subscription_service.list_next(
                previous_request=request, previous_response=response
            )
        return subscriptions

    def get_subscription(self, subscription_name):
        query = {"subscription": subscription_name}
        subscription_service = self.client.projects().subscriptions()
        request = subscription_service.get(**query)
        response = request.execute()
        return response

    def get_snapshot(self, snapshot_name):
        query = {"snapshot": snapshot_name}
        snapshot_service = self.client.projects().snapshots()
        request = snapshot_service.get(**query)
        response = request.execute()
        return response

    def _make_project_fmt(self):
        return f"projects/{self.project_id}"
