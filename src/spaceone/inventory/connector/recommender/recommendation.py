import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ['RecommendationConnector']
_LOGGER = logging.getLogger(__name__)


class RecommendationConnector(GoogleCloudConnector):
    google_client_service = 'recommender'
    version = 'v1beta1'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_recommendations(self, **query):
        recommendations = []
        query.update({'parent': self._make_parent()})
        request = self.client.projects().locations().recommenders().recommendations().list(**query)

        while request is not None:
            response = request.execute()
            recommendations = [recommendation for recommendation in response.get('recommendations', [])]
            request = self.client.projects().locations().recommenders().recommendations().list_next(
                previous_request=request, previous_response=response)
        return recommendations

    def _make_parent(self):
        return f'projects/{self.project_id}/locations/us-central1-a/recommenders/google.iam.policy.Recommender'
