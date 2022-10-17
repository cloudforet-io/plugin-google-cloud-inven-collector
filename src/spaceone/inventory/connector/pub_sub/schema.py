import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ['SchemaConnector']
_LOGGER = logging.getLogger(__name__)


class SchemaConnector(GoogleCloudConnector):
    google_client_service = 'compute'
    version = 'v1'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
