import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ['RecommendationConnector']
_LOGGER = logging.getLogger(__name__)


class RecommendationConnector(GoogleCloudConnector):
    google_client_service = 'recommender'
    version = 'v1beta1'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_recommendation(self, name):
        return self.client.projects().locations().recommenders().recommendations().get(name=name).execute()
