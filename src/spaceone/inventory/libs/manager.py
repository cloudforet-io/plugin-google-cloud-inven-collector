import math
import json
import logging
import ipaddress
from urllib.parse import urlparse

from spaceone.core.manager import BaseManager
from spaceone.inventory.libs.connector import GoogleCloudConnector
from spaceone.inventory.libs.schema.region import RegionResource, RegionResponse
from spaceone.inventory.libs.schema.cloud_service import ErrorResourceResponse


_LOGGER = logging.getLogger(__name__)

REGION_INFO = {
    "asia-east1": {"name": "Taiwan (Changhua County)", "tags": {"latitude": "24.051196", "longitude": "120.516430", "continent": "asia_pacific"}},
    "asia-east2": {"name": "Hong Kong", "tags": {"latitude": "22.283289", "longitude": "114.155851", "continent": "asia_pacific"}},
    "asia-northeast1": {"name": "Japan (Tokyo)", "tags": {"latitude": "35.628391", "longitude": "139.417634", "continent": "asia_pacific"}},
    "asia-northeast2": {"name": "Japan (Osaka)", "tags": {"latitude": "34.705403", "longitude": "135.490119", "continent": "asia_pacific"}},
    "asia-northeast3": {"name": "South Korea (Seoul)", "tags": {"latitude": "37.499968", "longitude": "127.036376", "continent": "asia_pacific"}},
    "asia-south1": {"name": "India (Mumbai)", "tags": {"latitude": "19.164951", "longitude": "72.851765", "continent": "asia_pacific"}},
    "asia-south2": {"name": "India (Delhi)", "tags": {"latitude": "28.644800", "longitude": "77.216721", "continent": "asia_pacific"}},
    "asia-southeast1": {"name": "Singapore (Jurong West)", "tags": {"latitude": "1.351376", "longitude": "103.709574", "continent": "asia_pacific"}},
    "asia-southeast2": {"name": "Indonesia (Jakarta)", "tags": {"latitude": "-6.227851", "longitude": "106.808169", "continent": "asia_pacific"}},
    "australia-southeast1": {"name": "Australia (Sydney)", "tags": {"latitude": "-33.733694", "longitude": "150.969840", "continent": "asia_pacific"}},
    "australia-southeast2": {"name": "Australia (Melbourne)", "tags": {"latitude": "-37.840935", "longitude": "144.946457", "continent": "asia_pacific"}},
    "europe-north1": {"name": "Finland (Hamina)", "tags": {"latitude": "60.539504", "longitude": "27.113819", "continent": "europe"}},
    "europe-west1": {"name": "Belgium (St.Ghislain)", "tags": {"latitude": "50.471248", "longitude": "3.825493", "continent": "europe"}},
    "europe-west2": {"name": "England, UK (London)", "tags": {"latitude": "51.515998", "longitude": "-0.126918", "continent": "europe"}},
    "europe-west3": {"name": "Germany (Frankfurt)", "tags": {"latitude": "50.115963", "longitude": "8.669625", "continent": "europe"}},
    "europe-west4": {"name": "Netherlands (Eemshaven)", "tags": {"latitude": "53.427625", "longitude": "6.865703", "continent": "europe"}},
    "europe-west6": {"name": "Switzerland (Zürich)", "tags": {"latitude": "47.365663", "longitude": "8.524881", "continent": "europe"}},
    "northamerica-northeast1": {"name": "Canada, Québec (Montréal)", "tags": {"latitude": "45.501926", "longitude": "-73.570086", "continent": "north_america"}},
    "northamerica-northeast2": {"name": "Canada, Ontario (Toronto)", "tags": {"latitude": "50.000000", "longitude": "-85.000000", "continent": "north_america"}},
    "southamerica-east1": {"name": "Brazil, São Paulo (Osasco)", "tags": {"latitude": "43.8345", "longitude": "2.1972", "continent": "south_america"}},
    "southamerica-west1": {"name": "Chile (Santiago)", "tags": {"latitude": "-33.447487", "longitude": "-70.673676", "continent": "south_america"}},
    "us-central1": {"name": "US, Iowa (Council Bluffs)", "tags": {"latitude": "41.221419", "longitude": "-95.862676", "continent": "north_america"}},
    "us-east1": {"name": "US, South Carolina (Moncks Corner)", "tags": {"latitude": "33.203394", "longitude": "-79.986329", "continent": "north_america"}},
    "us-east4": {"name": "US, Northern Virginia (Ashburn)", "tags": {"latitude": "39.021075", "longitude": "-77.463569", "continent": "north_america"}},
    "us-west1": {"name": "US, Oregon (The Dalles)", "tags": {"latitude": "45.631800", "longitude": "-121.200921", "continent": "north_america"}},
    "us-west2": {"name": "US, California (Los Angeles)", "tags": {"latitude": "34.049329", "longitude": "-118.255265", "continent": "north_america"}},
    "us-west3": {"name": "US, Utah (Salt Lake City)", "tags": {"latitude": "40.730109", "longitude": "-111.951386", "continent": "north_america"}},
    "us-west4": {"name": "US, Nevada (Las Vegas)", "tags": {"latitude": "36.092498", "longitude": "-115.086073", "continent": "north_america"}},
    "global": {"name": "Global"}
}


class GoogleCloudManager(BaseManager):
    connector_name = None
    cloud_service_types = []
    response_schema = None
    collected_region_codes = []

    def verify(self, options, secret_data, **kwargs):
        """ Check collector's status.
        """
        connector: GoogleCloudConnector = GoogleCloudConnector(secret_data=secret_data)
        connector.verify()

    def collect_cloud_service_type(self, params):
        options = params.get('options', {})

        for cloud_service_type in self.cloud_service_types:
            _LOGGER.debug(f'cloud_service_type start => {cloud_service_type.resource.service_code}')
            if 'service_code_mappers' in options:
                svc_code_maps = options['service_code_mappers']
                _LOGGER.debug(f'svc_code_maps => {svc_code_maps}')
                _LOGGER.debug(f'service_code temp => {cloud_service_type.resource.service_code}')
                if getattr(cloud_service_type.resource, 'service_code') and \
                        cloud_service_type.resource.service_code in svc_code_maps:
                    cloud_service_type.resource.service_code = svc_code_maps[cloud_service_type.resource.service_code]
                _LOGGER.debug(f'service_code end => {cloud_service_type.resource.service_code}')
            yield cloud_service_type

    def collect_cloud_service(self, params) -> list:
        raise NotImplemented

    def collect_resources(self, params) -> list:
        total_resources = []

        try:
            # Collect Cloud Service Type3wee
            total_resources.extend(self.collect_cloud_service_type(params))

            # Collect Cloud Service
            resources, error_resources = self.collect_cloud_service(params)
            total_resources.extend(resources)
            total_resources.extend(error_resources)

            # Collect Region
            total_resources.extend(self.collect_region())

        except Exception as e:
            _LOGGER.error(f'[collect_resources] {e}', exc_info=True)
            error_resource_response = self.generate_error_response(e, self.cloud_service_types[0].resource.group, self.cloud_service_types[0].resource.name)
            total_resources.append(error_resource_response)

        return total_resources

    def collect_region(self):
        results = []
        for region_code in self.collected_region_codes:
            if region := self.match_region_info(region_code):
                results.append(RegionResponse({'resource': region}))

        return results

    def set_region_code(self, region):
        if region not in REGION_INFO:
            region = 'global'

        if region not in self.collected_region_codes:
            self.collected_region_codes.append(region)

    @staticmethod
    def get_param_in_url(url, key):
        param = ""
        raw_path = urlparse(url).path
        list_path = raw_path.split('/')
        # Google cloud resource representation rules is /{key}/{value}/{key}/{value}
        if key in list_path:
            index_key = list_path.index(key)
            index_value = index_key+1
            param = list_path[index_value]
        return param

    @staticmethod
    def check_is_ipaddress(string_to_check):
        try:
            ip = ipaddress.ip_address(string_to_check)
            return True
        except ValueError:
            return False

    def get_region(self, resource_info):
        if 'region' in resource_info:
            return self.get_param_in_url(resource_info.get('region', ''), 'regions')
        else:
            return 'global'

    @staticmethod
    def generate_error_response(e, cloud_service_group, cloud_service_type):
        if type(e) is dict:
            error_resource_response = ErrorResourceResponse({
                'message': json.dumps(e),
                'resource': {
                    'cloud_service_group': cloud_service_group,
                    'cloud_service_type': cloud_service_type
                }})
        else:
            error_resource_response = ErrorResourceResponse({
                'message': str(e),
                'resource': {
                    'cloud_service_group': cloud_service_group,
                    'cloud_service_type': cloud_service_type
                }})

        return error_resource_response

    @staticmethod
    def generate_resource_error_response(e, cloud_service_group, cloud_service_type, resource_id):
        if type(e) is dict:
            error_resource_response = ErrorResourceResponse({
                'message': json.dumps(e),
                'resource': {
                    'cloud_service_group': cloud_service_group,
                    'cloud_service_type': cloud_service_type,
                    'resource_id': resource_id
                }})
        else:
            error_resource_response = ErrorResourceResponse({
                'message': str(e),
                'resource': {
                    'cloud_service_group': cloud_service_group,
                    'cloud_service_type': cloud_service_type,
                    'resource_id': resource_id
                }})
        return error_resource_response

    @staticmethod
    def match_region_info(region_code):
        match_region_info = REGION_INFO.get(region_code)

        if match_region_info:
            region_info = match_region_info.copy()
            region_info.update({
                'region_code': region_code
            })
            return RegionResource(region_info, strict=False)

        return None

    @staticmethod
    def convert_labels_format(labels):
        convert_labels = []
        for k, v in labels.items():
            convert_labels.append({
                'key': k,
                'value': v
            })
        return convert_labels

    @staticmethod
    def _convert_size(size_bytes):
        if size_bytes == 0:
            return "0 B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

    @staticmethod
    def parse_region_from_zone(zone):
        '''
        EX> zone = 'ap-northeast2-a'
        '''
        parsed_zone = zone.split('-')
        if len(parsed_zone) >= 2:
            return f'{parsed_zone[0]}-{parsed_zone[1]}'

        else:
            return ''

    @staticmethod
    def get_disk_encryption_type(dict_encryption_info):
        encryption_type = 'Google managed'
        if dict_encryption_info:
            if 'kmsKeyName' in dict_encryption_info or 'kmsKeyServiceAccount' in dict_encryption_info:
                encryption_type = 'Customer managed'
            else:
                encryption_type = 'Customer supplied'

        return encryption_type
