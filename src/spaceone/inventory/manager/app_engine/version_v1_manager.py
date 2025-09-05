import logging
from typing import List, Dict, Any, Tuple

from spaceone.inventory.connector.app_engine.version_v1 import (
    AppEngineVersionV1Connector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager

from spaceone.inventory.model.app_engine.version.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)

from spaceone.inventory.model.app_engine.version.cloud_service import (
    AppEngineVersionResource,
    AppEngineVersionResponse,
)
from spaceone.inventory.model.app_engine.version.data import (
    AppEngineVersion,
)
from spaceone.inventory.model.kubernetes_engine.cluster.data import convert_datetime
from spaceone.inventory.libs.schema.cloud_service import ErrorResourceResponse

_LOGGER = logging.getLogger(__name__)


class AppEngineVersionV1Manager(GoogleCloudManager):
    connector_name = "AppEngineVersionV1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    cloud_service_group = "AppEngine"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_versions(
        self, service_id: str, params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """AppEngine 버전 목록을 조회합니다 (v1 API).

        Args:
            service_id: 서비스 ID.
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            App Engine 버전 목록.

        Raises:
            Exception: App Engine API 호출 중 오류 발생 시.
        """
        version_connector: AppEngineVersionV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            versions = version_connector.list_versions(service_id)
            _LOGGER.info(
                f"Found {len(versions)} versions for service {service_id} (v1)"
            )
            return versions
        except Exception as e:
            _LOGGER.error(f"Failed to list versions for service {service_id} (v1): {e}")
            return []

    def get_version(
        self, service_id: str, version_id: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """특정 AppEngine 버전 정보를 조회합니다 (v1 API).

        Args:
            service_id: 서비스 ID.
            version_id: 버전 ID.
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            App Engine 버전 정보 딕셔너리.

        Raises:
            Exception: App Engine API 호출 중 오류 발생 시.
        """
        version_connector: AppEngineVersionV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            version = version_connector.get_version(service_id, version_id)
            if version:
                _LOGGER.info(f"Retrieved version {version_id} (v1)")
            return version or {}
        except Exception as e:
            _LOGGER.error(f"Failed to get version {version_id} (v1): {e}")
            return {}

    def list_instances(
        self, service_id: str, version_id: str, params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """특정 버전의 인스턴스 목록을 조회합니다 (v1 API).

        Args:
            service_id: 서비스 ID.
            version_id: 버전 ID.
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            인스턴스 목록.

        Raises:
            Exception: App Engine API 호출 중 오류 발생 시.
        """
        version_connector: AppEngineVersionV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            instances = version_connector.list_instances(service_id, version_id)
            _LOGGER.info(
                f"Found {len(instances)} instances for version {version_id} (v1)"
            )
            return instances
        except Exception as e:
            _LOGGER.error(
                f"Failed to list instances for version {version_id} (v1): {e}"
            )
            return []

    def get_version_metrics(
        self, service_id: str, version_id: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """AppEngine 버전 메트릭을 조회합니다 (v1 API).

        Args:
            service_id: 서비스 ID.
            version_id: 버전 ID.
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            버전 메트릭 정보 딕셔너리.

        Raises:
            Exception: App Engine API 호출 중 오류 발생 시.
        """
        version_connector: AppEngineVersionV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            metrics = version_connector.get_version_metrics(service_id, version_id)
            return metrics or {}
        except Exception as e:
            _LOGGER.error(f"Failed to get metrics for version {version_id} (v1): {e}")
            return {}

    def collect_cloud_service(
        self, params: Dict[str, Any]
    ) -> Tuple[List[Any], List[ErrorResourceResponse]]:
        """AppEngine 버전 정보를 수집합니다 (v1 API).

        Args:
            params: 수집에 필요한 파라미터 딕셔너리.

        Returns:
            수집된 클라우드 서비스 목록과 오류 응답 목록의 튜플.

        Raises:
            Exception: 데이터 수집 중 오류 발생 시.
        """
        _LOGGER.debug("** AppEngine Version V1 START **")

        collected_cloud_services = []
        error_responses = []

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        # 먼저 서비스 목록을 조회하여 각 서비스의 버전을 수집
        from spaceone.inventory.connector.app_engine.application_v1 import (
            AppEngineApplicationV1Connector,
        )

        app_connector = AppEngineApplicationV1Connector(secret_data=secret_data)

        services = app_connector.list_services()

        for service in services:
            service_id = service.get("id")
            if not service_id:
                continue

            # 각 서비스의 버전 목록 조회
            versions = self.list_versions(service_id, params)

            for version in versions:
                try:
                    version_id = version.get("id")

                    # 인스턴스 목록 조회
                    instances = []
                    if version_id:
                        instances = self.list_instances(service_id, version_id, params)

                    # 메트릭 정보 조회
                    metrics = {}
                    if version_id:
                        metrics = self.get_version_metrics(
                            service_id, version_id, params
                        )

                    # 기본 버전 데이터 준비
                    version_data = {
                        "name": str(version.get("name", "")),
                        "projectId": str(version.get("projectId", "")),
                        "serviceId": str(service_id),
                        "id": str(version.get("id", "")),
                        "servingStatus": str(version.get("servingStatus", "")),
                        "runtime": str(version.get("runtime", "")),
                        "environment": str(version.get("environment", "")),
                        "createTime": convert_datetime(version.get("createTime")),
                        "updateTime": convert_datetime(version.get("updateTime")),
                        "instance_count": str(len(instances)),
                        "memory_usage": str(metrics.get("memory_usage", 0)),
                        "cpu_usage": str(metrics.get("cpu_usage", 0)),
                    }

                    # Automatic Scaling 추가
                    if "automaticScaling" in version:
                        auto_scaling = version["automaticScaling"]
                        version_data["automaticScaling"] = {
                            "coolDownPeriod": str(
                                auto_scaling.get("coolDownPeriod", "")
                            ),
                            "cpuUtilization": auto_scaling.get("cpuUtilization", {}),
                            "maxConcurrentRequests": auto_scaling.get(
                                "maxConcurrentRequests"
                            ),
                            "maxIdleInstances": auto_scaling.get("maxIdleInstances"),
                            "maxTotalInstances": auto_scaling.get("maxTotalInstances"),
                            "minIdleInstances": auto_scaling.get("minIdleInstances"),
                            "minTotalInstances": auto_scaling.get("minTotalInstances"),
                        }

                    # Manual Scaling 추가
                    if "manualScaling" in version:
                        manual_scaling = version["manualScaling"]
                        version_data["manualScaling"] = {
                            "instances": manual_scaling.get("instances"),
                        }

                    # Basic Scaling 추가
                    if "basicScaling" in version:
                        basic_scaling = version["basicScaling"]
                        version_data["basicScaling"] = {
                            "idleTimeout": str(basic_scaling.get("idleTimeout", "")),
                            "maxInstances": basic_scaling.get("maxInstances"),
                        }

                    # Resources 추가
                    if "resources" in version:
                        resources = version["resources"]
                        version_data["resources"] = {
                            "cpu": resources.get("cpu"),
                            "diskGb": resources.get("diskGb"),
                            "memoryGb": resources.get("memoryGb"),
                            "volumes": resources.get("volumes", []),
                        }

                    # AppEngineVersion 모델 생성
                    app_engine_version_data = AppEngineVersion(
                        version_data, strict=False
                    )

                    # AppEngineVersionResource 생성
                    version_resource = AppEngineVersionResource(
                        {
                            "name": version_data.get("name"),
                            "data": app_engine_version_data,
                            "reference": {
                                "resource_id": version.get("id"),
                                "external_link": f"https://console.cloud.google.com/appengine/versions?project={project_id}&serviceId={service_id}",
                            },
                            "region_code": "global",  # App Engine은 global 리소스
                            "account": version_data.get("projectId"),
                        }
                    )

                    ##################################
                    # 4. Make Collected Region Code
                    ##################################
                    self.set_region_code("global")

                    # AppEngineVersionResponse 생성
                    version_response = AppEngineVersionResponse(
                        {"resource": version_resource}
                    )

                    collected_cloud_services.append(version_response)

                except Exception as e:
                    _LOGGER.error(f"[collect_cloud_service] => {e}", exc_info=True)
                    error_responses.append(
                        self.generate_error_response(
                            e, self.cloud_service_group, "Version"
                        )
                    )

        _LOGGER.debug("** AppEngine Version V1 END **")
        return collected_cloud_services, error_responses
