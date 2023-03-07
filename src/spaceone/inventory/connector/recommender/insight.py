import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ['InsightConnector']
_LOGGER = logging.getLogger(__name__)


class InsightConnector(GoogleCloudConnector):
    google_client_service = 'recommender'
    version = 'v1beta1'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_insights(self, region, insight_type, **query):
        insights = []
        query.update({'parent': f'projects/{self.project_id}/locations/{region}/insightTypes/{insight_type}'})
        request = self.client.projects().locations().insightTypes().insights().list(**query)

        while request is not None:
            response = request.execute()
            insights = [insight for insight in response.get('insights', [])]
            request = self.client.projects().locations().insightTypes().insights().list_next(
                previous_request=request, previous_response=response)
        return insights

    def _make_parent(self):
        return f'projects/{self.project_id}/locations/us-central1-a/recommenders/google.iam.policy.Recommender'
