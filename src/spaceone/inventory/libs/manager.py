import ipaddress
import json
import logging
import math
from urllib.parse import urlparse

from googleapiclient.errors import HttpError

from spaceone.core.manager import BaseManager
from spaceone.inventory.conf.cloud_service_conf import (
    CLOUD_LOGGING_RESOURCE_TYPE_MAP,
    REGION_INFO,
)
from spaceone.inventory.libs.connector import GoogleCloudConnector
from spaceone.inventory.libs.schema.cloud_service import (
    ErrorResourceResponse,
)
from spaceone.inventory.libs.schema.region import RegionResource, RegionResponse

_LOGGER = logging.getLogger(__name__)


class GoogleCloudManager(BaseManager):
    connector_name = None
    cloud_service_types = []
    response_schema = None
    collected_region_codes = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def verify(self, options, secret_data, **kwargs):
        """Check collector's status."""
        connector: GoogleCloudConnector = GoogleCloudConnector(secret_data=secret_data)
        connector.verify()

    def collect_cloud_service_type(self, params):
        options = params.get("options", {})

        for cloud_service_type in self.cloud_service_types:
            if "service_code_mappers" in options:
                svc_code_maps = options["service_code_mappers"]
                if (
                    getattr(cloud_service_type.resource, "service_code")
                    and cloud_service_type.resource.service_code in svc_code_maps
                ):
                    cloud_service_type.resource.service_code = svc_code_maps[
                        cloud_service_type.resource.service_code
                    ]

            if "custom_asset_url" in options:
                _tags = cloud_service_type.resource.tags

                if "spaceone:icon" in _tags:
                    _icon = _tags["spaceone:icon"]
                    _tags["spaceone:icon"] = (
                        f"{options['custom_asset_url']}/{_icon.split('/')[-1]}"
                    )

            yield cloud_service_type

    def collect_cloud_service(self, params) -> list:
        raise NotImplementedError

    def collect_resources(self, params) -> list:
        total_resources = []

        try:
            # Collect Cloud Service Type
            total_resources.extend(self.collect_cloud_service_type(params))

            # Collect Cloud Service
            resources, error_resources = self.collect_cloud_service(params)
            total_resources.extend(resources)
            total_resources.extend(error_resources)

            # Collect Region
            total_resources.extend(self.collect_region())

        except Exception as e:
            if isinstance(e, HttpError) and e.status_code == 403:
                if (
                    len(e.error_details) == 1
                    and e.error_details[0].get("reason") == "accessNotConfigured"
                ):
                    _LOGGER.error(f"[collect_resources] SKIP Disabled Service {e}")
                    pass
                elif (
                    len(e.error_details) == 2
                    and e.error_details[1].get("reason") == "SERVICE_DISABLED"
                ):
                    _LOGGER.error(f"[collect_resources] SKIP Disabled Service {e}")
                    pass
                else:
                    _LOGGER.error(f"[collect_resources] {e}", exc_info=True)
                    error_resource_response = self.generate_error_response(
                        e,
                        self.cloud_service_types[0].resource.group,
                        self.cloud_service_types[0].resource.name,
                    )

                    total_resources.append(error_resource_response)
            elif isinstance(e, HttpError) and e.status_code == 400:
                if (
                    len(e.error_details) == 1
                    and e.error_details[0].get("reason") == "invalid"
                    and self.cloud_service_types[0].resource.group == "BigQuery"
                ):
                    _LOGGER.error(f"[collect_resources] SKIP Disabled Service {e}")
                    pass
                elif (
                    len(e.error_details) == 2
                    and e.error_details[1].get("reason") == "invalid"
                    and self.cloud_service_types[0].resource.group == "BigQuery"
                ):
                    _LOGGER.error(f"[collect_resources] SKIP Disabled Service {e}")
                    pass
                else:
                    _LOGGER.error(f"[collect_resources] {e}", exc_info=True)
                    error_resource_response = self.generate_error_response(
                        e,
                        self.cloud_service_types[0].resource.group,
                        self.cloud_service_types[0].resource.name,
                    )

                    total_resources.append(error_resource_response)

            else:
                _LOGGER.error(f"[collect_resources] {e}", exc_info=True)
                error_resource_response = self.generate_error_response(
                    e,
                    self.cloud_service_types[0].resource.group,
                    self.cloud_service_types[0].resource.name,
                )

                total_resources.append(error_resource_response)

        return total_resources

    def collect_region(self):
        results = []
        for region_code in self.collected_region_codes:
            if region := self.match_region_info(region_code):
                results.append(RegionResponse({"resource": region}))

        return results

    def set_region_code(self, region):
        if region not in REGION_INFO:
            region = "global"

        if region not in self.collected_region_codes:
            self.collected_region_codes.append(region)

    @staticmethod
    def set_google_cloud_monitoring(project_id, metric_type, resource_id, filters):
        # Support legacy method (single metric_type)
        if isinstance(metric_type, str):
            return {
                "name": f"projects/{project_id}",
                "resource_id": resource_id,
                "filters": [{"metric_type": metric_type, "labels": filters}],
            }

        # Support new method (multiple metric_types)
        if isinstance(metric_type, list):
            monitoring_filters = []
            for i, mt in enumerate(metric_type):
                # Use corresponding index if filters is nested list, otherwise use same filters
                if isinstance(filters[0], list) and len(filters) > i:
                    filter_labels = filters[i]
                else:
                    filter_labels = filters

                monitoring_filters.append({"metric_type": mt, "labels": filter_labels})

            return {
                "name": f"projects/{project_id}",
                "resource_id": resource_id,
                "filters": monitoring_filters,
            }

        # Return default for exceptional cases
        return {
            "name": f"projects/{project_id}",
            "resource_id": resource_id,
            "filters": [],
        }

    @staticmethod
    def set_google_cloud_logging(service, cloud_service_type, project_id, resource_id):
        cloud_logging_info = CLOUD_LOGGING_RESOURCE_TYPE_MAP[service][
            cloud_service_type
        ]
        resource_type = cloud_logging_info.get("resource_type", [])
        labels_key = cloud_logging_info.get("labels_key", [])
        return {
            "name": f"projects/{project_id}",
            "resource_id": resource_id,
            "filters": [
                {
                    "resource_type": resource_type,
                    "labels": [{"key": labels_key, "value": resource_id}],
                }
            ],
        }

    @staticmethod
    def get_param_in_url(url, key):
        param = ""
        raw_path = urlparse(url).path
        list_path = raw_path.split("/")
        # Google cloud resource representation rules is /{key}/{value}/{key}/{value}
        if key in list_path:
            index_key = list_path.index(key)
            index_value = index_key + 1
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
        if "region" in resource_info:
            return self.get_param_in_url(resource_info.get("region", ""), "regions")
        else:
            return "global"

    @staticmethod
    def generate_error_response(e, cloud_service_group, cloud_service_type):
        if type(e) is dict:
            error_resource_response = ErrorResourceResponse(
                {
                    "message": json.dumps(e),
                    "resource": {
                        "cloud_service_group": cloud_service_group,
                        "cloud_service_type": cloud_service_type,
                    },
                }
            )
        else:
            error_resource_response = ErrorResourceResponse(
                {
                    "message": str(e),
                    "resource": {
                        "cloud_service_group": cloud_service_group,
                        "cloud_service_type": cloud_service_type,
                    },
                }
            )

        return error_resource_response

    @staticmethod
    def generate_resource_error_response(
        e, cloud_service_group, cloud_service_type, resource_id
    ):
        if type(e) is dict:
            error_resource_response = ErrorResourceResponse(
                {
                    "message": json.dumps(e),
                    "resource": {
                        "cloud_service_group": cloud_service_group,
                        "cloud_service_type": cloud_service_type,
                        "resource_id": resource_id,
                    },
                }
            )
        else:
            error_resource_response = ErrorResourceResponse(
                {
                    "message": str(e),
                    "resource": {
                        "cloud_service_group": cloud_service_group,
                        "cloud_service_type": cloud_service_type,
                        "resource_id": resource_id,
                    },
                }
            )
        return error_resource_response

    @staticmethod
    def match_region_info(region_code):
        match_region_info = REGION_INFO.get(region_code)

        if match_region_info:
            region_info = match_region_info.copy()
            region_info.update({"region_code": region_code})
            return RegionResource(region_info, strict=False)

        return None

    @staticmethod
    def convert_labels_format(labels):
        convert_labels = []
        for k, v in labels.items():
            convert_labels.append({"key": k, "value": v})
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
        """
        EX> zone = 'ap-northeast2-a'
        """
        parsed_zone = zone.split("-")
        if len(parsed_zone) >= 2:
            return f"{parsed_zone[0]}-{parsed_zone[1]}"

        else:
            return ""

    @staticmethod
    def get_disk_encryption_type(dict_encryption_info):
        encryption_type = "Google managed"
        if dict_encryption_info:
            if (
                "kmsKeyName" in dict_encryption_info
                or "kmsKeyServiceAccount" in dict_encryption_info
            ):
                encryption_type = "Customer managed"
            else:
                encryption_type = "Customer supplied"

        return encryption_type
