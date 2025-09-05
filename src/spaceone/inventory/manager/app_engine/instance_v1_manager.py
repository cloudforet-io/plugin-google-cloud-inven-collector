import logging
from typing import List, Dict, Any, Tuple

from spaceone.inventory.connector.app_engine.instance_v1 import (
    AppEngineInstanceV1Connector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager

from spaceone.inventory.model.app_engine.instance.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)

from spaceone.inventory.model.app_engine.instance.cloud_service import (
    AppEngineInstanceResource,
    AppEngineInstanceResponse,
)
from spaceone.inventory.model.app_engine.instance.data import (
    AppEngineInstance,
)
from spaceone.inventory.model.kubernetes_engine.cluster.data import convert_datetime
from spaceone.inventory.libs.schema.cloud_service import ErrorResourceResponse

_LOGGER = logging.getLogger(__name__)


class AppEngineInstanceV1Manager(GoogleCloudManager):
    connector_name = "AppEngineInstanceV1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    cloud_service_group = "AppEngine"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_instances(
        self, service_id: str, version_id: str, params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """AppEngine 인스턴스 목록을 조회합니다 (v1 API).

        Args:
            service_id: 서비스 ID.
            version_id: 버전 ID.
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            App Engine 인스턴스 목록.

        Raises:
            Exception: App Engine API 호출 중 오류 발생 시.
        """
        instance_connector: AppEngineInstanceV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            instances = instance_connector.list_instances(service_id, version_id)
            _LOGGER.info(
                f"Found {len(instances)} instances for version {version_id} (v1)"
            )
            return instances
        except Exception as e:
            _LOGGER.error(
                f"Failed to list instances for version {version_id} (v1): {e}"
            )
            return []

    def get_instance(
        self, service_id: str, version_id: str, instance_id: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """특정 AppEngine 인스턴스 정보를 조회합니다 (v1 API).

        Args:
            service_id: 서비스 ID.
            version_id: 버전 ID.
            instance_id: 인스턴스 ID.
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            App Engine 인스턴스 정보 딕셔너리.

        Raises:
            Exception: App Engine API 호출 중 오류 발생 시.
        """
        instance_connector: AppEngineInstanceV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            instance = instance_connector.get_instance(
                service_id, version_id, instance_id
            )
            if instance:
                _LOGGER.info(f"Retrieved instance {instance_id} (v1)")
            return instance or {}
        except Exception as e:
            _LOGGER.error(f"Failed to get instance {instance_id} (v1): {e}")
            return {}

    def list_all_instances(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """모든 AppEngine 인스턴스를 조회합니다 (v1 API).

        Args:
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            모든 App Engine 인스턴스 목록.

        Raises:
            Exception: App Engine API 호출 중 오류 발생 시.
        """
        instance_connector: AppEngineInstanceV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            instances = instance_connector.list_all_instances()
            _LOGGER.info(f"Found {len(instances)} total AppEngine instances (v1)")
            return instances
        except Exception as e:
            _LOGGER.error(f"Failed to list all AppEngine instances (v1): {e}")
            return []

    def get_instance_metrics(
        self, service_id: str, version_id: str, instance_id: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """AppEngine 인스턴스 메트릭을 조회합니다 (v1 API).

        Args:
            service_id: 서비스 ID.
            version_id: 버전 ID.
            instance_id: 인스턴스 ID.
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            인스턴스 메트릭 정보 딕셔너리.

        Raises:
            Exception: App Engine API 호출 중 오류 발생 시.
        """
        instance_connector: AppEngineInstanceV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            metrics = instance_connector.get_instance_metrics(
                service_id, version_id, instance_id
            )
            return metrics or {}
        except Exception as e:
            _LOGGER.error(f"Failed to get metrics for instance {instance_id} (v1): {e}")
            return {}

    def get_instance_details(
        self, service_id: str, version_id: str, instance_id: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """AppEngine 인스턴스 상세 정보를 조회합니다 (v1 API).

        Args:
            service_id: 서비스 ID.
            version_id: 버전 ID.
            instance_id: 인스턴스 ID.
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            인스턴스 상세 정보 딕셔너리.

        Raises:
            Exception: App Engine API 호출 중 오류 발생 시.
        """
        instance_connector: AppEngineInstanceV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            details = instance_connector.get_instance_details(
                service_id, version_id, instance_id
            )
            return details or {}
        except Exception as e:
            _LOGGER.error(f"Failed to get details for instance {instance_id} (v1): {e}")
            return {}

    def collect_cloud_service(
        self, params: Dict[str, Any]
    ) -> Tuple[List[Any], List[ErrorResourceResponse]]:
        """AppEngine 인스턴스 정보를 수집합니다 (v1 API).

        Args:
            params: 수집에 필요한 파라미터 딕셔너리.

        Returns:
            수집된 클라우드 서비스 목록과 오류 응답 목록의 튜플.

        Raises:
            Exception: 데이터 수집 중 오류 발생 시.
        """
        _LOGGER.debug("** AppEngine Instance V1 START **")

        collected_cloud_services = []
        error_responses = []

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        # 모든 인스턴스를 조회
        instances = self.list_all_instances(params)

        for instance in instances:
            try:
                service_id = instance.get("service_id")
                version_id = instance.get("version_id")
                instance_id = instance.get("id")

                if not all([service_id, version_id, instance_id]):
                    continue

                # 인스턴스 상세 정보 조회 (향후 사용 예정)
                # instance_details = self.get_instance_details(service_id, version_id, instance_id, params)

                # 메트릭 정보 조회 (향후 사용 예정)
                # metrics = self.get_instance_metrics(service_id, version_id, instance_id, params)

                # 기본 인스턴스 데이터 준비
                instance_data = {
                    "name": str(instance.get("name", "")),
                    "projectId": str(instance.get("projectId", "")),
                    "serviceId": str(service_id),
                    "versionId": str(version_id),
                    "id": str(instance_id),
                    "vmStatus": str(instance.get("vmStatus", "")),
                    "vmDebugEnabled": instance.get("vmDebugEnabled"),
                    "vmLiveness": str(instance.get("vmLiveness", "")),
                    "requestCount": instance.get("requestCount"),
                    "memoryUsage": instance.get("memoryUsage"),
                    "cpuUsage": instance.get("cpuUsage"),
                    "createTime": convert_datetime(instance.get("createTime")),
                    "updateTime": convert_datetime(instance.get("updateTime")),
                }

                # VM Details 추가
                if "vmDetails" in instance:
                    vm_details = instance["vmDetails"]
                    instance_data["vmDetails"] = {
                        "vmZoneName": str(vm_details.get("vmZoneName", "")),
                        "vmId": str(vm_details.get("vmId", "")),
                        "vmIp": str(vm_details.get("vmIp", "")),
                        "vmName": str(vm_details.get("vmName", "")),
                    }

                # App Engine Release 추가
                if "appEngineRelease" in instance:
                    instance_data["appEngineRelease"] = str(
                        instance["appEngineRelease"]
                    )

                # Availability 추가
                if "availability" in instance:
                    availability = instance["availability"]
                    instance_data["availability"] = {
                        "liveness": str(availability.get("liveness", "")),
                        "readiness": str(availability.get("readiness", "")),
                    }

                # Network 추가
                if "network" in instance:
                    network = instance["network"]
                    instance_data["network"] = {
                        "forwardedPorts": str(network.get("forwardedPorts", "")),
                        "instanceTag": str(network.get("instanceTag", "")),
                        "name": str(network.get("name", "")),
                        "subnetworkName": str(network.get("subnetworkName", "")),
                    }

                # Resources 추가
                if "resources" in instance:
                    resources = instance["resources"]
                    instance_data["resources"] = {
                        "cpu": resources.get("cpu"),
                        "diskGb": resources.get("diskGb"),
                        "memoryGb": resources.get("memoryGb"),
                        "volumes": resources.get("volumes", []),
                    }

                # AppEngineInstance 모델 생성
                app_engine_instance_data = AppEngineInstance(
                    instance_data, strict=False
                )

                # AppEngineInstanceResource 생성
                instance_resource = AppEngineInstanceResource(
                    {
                        "name": instance_data.get("name"),
                        "data": app_engine_instance_data,
                        "reference": {
                            "resource_id": instance_id,
                            "external_link": f"https://console.cloud.google.com/appengine/instances?project={project_id}&serviceId={service_id}&versionId={version_id}",
                        },
                        "region_code": "global",  # App Engine은 global 리소스
                        "account": instance_data.get("projectId"),
                    }
                )

                ##################################
                # 4. Make Collected Region Code
                ##################################
                self.set_region_code("global")

                # AppEngineInstanceResponse 생성
                instance_response = AppEngineInstanceResponse(
                    {"resource": instance_resource}
                )

                collected_cloud_services.append(instance_response)

            except Exception as e:
                _LOGGER.error(f"[collect_cloud_service] => {e}", exc_info=True)
                error_responses.append(
                    self.generate_error_response(
                        e, self.cloud_service_group, "Instance"
                    )
                )

        _LOGGER.debug("** AppEngine Instance V1 END **")
        return collected_cloud_services, error_responses
