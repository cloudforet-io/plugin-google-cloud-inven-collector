import time
import logging

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.connector.cloud_sql.instance import CloudSQLInstanceConnector
from spaceone.inventory.model.cloud_sql.instance.cloud_service_type import CLOUD_SERVICE_TYPES
from spaceone.inventory.model.cloud_sql.instance.cloud_service import Instance, InstanceResource, InstanceResponse
from spaceone.inventory.model.cloud_sql.instance.data import Database, User

_LOGGER = logging.getLogger(__name__)


class CloudSQLManager(GoogleCloudManager):
    connector_name = 'FunctionConnector'
    cloud_service_types = CLOUD_SERVICE_TYPES
