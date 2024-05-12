import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["SubscriptionConnector"]
_LOGGER = logging.getLogger(__name__)


class SubscriptionConnector(GoogleCloudConnector):
    google_client_service = "pubsub"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_subscriptions(self, **query):
        subscriptions = []
        query.update({"project": self._make_project_fmt()})
        request = self.client.projects().subscriptions().list(**query)

        while request is not None:
            response = request.execute()
            subscriptions = response.get("subscriptions", [])
            request = (
                self.client.projects()
                .subscriptions()
                .list_next(previous_request=request, previous_response=response)
            )
        return subscriptions

    def _make_project_fmt(self):
        return f"projects/{self.project_id}"
