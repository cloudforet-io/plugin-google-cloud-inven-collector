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
from spaceone.inventory.connector.cloud_functions.function_gen1 import FunctionGen1Connector
from spaceone.inventory.connector.cloud_functions.eventarc import EventarcConnector
from spaceone.inventory.model.cloud_functions.function_gen1.cloud_service_type import CLOUD_SERVICE_TYPES, cst_function
from spaceone.inventory.model.cloud_functions.function_gen1.cloud_service import FunctionResource, FunctionResponse
from spaceone.inventory.model.cloud_functions.function_gen1.data import FunctionGen1

_LOGGER = logging.getLogger(__name__)


class FunctionGen1Manager(GoogleCloudManager):
    connector_name = 'FunctionGen1Connector'
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
        start_time = time.time()
        collected_cloud_services = []
        error_responses = []
        function_id = ""

        secret_data = params['secret_data']
        project_id = secret_data['project_id']
        trigger_provider_map = self._create_trigger_provider_map(params)

        self.function_conn: FunctionGen1Connector = self.locator.get_connector(self.connector_name, **params)

        functions = self.function_conn.list_functions()

        for function in functions:
            try:
                function_name = function.get('name')
                location, function_id = self._make_location_and_id(function_name, project_id)
                labels = function.get('labels')

                display = {}
                display.update({
                    'region': location,
                    'environment': '1st gen',
                    'function_id': function_id,
                    'last_deployed': self._make_last_deployed(function['updateTime']),
                    'runtime': self._make_runtime_for_readable(function['runtime']),
                    'timeout': self._make_timeout(function['timeout']),
                    'memory_allocated': self._make_memory_allocated(function['availableMemoryMb']),
                    'ingress_settings': self._make_ingress_setting_readable(function['ingressSettings']),
                    'vpc_connector_egress_settings': self._make_vpc_egress_readable(
                        function.get('vpc_connector_egress_settings'))
                })

                if http_trigger := function.get('httpsTrigger'):
                    display.update({
                        'trigger': 'HTTP',
                        'http_url': http_trigger['url']
                    })
                # TODO: need to solve 'Not Fount' about event_provider
                if event_trigger := function.get('eventTrigger'):
                    trigger = self._get_event_provider_from_trigger_map(event_trigger['eventType'],
                                                                        trigger_provider_map)
                    display.update({
                        'trigger': trigger,
                        'event_provider': trigger
                    })

                if function.get('sourceUploadUrl'):
                    bucket = self._make_bucket_from_build_name(function.get('buildName'))
                    source_location, source_code = self._get_source_location_and_code(bucket, function_id, secret_data)

                    display.update({
                        'source_location': source_location,
                        'source_code': source_code
                    })

                if runtime_environment_variables := function.get('environmentVariables'):
                    display.update({
                        'runtime_environment_variables': self._dict_to_list_of_dict(runtime_environment_variables)
                    })
                if build_environment_variables := function.get('buildEnvironmentVariables'):
                    display.update({
                        'build_environment_variables': self._dict_to_list_of_dict(build_environment_variables)
                    })

                function.update({
                    # 'function_id': function_id,
                    'project': project_id,
                    'display': display
                })
                function_data = FunctionGen1(function, strict=False)

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

                collected_cloud_services.append(FunctionResponse({'resource': function_resource}))

            except Exception as e:
                _LOGGER.error(f'[collect_cloud_service] => {e}', exc_info=True)
                error_response = self.generate_resource_error_response(e, self.cloud_service_group,
                                                                       self.cloud_service_type, function_id)
                error_responses.append(error_response)

        _LOGGER.debug(f'** Function Gen1 Finished {time.time() - start_time} Seconds **')
        return collected_cloud_services, error_responses

    @staticmethod
    def _make_location_and_id(function_name, project_id):
        project_path, location_and_id_path = function_name.split(f'projects/{project_id}/locations/')
        location, function, function_id = location_and_id_path.split('/')
        return location, function_id

    @staticmethod
    def _make_last_deployed(update_time):
        update_time, microseconds = update_time.split('.')
        updated_time = datetime.strptime(update_time, '%Y-%m-%dT%H:%M:%S')
        korea_time = updated_time + timedelta(hours=9)
        return f'{korea_time.strftime("%m/%d, %Y,%I:%M:%S %p")} GMT+9'

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
        return f'{timeout[:-1]} seconds'

    @staticmethod
    def _make_memory_allocated(memory):
        return f'{memory} MiB'

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
    def _make_bucket_from_build_name(build_name):
        items = list(build_name.split('/'))
        bucket_project = items[1]
        bucket_region = items[3]
        return f'gcf-sources-{bucket_project}-{bucket_region}'

    @staticmethod
    def _make_storage_object(function_id):
        return f'{function_id}/version-1/function-source.zip'

    @staticmethod
    def _get_source_location_and_code(bucket_name, function_id, secret_data):
        credentials = google.oauth2.service_account.Credentials.from_service_account_info(secret_data)
        storage_client = storage.Client(project=secret_data['project_id'], credentials=credentials)

        bucket = storage_client.get_bucket(bucket_name)
        blob_names = [blob.name for blob in bucket.list_blobs()]

        location = ''
        blob = None
        for blob_name in blob_names:
            if function_id == blob_name[:len(function_id)]:
                blob = bucket.blob(blob_name)
                location = f'{bucket_name}/{blob_name}'
        if blob:
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
            return location, code_data
        else:
            return '', {}

    @staticmethod
    def _dict_to_list_of_dict(dict_variables: dict) -> list:
        variables = []
        for key, value in dict_variables.items():
            variables.append({'key': key, 'value': value})
        return variables

    def _create_trigger_provider_map(self, params):
        providers = self._list_providers_from_eventarc(params)

        trigger_provider_map = {}
        for provider in providers:
            display_name = provider['displayName']

            event_types = []
            for event_type in provider['eventTypes']:
                if display_name in trigger_provider_map:
                    if event_type not in trigger_provider_map[display_name]:
                        event_types.append(event_type['type'])
                else:
                    event_types.append(event_type['type'])
            trigger_provider_map[display_name] = event_types
        return trigger_provider_map

    def _list_providers_from_eventarc(self, params):
        eventarc_conn: EventarcConnector = self.locator.get_connector('EventarcConnector', **params)
        providers = eventarc_conn.list_providers()
        return providers

    @staticmethod
    def _get_event_provider_from_trigger_map(event_type, trigger_provider_map):
        for display_name, event_types in trigger_provider_map.items():
            if event_type in event_types:
                return display_name
        return 'Not Found'
