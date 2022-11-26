import time
import logging
from datetime import datetime, timedelta
import google.oauth2.service_account
from google.cloud import storage
from zipfile import ZipFile
from zipfile import is_zipfile
import io

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.connector.cloud_functions.function import FunctionConnector
from spaceone.inventory.model.cloud_functions.function.cloud_service_type import CLOUD_SERVICE_TYPES, cst_function
from spaceone.inventory.model.cloud_functions.function.cloud_service import FunctionResource, FunctionResponse
from spaceone.inventory.model.cloud_functions.function.data import Function

_LOGGER = logging.getLogger(__name__)


class FunctionManager(GoogleCloudManager):
    connector_name = 'FunctionConnector'
    cloud_service_types = CLOUD_SERVICE_TYPES

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = cst_function.group
        self.cloud_service_type = cst_function.name
        self.function_conn = None

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
        _LOGGER.debug(f'** [{self.cloud_service_group}] {self.cloud_service_type} START **')

        start_time = time.time()

        collected_cloud_services = []
        error_responses = []
        function_id = ""

        secret_data = params['secret_data']
        project_id = secret_data['project_id']

        self.function_conn: FunctionConnector = self.locator.get_connector(self.connector_name, **params)

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        functions = self.function_conn.list_functions()

        for function in functions:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                function_name = function.get('name')
                location, function_id = self._make_location_and_id(function_name, project_id)
                labels = function.get('labels')

                ##################################
                # 2. Make Base Data
                ##################################
                display = {}

                # main table
                display.update({
                    'region': location,
                    'environment': self._make_readable_environment(function['environment']),
                    'function_id': function_id,
                    'last_deployed': self._make_last_deployed(function['updateTime']),
                    'trigger': self._make_trigger(function.get('eventTrigger')),
                    'runtime': self._make_runtime_for_readable(function['buildConfig']['runtime']),
                    'timeout': self._make_timeout(function['serviceConfig']['timeoutSeconds']),
                    'memory_allocated': self._make_memory_allocated(function['serviceConfig']['availableMemory']),
                    'ingress_settings': self._make_ingress_setting_readable(
                        function['serviceConfig'].get('ingressSettings')),
                    'vpc_connector_egress_settings': self._make_vpc_egress_readable(
                        function['serviceConfig'].get('vpcConnectorEgressSettings')),
                })

                if storage_source := function['buildConfig']['source'].get('storageSource'):
                    bucket = storage_source['bucket']
                    storage_object = storage_source['object']
                    source_location = self._make_source_location(bucket, storage_object)
                    display.update({
                        'source_location': source_location,
                        'source_code': self._make_source_code(bucket, storage_object, secret_data),
                    })

                if trigger_data := function.get('eventTrigger'):
                    display.update({
                        'trigger_name': self._make_trigger_name(trigger_data.get('trigger')),
                        'retry_policy': self._make_retry_policy(
                            trigger_data.get('retryPolicy', 'RETRY_POLICY_UNSPECIFIED'))
                    })

                if runtime_environment_variables := function['serviceConfig'].get('environmentVariables', {}):
                    display.update({
                        'runtime_environment_variables': self._dict_to_list_of_dict(runtime_environment_variables)
                    })
                if build_environment_variables := function['buildConfig'].get('environmentVariables', {}):
                    display.update({
                        'build_environment_variables': self._dict_to_list_of_dict(build_environment_variables)
                    })
                ##################################
                # 3. Make function data
                ##################################
                function.update({
                    # 'function_id': function_id,
                    'project': project_id,
                    'display': display
                })
                function_data = Function(function, strict=False)

                ##################################
                # 4. Make Function Resource Code
                ##################################
                function_resource = FunctionResource({
                    'name': function_name,
                    'account': project_id,
                    'tags': labels,
                    'region_code': location,
                    'instance_type': '',
                    'instance_size': 0,
                    'data': function_data,
                    'reference': ReferenceModel(function_data.reference())
                })
                self.set_region_code(location)
                ##################################
                # 5. Make Resource Response Object
                ##################################
                collected_cloud_services.append(FunctionResponse({'resource': function_resource}))

            except Exception as e:
                _LOGGER.error(f'[collect_cloud_service] => {e}', exc_info=True)
                error_response = self.generate_resource_error_response(e, self.cloud_service_group,
                                                                       self.cloud_service_type, function_id)
                error_responses.append(error_response)

        _LOGGER.debug(f'** Function Gen2 Finished {time.time() - start_time} Seconds **')
        return collected_cloud_services, error_responses

    @staticmethod
    def _make_location_and_id(function_name, project_id):
        project_path, location_and_id_path = function_name.split(f'projects/{project_id}/locations/')
        location, function, function_id = location_and_id_path.split('/')
        return location, function_id

    @staticmethod
    def _make_readable_environment(environment):
        environment_map = {
            'GEN_1': '1st gen',
            'GEN_2': '2nd gen',
            'ENVIRONMENT_UNSPECIFIED': 'unspecified'
        }
        return environment_map[environment]

    @staticmethod
    def _make_last_deployed(update_time):
        update_time, microseconds = update_time.split('.')
        updated_time = datetime.strptime(update_time, '%Y-%m-%dT%H:%M:%S')
        korea_time = updated_time + timedelta(hours=9)
        return f'{korea_time.strftime("%m/%d, %Y,%I:%M:%S %p")} GMT+9'

    @staticmethod
    def _make_trigger(event_trigger):
        if event_trigger:
            return event_trigger.get('eventType', 'Not Found')
        else:
            return 'HTTP'

    @staticmethod
    def _make_runtime_for_readable(runtime):
        runtime_map = {
            'dotnet6': '.NET 6.0',
            'dotnet3': '.NET Core 3.1',
            'go119': 'Go 1.19',
            'go118': 'Go 1.18',
            'go116': 'Go 1.16',
            'go113': 'Go 1.13',
            'java17': 'Java 17',
            'java11': 'Java 11',
            'nodejs12': 'Node.js 12',
            'nodejs14': 'Node.js 14',
            'nodejs16': 'Node.js 16',
            'php81': 'PHP 8.1',
            'php74': 'PHP 7.4',
            'python38': 'Python 3.8',
            'python39': 'Python 3.9',
            'python310': 'Python 3.10',
            'ruby30': 'Ruby 3.0',
            'ruby27': 'Ruby 2.7',
            'ruby26': 'Ruby 2.6'
        }
        return runtime_map.get(runtime, 'Not Found')

    @staticmethod
    def _make_timeout(timeout):
        return f'{timeout} seconds'

    @staticmethod
    def _make_memory_allocated(memory):
        try:
            number, unit = memory.split('Mi')
            return f'{number} MiB'
        except:
            number, unit = memory.split('Gi')
            return f'{number} GiB'

    @staticmethod
    def _make_vpc_egress_readable(egress_settings):
        if egress_settings:
            egress_settings = egress_settings.replace('_', ' ').lower()
            first_character, other_character = egress_settings[0:3], egress_settings[1:]

            if first_character == 'vpc':
                first_character = 'VPC'
            elif first_character == 'all':
                first_character = 'All'
            else:
                first_character = 'Pri'
            return first_character + other_character
        else:
            return ''

    @staticmethod
    def _make_ingress_setting_readable(ingress_settings):
        ingress_settings = ingress_settings.replace('_', ' ').lower()
        return ingress_settings[0].upper() + ingress_settings[1:]

    @staticmethod
    def _make_source_location(bucket, storage_object):
        return f'{bucket}/{storage_object}'

    @staticmethod
    def _make_source_code(bucket, storage_object, secret_data):
        credentials = google.oauth2.service_account.Credentials.from_service_account_info(secret_data)
        storage_client = storage.Client(project=secret_data['project_id'], credentials=credentials)

        bucket = storage_client.get_bucket(bucket)
        blob = bucket.blob(storage_object)
        zip_file_from_storage = io.BytesIO(blob.download_as_string())
        code_data = []
        if is_zipfile(zip_file_from_storage):
            with ZipFile(zip_file_from_storage, 'r') as file:
                for content_file_name in file.namelist():
                    content = file.read(content_file_name)
                    code_data.append({
                        'file_name': content_file_name,
                        'content': content,
                        'output_display': 'show'
                    })
        return code_data

    @staticmethod
    def _make_trigger_name(trigger_id):
        path, trigger_name = trigger_id.split('triggers/')
        return trigger_name

    @staticmethod
    def _make_retry_policy(retry_policy):
        if retry_policy == 'RETRY_POLICY_RETRY':
            return 'Enabled'
        elif retry_policy == 'RETRY_POLICY_DO_NOT_RETRY':
            return 'Disabled'
        else:
            return 'Unspecified'

    @staticmethod
    def _dict_to_list_of_dict(dict_variables: dict) -> list:
        variables = []
        for key, value in dict_variables.items():
            variables.append({'key': key, 'value': value})
        return variables
