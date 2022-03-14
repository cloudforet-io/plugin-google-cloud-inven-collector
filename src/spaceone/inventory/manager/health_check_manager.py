import time
import logging

from spaceone.inventory.connector import HealthCheckConnector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.health_check.cloud_service import *
from spaceone.inventory.model.health_check.cloud_service_type import CLOUD_SERVICE_TYPES

_LOGGER = logging.getLogger(__name__)


class HealthCheckManager(GoogleCloudManager):
    connector_name = 'HealthCheckConnector'
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug(f'** HealthCheck Start **')
        start_time = time.time()
        """
        Args:
            params:
                - options
                - schema
                - secret_data
                - filter
                - zones
        Response:
            CloudServiceResponse/ErrorResourceResponse
        """
        collected_cloud_services = []
        error_responses = []
        health_check_id = ""
        secret_data = params['secret_data']
        project_id = secret_data['project_id']

        health_check_conn: HealthCheckConnector = self.locator.get_connector(self.connector_name, **params)
        health_checks = health_check_conn.list_health_checks()

        for health_check in health_checks:
            try:
                # No labels!!
                health_check_id = health_check.get('id')
                health_check_data = HealthCheck(health_check, strict=False)
                health_check_resource = HealthCheckResource({
                    'name': health_check_data['name'],
                    'account': project_id,
                    'region_code': 'hardcoded',
                    'data': health_check_data,
                    'reference': ReferenceModel(health_check_data.reference())
                })
                collected_cloud_services.append(HealthCheckResponse({'resource': health_check_resource}))
            except Exception as e:
                _LOGGER.error(f'[collect_cloud_service] => {e}', exc_info=True)
                error_response = self.generate_resource_error_response(e, 'ComputeEngine', 'HealthCheck', health_check_id)
                error_responses.append(error_response)

        _LOGGER.debug(f'** HealthCheck Finished {time.time() - start_time} Seconds **')
        return collected_cloud_services, error_responses

    @staticmethod
    def get_stackdriver(project, name):
        return {
            'type': 'cloudsql.googleapis.com',
            'identifier': 'database_id',
            'filters': [{
                'key': 'resource.label.database_id',
                'value': f'{project}:{name}' if project != '' else f'{name}'
            }]
        }


