import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ['TopicConnector']
_LOGGER = logging.getLogger(__name__)


class TopicConnector(GoogleCloudConnector):
    google_client_service = 'compute'
    version = 'v1'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
