import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ['FunctionConnector']
_LOGGER = logging.getLogger(__name__)


class FunctionConnector(GoogleCloudConnector):

    google_client_service = 'sqladmin'
    version = 'v1beta4'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


