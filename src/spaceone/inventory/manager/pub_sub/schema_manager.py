import logging
import time

from spaceone.inventory.connector.pub_sub.schema import SchemaConnector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.pub_sub.schema.cloud_service import SchemaResource, SchemaResponse
from spaceone.inventory.model.pub_sub.schema.cloud_service_type import CLOUD_SERVICE_TYPES
from spaceone.inventory.model.pub_sub.schema.data import Schema

_LOGGER = logging.getLogger(__name__)


class SchemaManager(GoogleCloudManager):
    connector_name = 'SchemaConnector'
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
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
        _LOGGER.debug(f'** Pub/Sub Schema START **')

        start_time = time.time()
        collected_cloud_services = []
        error_responses = []
        schema_id = ""

        secret_data = params['secret_data']
        project_id = secret_data['project_id']

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        schema_conn: SchemaConnector = self.locator.get_connector(self.connector_name, **params)
        schema_names = schema_conn.list_schema_names()

        for schema_name in schema_names:
            try:
                schema = schema_conn.get_schema(schema_name)

                ##################################
                # 1. Set Basic Information
                ##################################
                schema_id = self._make_schema_id(schema_name, project_id)

                ##################################
                # 2. Make Base Data
                ##################################

                ##################################
                # 3. Make schema data
                ##################################
                display = {
                    'output_display': 'show'
                }

                schema.update({
                    'id': schema_id,
                    'project': project_id,
                    'schema_type': schema.get('type'),
                    'display': display
                })
                schema_data = Schema(schema, strict=False)

                ##################################
                # 4. Make TopicResource Code
                ##################################
                schema_resource = SchemaResource({
                    'name': schema_name,
                    'account': project_id,
                    'tags': [],
                    'region_code': 'Global',
                    'instance_type': '',
                    'instance_size': 0,
                    'data': schema_data,
                    'reference': ReferenceModel(schema_data.reference())
                })

                ##################################
                # 5. Make Resource Response Object
                ##################################
                collected_cloud_services.append(SchemaResponse({'resource': schema_resource}))
                time.sleep(0.1)

            except Exception as e:
                _LOGGER.error(f'[collect_cloud_service] => {e}', exc_info=True)
                error_response = self.generate_resource_error_response(e, 'Pub/Sub', 'Schema', schema_id)
                error_responses.append(error_response)

        _LOGGER.debug(f'** Pub/Sub Scheam Finished {time.time() - start_time} Seconds **')
        return collected_cloud_services, error_responses

    @staticmethod
    def _make_schema_id(schema_name, project_id):
        path, schema_id = schema_name.split(f'projects/{project_id}/schemas/')
        return schema_id
