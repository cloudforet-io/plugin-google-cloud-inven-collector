import json
import logging
import os
import time

from spaceone.core import utils
from spaceone.core.service import (
    BaseService,
    authentication_handler,
    check_required,
    transaction,
)
from spaceone.inventory.conf.cloud_service_conf import (
    CLOUD_SERVICE_GROUP_MAP,
    FILTER_FORMAT,
    SUPPORTED_FEATURES,
    SUPPORTED_RESOURCE_TYPE,
    SUPPORTED_SCHEDULES,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import (
    BaseResponse,
    log_state_summary,
    reset_state_counters,
)
from spaceone.inventory.libs.schema.cloud_service import (
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
            'VMInstance',
            'FirebaseProjectManager'
            'CloudRunServiceManager',
            'CloudRunJobManager',
            'CloudRunWorkerPoolManager',
            'CloudRunDomainMappingManager'
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
        secret_data = params.get("secret_data", {})
        if secret_data != {}:
            google_manager = GoogleCloudManager()
            google_manager.verify({}, secret_data)

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

        # Project validation을 건너뛰고 바로 매니저 실행으로 진행
        # ProjectConnector 호출로 인한 private key 오류를 회피
        secret_data = params.get("secret_data", {})
        project_id = secret_data.get("project_id", "unknown")
        _LOGGER.debug(f"[collect] project => {project_id}")

        start_time = time.time()

        # State 카운터 초기화
        reset_state_counters()

        _LOGGER.debug("EXECUTOR START: Google Cloud Service")
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

        # Execute manager (순차 처리)
        for execute_manager in self.execute_managers:
            try:
                _manager = self.locator.get_manager(execute_manager)
                for result in _manager.collect_resources(params):
                    yield result.to_primitive()
            except Exception as e:
                _LOGGER.error(
                    f"[collect] failed to yield result from {execute_manager} => {e}",
                    exc_info=True,
                )
                error_resource_response = self.generate_error_response(
                    e, "", "inventory.Error"
                )
                _LOGGER.debug(error_resource_response)
                yield error_resource_response.to_primitive()

        for service in CLOUD_SERVICE_GROUP_MAP.keys():
            for response in self.collect_metrics(service):
                yield response

        # 최종 요약 정보 로깅
        log_state_summary()
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
        """
        개선된 로깅 기능을 사용하여 에러 응답을 생성합니다.

        Args:
            e: 발생한 예외 또는 에러 정보
            cloud_service_group: 클라우드 서비스 그룹
            cloud_service_type: 클라우드 서비스 타입

        Returns:
            ErrorResourceResponse 인스턴스
        """
        if type(e) is dict:
            error_message = json.dumps(e)
            error_code = "DICT_ERROR"
        else:
            error_message = str(e)
            error_code = type(e).__name__

        # 추가 컨텍스트 정보
        additional_context = {
            "cloud_service_group": cloud_service_group,
            "cloud_service_type": cloud_service_type,
        }

        # 로깅과 함께 에러 응답 생성
        error_resource_response = ErrorResourceResponse.create_with_logging(
            error_message=error_message,
            error_code=error_code,
            additional_data=additional_context,
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
        """
        Namespace 또는 Metric 응답을 생성하고 상태를 로깅합니다.

        Args:
            metric: 메트릭 데이터
            namespace: 네임스페이스 데이터
            resource_type: 리소스 타입

        Returns:
            응답 딕셔너리
        """
        # SUCCESS state 카운터 업데이트 (로깅은 하지 않음)
        import spaceone.inventory.libs.schema.base as base_schema

        base_schema._STATE_COUNTERS["SUCCESS"] += 1

        # 기존 방식으로 응답 생성 (스키마 검증 오류 방지)
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

    @staticmethod
    def handle_error_with_logging(
        error: Exception,
        operation: str = "",
        resource_type: str = "inventory.ErrorResource",
        additional_context: dict = None,
    ) -> dict:
        """
        예외를 처리하고 적절한 상태 로깅과 함께 에러 응답을 생성합니다.

        Args:
            error: 발생한 예외
            operation: 실행 중이던 작업명
            resource_type: 리소스 타입
            additional_context: 추가 컨텍스트 정보

        Returns:
            에러 응답 딕셔너리
        """
        error_message = str(error)
        error_type = type(error).__name__

        # 에러 종류별 state 결정
        if "timeout" in error_message.lower() or error_type in [
            "TimeoutError",
            "ConnectTimeout",
        ]:
            # TIMEOUT 상태로 로깅
            timeout_response = BaseResponse.create_with_logging(
                state="TIMEOUT",
                resource_type=resource_type,
                message=f"Timeout during {operation}: {error_message}",
            )
            return timeout_response.to_primitive()
        else:
            # FAILURE 상태로 로깅
            error_response = ErrorResourceResponse.create_with_logging(
                error_message=f"Error during {operation}: {error_message}",
                error_code=error_type,
                resource_type=resource_type,
                additional_data=additional_context,
            )
            return error_response.to_primitive()

    @transaction
    @check_required(["options", "secret_data"])
    def get_firebase_projects(self, params):
        """
        특정 프로젝트의 Firebase 앱들을 조회합니다.
        Firebase Management API의 searchApps 엔드포인트를 사용합니다.

        Args:
            params:
                - options
                - secret_data

        Returns:
            dict: Firebase 앱 목록
        """
        try:
            from spaceone.inventory.connector.firebase.project import (
                FirebaseProjectConnector,
            )

            firebase_conn = FirebaseProjectConnector(**params)
            firebase_apps = firebase_conn.list_firebase_apps()

            return {
                "apps": firebase_apps,
                "total_count": len(firebase_apps),
                "project_id": params["secret_data"]["project_id"],
            }

        except Exception as e:
            _LOGGER.error(f"Failed to get Firebase apps: {e}")
            raise e
