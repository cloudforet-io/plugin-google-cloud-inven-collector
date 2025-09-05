import logging
from typing import List, Dict, Any, Tuple

from spaceone.inventory.connector.app_engine.service_v1 import (
    AppEngineServiceV1Connector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager

from spaceone.inventory.model.app_engine.service.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)

from spaceone.inventory.model.app_engine.service.cloud_service import (
    AppEngineServiceResource,
    AppEngineServiceResponse,
)
from spaceone.inventory.model.app_engine.service.data import (
    AppEngineService,
)
from spaceone.inventory.model.kubernetes_engine.cluster.data import convert_datetime
from spaceone.inventory.libs.schema.cloud_service import ErrorResourceResponse

_LOGGER = logging.getLogger(__name__)


class AppEngineServiceV1Manager(GoogleCloudManager):
    connector_name = "AppEngineServiceV1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    cloud_service_group = "AppEngine"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_services(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """AppEngine 서비스 목록을 조회합니다 (v1 API).

        Args:
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            App Engine 서비스 목록.

        Raises:
            Exception: App Engine API 호출 중 오류 발생 시.
        """
        service_connector: AppEngineServiceV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            services = service_connector.list_services()
            _LOGGER.info(f"Found {len(services)} AppEngine services (v1)")
            return services
        except Exception as e:
            _LOGGER.error(f"Failed to list AppEngine services (v1): {e}")
            return []

    def get_service(self, service_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """특정 AppEngine 서비스 정보를 조회합니다 (v1 API).

        Args:
            service_id: 서비스 ID.
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            App Engine 서비스 정보 딕셔너리.

        Raises:
            Exception: App Engine API 호출 중 오류 발생 시.
        """
        service_connector: AppEngineServiceV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            service = service_connector.get_service(service_id)
            if service:
                _LOGGER.info(f"Retrieved service {service_id} (v1)")
            return service or {}
        except Exception as e:
            _LOGGER.error(f"Failed to get service {service_id} (v1): {e}")
            return {}

    def list_versions(
        self, service_id: str, params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """특정 서비스의 버전 목록을 조회합니다 (v1 API).

        Args:
            service_id: 서비스 ID.
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            서비스 버전 목록.

        Raises:
            Exception: App Engine API 호출 중 오류 발생 시.
        """
        service_connector: AppEngineServiceV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            versions = service_connector.list_versions(service_id)
            _LOGGER.info(
                f"Found {len(versions)} versions for service {service_id} (v1)"
            )
            return versions
        except Exception as e:
            _LOGGER.error(f"Failed to list versions for service {service_id} (v1): {e}")
            return []

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
        service_connector: AppEngineServiceV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            instances = service_connector.list_instances(service_id, version_id)
            _LOGGER.info(
                f"Found {len(instances)} instances for version {version_id} (v1)"
            )
            return instances
        except Exception as e:
            _LOGGER.error(
                f"Failed to list instances for version {version_id} (v1): {e}"
            )
            return []

    def collect_cloud_service(
        self, params: Dict[str, Any]
    ) -> Tuple[List[Any], List[ErrorResourceResponse]]:
        """AppEngine 서비스 정보를 수집합니다 (v1 API).

        Args:
            params: 수집에 필요한 파라미터 딕셔너리.

        Returns:
            수집된 클라우드 서비스 목록과 오류 응답 목록의 튜플.

        Raises:
            Exception: 데이터 수집 중 오류 발생 시.
        """
        _LOGGER.debug("** AppEngine Service V1 START **")

        collected_cloud_services = []
        error_responses = []

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        # App Engine 서비스 목록 조회
        services = self.list_services(params)

        for service in services:
            try:
                service_id = service.get("id")

                # 버전 목록 조회
                versions = []
                if service_id:
                    versions = self.list_versions(service_id, params)

                # 인스턴스 정보 수집
                total_instances = 0
                for version in versions:
                    version_id = version.get("id")
                    if version_id:
                        instances = self.list_instances(service_id, version_id, params)
                        total_instances += len(instances)

                # 기본 서비스 데이터 준비
                service_data = {
                    "name": str(service.get("name", "")),
                    "projectId": str(service.get("projectId", "")),
                    "id": str(service.get("id", "")),
                    "servingStatus": str(service.get("servingStatus", "")),
                    "createTime": convert_datetime(service.get("createTime")),
                    "updateTime": convert_datetime(service.get("updateTime")),
                    "version_count": str(len(versions)),
                    "instance_count": str(total_instances),
                }

                # Traffic Split 추가
                if "split" in service:
                    split_data = service["split"]
                    service_data["split"] = {
                        "allocations": split_data.get("allocations", {}),
                        "shardBy": str(split_data.get("shardBy", "")),
                    }

                # Network Settings 추가
                if "network" in service:
                    network_data = service["network"]
                    service_data["network"] = {
                        "forwardedPorts": str(network_data.get("forwardedPorts", "")),
                        "instanceTag": str(network_data.get("instanceTag", "")),
                        "name": str(network_data.get("name", "")),
                        "subnetworkName": str(network_data.get("subnetworkName", "")),
                    }

                # AppEngineService 모델 생성
                app_engine_service_data = AppEngineService(service_data, strict=False)

                # AppEngineServiceResource 생성
                service_resource = AppEngineServiceResource(
                    {
                        "name": service_data.get("name"),
                        "data": app_engine_service_data,
                        "reference": {
                            "resource_id": service.get("id"),
                            "external_link": f"https://console.cloud.google.com/appengine/services?project={project_id}",
                        },
                        "region_code": "global",  # App Engine은 global 리소스
                        "account": service_data.get("projectId"),
                    }
                )

                ##################################
                # 4. Make Collected Region Code
                ##################################
                self.set_region_code("global")

                # AppEngineServiceResponse 생성
                service_response = AppEngineServiceResponse(
                    {"resource": service_resource}
                )

                collected_cloud_services.append(service_response)

            except Exception as e:
                _LOGGER.error(f"[collect_cloud_service] => {e}", exc_info=True)
                error_responses.append(
                    self.generate_error_response(e, self.cloud_service_group, "Service")
                )

        _LOGGER.debug("** AppEngine Service V1 END **")
        return collected_cloud_services, error_responses
