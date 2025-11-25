import concurrent.futures
import json
import logging
import os
import time

from spaceone.core import utils
from spaceone.core.service import *
from spaceone.inventory.conf.cloud_service_conf import *
from spaceone.inventory.connector.resource_manager.project import ProjectConnector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceResponse,
    ErrorResourceResponse,
)

_LOGGER = logging.getLogger(__name__)

_CURRENT_DIR = os.path.dirname(__file__)
_BEFORE_CURRENT_DIR, _ = _CURRENT_DIR.rsplit("/", 1)
_METRIC_DIR = os.path.join(_BEFORE_CURRENT_DIR, "metrics/")


@authentication_handler
class CollectorService(BaseService):
    def __init__(self, metadata):
        super().__init__(metadata)
        # set google cloud service manager
        self.execute_managers = []
        """
        self.execute_managers = [
            'SQLWorkspaceManager',
            'CloudSQLManager',
            'InstanceGroupManager',
            'InstanceTemplateManager',
            'MachineImageManager',
            'DiskManager',
            'SnapshotManager',
            'StorageManager',
            'VPCNetworkManager',
            'ExternalIPAddressManager',
            'FirewallManager',
            'RouteManager',
            'LoadBalancingManager',
            'VMInstance'
        ]
        """

    @check_required(["options"])
    def init(self, params):
        """init plugin by options"""
        capability = {
            "filter_format": FILTER_FORMAT,
            "supported_resource_type": SUPPORTED_RESOURCE_TYPE,
            "supported_features": SUPPORTED_FEATURES,
            "supported_schedules": SUPPORTED_SCHEDULES,
        }
        return {"metadata": capability}

    @transaction
    @check_required(["options", "secret_data"])
    def verify(self, params):
        """
        Args:
              params:
                - options
                - secret_data
        """
        options = params["options"]
        secret_data = params.get("secret_data", {})
        if secret_data != {}:
            google_manager = GoogleCloudManager()
            active = google_manager.verify({}, secret_data)

        return {}

    @transaction
    @check_required(["options", "secret_data", "filter"])
    def collect(self, params):
        """
        Args:
            params:
                - options
                - schema
                - secret_data
                - filter
        """

        project_conn = self.locator.get_connector(ProjectConnector, **params)
        try:
            # _LOGGER.debug(f"[collect] project => {project_id} / {project_state}")
            project_info = project_conn.get_project_info()
            project_id = project_info["projectId"]
            project_state = project_info["state"]
        except Exception as e:
            _LOGGER.debug(f"[collect] failed to get project_info => {e}")
            return CloudServiceResponse().to_primitive()

        start_time = time.time()

        _LOGGER.debug("EXECUTOR START: Google Cloud Service")
        proxy_env = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
        if proxy_env:
            _LOGGER.debug(
                f"** Using proxy in environment variable HTTPS_PROXY/https_proxy: {proxy_env}"
            )  # src/spaceone/inventory/libs/connector.py _create_http_client
        # Get target manager to collect
        try:
            self.execute_managers = self._get_target_execute_manager(
                params.get("options", {})
            )
            _LOGGER.debug(msg=f"[collect] execute_managers => {self.execute_managers}")
        except Exception as e:
            _LOGGER.error(
                f"[collect] failed to get target execute_managers => {e}", exc_info=True
            )
            error_resource_response = self.generate_error_response(
                e, "", "inventory.Error"
            )
            yield error_resource_response.to_primitive()

        # Execute manager
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKER) as executor:
            future_executors = []
            for execute_manager in self.execute_managers:
                _manager = self.locator.get_manager(execute_manager)
                future_executors.append(
                    executor.submit(_manager.collect_resources, params)
                )

            for future in concurrent.futures.as_completed(future_executors):
                try:
                    for result in future.result():
                        yield result.to_primitive()
                except Exception as e:
                    _LOGGER.error(
                        f"[collect] failed to yield result => {e}", exc_info=True
                    )
                    error_resource_response = self.generate_error_response(
                        e, "", "inventory.Error"
                    )
                    _LOGGER.debug(error_resource_response)
                    yield error_resource_response.to_primitive()

        for service in CLOUD_SERVICE_GROUP_MAP.keys():
            for response in self.collect_metrics(service):
                yield response

        _LOGGER.debug(f"TOTAL TIME : {time.time() - start_time} Seconds")

    def _get_target_execute_manager(self, options):
        if "cloud_service_types" in options:
            execute_managers = self._cloud_service_groups_to_types(
                options["cloud_service_types"]
            )
        else:
            execute_managers = self._cloud_service_groups_to_types(
                CLOUD_SERVICE_GROUP_MAP.keys()
            )

        return execute_managers

    @staticmethod
    def _cloud_service_groups_to_types(cloud_service_groups) -> list:
        cloud_service_types = []
        for cloud_service_group in cloud_service_groups:
            if cloud_service_group in CLOUD_SERVICE_GROUP_MAP:
                cloud_service_types.extend(CLOUD_SERVICE_GROUP_MAP[cloud_service_group])

        return cloud_service_types

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

    def collect_metrics(self, service: str) -> dict:
        for dirname in os.listdir(os.path.join(_METRIC_DIR, service)):
            full_path = os.path.join(_METRIC_DIR, service, dirname)
            if not os.path.isdir(full_path):
                continue
            for filename in os.listdir(os.path.join(_METRIC_DIR, service, dirname)):
                if filename.endswith(".yaml"):
                    file_path = os.path.join(_METRIC_DIR, service, dirname, filename)
                    info = utils.load_yaml_from_file(file_path)
                    if filename == "namespace.yaml":
                        yield self.make_namespace_or_metric_response(
                            namespace=info,
                            resource_type="inventory.Namespace",
                        )
                    else:
                        yield self.make_namespace_or_metric_response(
                            metric=info,
                            resource_type="inventory.Metric",
                        )

    @staticmethod
    def make_namespace_or_metric_response(
        metric=None,
        namespace=None,
        resource_type: str = "inventory.Metric",
    ) -> dict:
        response = {
            "state": "SUCCESS",
            "resource_type": resource_type,
            "match_rules": {},
        }

        if resource_type == "inventory.Metric" and metric is not None:
            response["resource"] = metric
        elif resource_type == "inventory.Namespace" and namespace is not None:
            response["resource"] = namespace

        return response
