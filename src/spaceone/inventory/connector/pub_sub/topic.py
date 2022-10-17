import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ['TopicConnector']
_LOGGER = logging.getLogger(__name__)


class TopicConnector(GoogleCloudConnector):
    google_client_service = 'pubsub'
    version = 'v1'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_project_topic_names(self, **query):
        topic_names = []
        query.update({'project': self._make_project_fmt()})
        request = self.client.projects().topics().list(**query)

        while request is not None:
            response = request.execute()
            print(response)
            topics = response.get('topics', [])
            topic_names = [topic['name'] for topic in topics]
            request = self.client.projects().topics().list_next(previous_request=request, previous_response=response)
        return topic_names

    def get_topic_by_name(self, name):
        query = {'topic': name}
        request = self.client.projects().topics().get(**query)

        # while request is not None:
        #     response = request.execute()
        #     print(response)

    def _make_project_fmt(self):
        print(self.project_id)
        return f'projects/{self.project_id}'
