import logging
from typing import Any, Dict, List, Tuple

from spaceone.inventory.connector.app_engine.instance_v1 import (
    AppEngineInstanceV1Connector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import (
    BaseResponse,
    log_state_summary,
    reset_state_counters,
)
from spaceone.inventory.libs.schema.cloud_service import ErrorResourceResponse
from spaceone.inventory.model.app_engine.instance.cloud_service import (
    AppEngineInstanceResource,
)
from spaceone.inventory.model.app_engine.instance.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.app_engine.instance.data import AppEngineInstance
from spaceone.inventory.model.kubernetes_engine.cluster.data import convert_datetime

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

        # 상태 카운터 초기화
        reset_state_counters()

        collected_cloud_services = []
        error_responses = []

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        # App Engine 서비스를 통해 체계적으로 인스턴스 수집
        try:
            # 서비스 목록 조회
            app_connector = self.locator.get_connector(
                "AppEngineApplicationV1Connector", **params
            )
            services = app_connector.list_services()
            _LOGGER.info(f"Found {len(services)} App Engine services")

            for service in services:
                service_id = service.get("id")
                if not service_id:
                    continue

                try:
                    # 각 서비스의 버전 목록 조회
                    versions = app_connector.list_versions(service_id)
                    _LOGGER.debug(
                        f"Found {len(versions)} versions for service {service_id}"
                    )

                    for version in versions:
                        version_id = version.get("id")
                        if not version_id:
                            continue

                        try:
                            # 각 버전의 인스턴스 목록 조회
                            instances = self.list_instances(
                                service_id, version_id, params
                            )
                            _LOGGER.debug(
                                f"Found {len(instances)} instances for version {service_id}/{version_id}"
                            )

                            for instance in instances:
                                try:
                                    instance_id = instance.get("id")

                                    if not instance_id:
                                        _LOGGER.warning(
                                            f"Instance without ID found in service {service_id}, version {version_id}"
                                        )
                                        continue

                                    _LOGGER.debug(
                                        f"Processing instance {instance_id} for service {service_id}, version {version_id}"
                                    )
                                    _LOGGER.debug(f"Raw instance data: {instance}")

                                    # VM Status 및 Availability 디버깅
                                    _LOGGER.info(
                                        f"[API_RESPONSE] Instance {instance_id} - vmStatus: {instance.get('vmStatus')}"
                                    )
                                    _LOGGER.info(
                                        f"[API_RESPONSE] Instance {instance_id} - vmLiveness: {instance.get('vmLiveness')}"
                                    )
                                    _LOGGER.info(
                                        f"[API_RESPONSE] Instance {instance_id} - availability: {instance.get('availability')}"
                                    )
                                    _LOGGER.info(
                                        f"[API_RESPONSE] Instance {instance_id} - servingStatus: {instance.get('servingStatus')}"
                                    )
                                    _LOGGER.info(
                                        f"[API_RESPONSE] Instance {instance_id} - status: {instance.get('status')}"
                                    )
                                    _LOGGER.info(
                                        f"[API_RESPONSE] Instance {instance_id} - all keys: {sorted(list(instance.keys()))}"
                                    )
                                    _LOGGER.info(
                                        f"[API_RESPONSE] Instance {instance_id} - full response: {instance}"
                                    )

                                    # 인스턴스 상세 정보 조회
                                    instance_details = self.get_instance_details(
                                        service_id, version_id, instance_id, params
                                    )
                                    if instance_details:
                                        # 상세 정보로 기본 정보 업데이트
                                        instance.update(instance_details)
                                        _LOGGER.debug(
                                            f"Enhanced instance {instance_id} with detailed information"
                                        )

                                    # 메트릭 정보 조회
                                    metrics = self.get_instance_metrics(
                                        service_id, version_id, instance_id, params
                                    )
                                    if metrics:
                                        instance["metrics"] = metrics
                                        _LOGGER.debug(
                                            f"Added metrics to instance {instance_id}"
                                        )

                                    _LOGGER.debug(
                                        f"Final instance data after enhancements: {instance}"
                                    )

                                    # 기본 인스턴스 데이터 준비 - API 응답 구조와 정확히 일치하도록 수정
                                    instance_data = {
                                        # 기본 정보 - API 응답에서 직접 매핑
                                        "instance_id": str(
                                            instance_id
                                        ),  # API에서 'id' 필드
                                        "project_id": str(
                                            project_id
                                        ),  # secret_data에서 가져온 project_id 사용
                                        "service_id": str(service_id),
                                        "version_id": str(version_id),
                                        # VM 상태 정보 - App Engine 특성에 맞는 매핑
                                        "vm_status": str(
                                            instance.get("vmStatus")
                                            or instance.get("status")
                                            or instance.get("servingStatus")
                                            or
                                            # App Engine Flexible의 경우 availability가 상태를 나타냄
                                            (
                                                instance.get("availability")
                                                if instance.get("availability")
                                                in ["RUNNING", "DYNAMIC", "RESIDENT"]
                                                else None
                                            )
                                            or "UNKNOWN"
                                        ),
                                        "vm_debug_enabled": bool(
                                            instance.get("vmDebugEnabled", False)
                                        ),
                                        "vm_liveness": str(
                                            instance.get(
                                                "vmLiveness",
                                                instance.get("liveness", ""),
                                            )
                                        ),
                                        # 사용량 정보
                                        "request_count": int(
                                            instance.get(
                                                "requests",
                                                instance.get("requestCount", 0),
                                            )
                                            or 0
                                        ),
                                        "memory_usage": float(
                                            instance.get("memoryUsage", 0) or 0
                                        ),
                                        "cpu_usage": float(
                                            instance.get("cpuUsage", 0) or 0
                                        ),
                                        "qps": float(instance.get("qps", 0) or 0),
                                        "average_latency": float(
                                            instance.get("averageLatency", 0) or 0
                                        ),
                                        "errors": int(instance.get("errors", 0) or 0),
                                        # 시간 정보
                                        "create_time": convert_datetime(
                                            instance.get(
                                                "startTime", instance.get("createTime")
                                            )
                                        ),
                                        "update_time": convert_datetime(
                                            instance.get("updateTime", "")
                                        ),
                                        "start_time": convert_datetime(
                                            instance.get("startTime", "")
                                        ),
                                    }

                                    # 수집된 메트릭 정보 추가 (기존 availability는 덮어쓰지 않음)
                                    if "metrics" in instance:
                                        metrics_data = instance["metrics"]
                                        enhanced_metrics = {
                                            "memory_usage_enhanced": metrics_data.get(
                                                "memory_usage", ""
                                            ),
                                            "cpu_usage_enhanced": metrics_data.get(
                                                "cpu_usage", ""
                                            ),
                                            "request_count_enhanced": metrics_data.get(
                                                "request_count", ""
                                            ),
                                            "app_engine_release_enhanced": metrics_data.get(
                                                "app_engine_release", ""
                                            ),
                                        }
                                        instance_data.update(enhanced_metrics)

                                    # VM Details 추가 - 딕셔너리 타입 검증 후 전달
                                    if "vmDetails" in instance:
                                        vm_details = instance["vmDetails"]
                                        if isinstance(vm_details, dict):
                                            instance_data["vm_details"] = vm_details
                                        else:
                                            _LOGGER.warning(
                                                f"vmDetails is not a dict for instance {instance_id}: {type(vm_details)}"
                                            )

                                    # App Engine Release 추가
                                    if "appEngineRelease" in instance:
                                        instance_data["app_engine_release"] = str(
                                            instance["appEngineRelease"]
                                        )

                                    # Availability 추가 - 다양한 필드명 시도 및 타입 변환
                                    availability_data = None

                                    # 다양한 가능한 필드명 시도
                                    for field_name in [
                                        "availability",
                                        "vmLiveness",
                                        "liveness",
                                        "status",
                                    ]:
                                        if field_name in instance:
                                            availability_data = instance[field_name]
                                            _LOGGER.debug(
                                                f"Found availability data in {field_name} for {instance_id}: {availability_data}"
                                            )
                                            break

                                    if availability_data is not None:
                                        _LOGGER.debug(
                                            f"Processing availability for {instance_id}: {availability_data} (type: {type(availability_data)})"
                                        )

                                        if isinstance(availability_data, dict):
                                            # 이미 딕셔너리 형태면 그대로 사용
                                            instance_data["availability"] = (
                                                availability_data
                                            )
                                        elif isinstance(availability_data, str):
                                            # 문자열이면 liveness 필드로 매핑
                                            instance_data["availability"] = {
                                                "liveness": availability_data,
                                                "readiness": "",
                                            }
                                        else:
                                            # 다른 타입이면 문자열로 변환하여 liveness에 설정
                                            instance_data["availability"] = {
                                                "liveness": str(availability_data),
                                                "readiness": "",
                                            }
                                    else:
                                        # availability 관련 필드가 없는 경우 VM 상태 기반으로 설정
                                        vm_status = instance_data.get(
                                            "vm_status", "UNKNOWN"
                                        )
                                        liveness_status = (
                                            "HEALTHY"
                                            if vm_status == "RUNNING"
                                            else "UNHEALTHY"
                                            if vm_status != "UNKNOWN"
                                            else ""
                                        )
                                        instance_data["availability"] = {
                                            "liveness": liveness_status,
                                            "readiness": "",
                                        }

                                    # Network 추가 - 딕셔너리 타입 검증 후 전달
                                    if "network" in instance:
                                        network = instance["network"]
                                        if isinstance(network, dict):
                                            instance_data["network"] = network
                                        else:
                                            _LOGGER.warning(
                                                f"network is not a dict for instance {instance_id}: {type(network)}"
                                            )

                                    # Resources 추가 - 딕셔너리 타입 검증 후 전달
                                    if "resources" in instance:
                                        resources = instance["resources"]
                                        if isinstance(resources, dict):
                                            instance_data["resources"] = resources
                                        else:
                                            _LOGGER.warning(
                                                f"resources is not a dict for instance {instance_id}: {type(resources)}"
                                            )

                                    _LOGGER.debug(
                                        f"Created instance_data for {instance_id}: {instance_data}"
                                    )

                                    # Stackdriver 정보 추가
                                    if not instance_id:
                                        _LOGGER.warning(
                                            f"Instance missing ID, skipping monitoring setup: service={service_id}, version={version_id}"
                                        )
                                        instance_id = "unknown"

                                    # Google Cloud Monitoring/Logging 리소스 ID: App Engine Instance의 경우 instance_id 사용
                                    monitoring_resource_id = instance_id

                                    google_cloud_monitoring_filters = [
                                        {
                                            "key": "resource.labels.module_id",
                                            "value": service_id,
                                        },
                                        {
                                            "key": "resource.labels.version_id",
                                            "value": version_id,
                                        },
                                        {
                                            "key": "resource.labels.instance_id",
                                            "value": instance_id,
                                        },
                                        {
                                            "key": "resource.labels.project_id",
                                            "value": project_id,
                                        },
                                    ]
                                    instance_data["google_cloud_monitoring"] = (
                                        self.set_google_cloud_monitoring(
                                            project_id,
                                            "appengine.googleapis.com/flex/instance",
                                            monitoring_resource_id,
                                            google_cloud_monitoring_filters,
                                        )
                                    )
                                    instance_data["google_cloud_logging"] = (
                                        self.set_google_cloud_logging(
                                            "AppEngine",
                                            "Instance",
                                            project_id,
                                            monitoring_resource_id,
                                        )
                                    )

                                    # AppEngineInstance 모델 생성
                                    app_engine_instance_data = AppEngineInstance(
                                        instance_data, strict=False
                                    )
                                    _LOGGER.debug(
                                        f"Created AppEngineInstance model for {instance_id}: {app_engine_instance_data}"
                                    )

                                    # AppEngineInstanceResource 생성
                                    instance_resource = AppEngineInstanceResource(
                                        {
                                            "name": instance_data.get("instance_id"),
                                            "data": app_engine_instance_data,
                                            "reference": {
                                                "resource_id": instance_id,
                                                "external_link": f"https://console.cloud.google.com/appengine/instances?project={project_id}&serviceId={service_id}&versionId={version_id}",
                                            },
                                            "region_code": "global",  # App Engine은 global 리소스
                                            "account": instance_data.get("project_id"),
                                        }
                                    )
                                    _LOGGER.debug(
                                        f"Created AppEngineInstanceResource for {instance_id}"
                                    )

                                    ##################################
                                    # 4. Make Collected Region Code
                                    ##################################
                                    self.set_region_code("global")

                                    # BaseResponse를 사용한 로깅 기반 응답 생성
                                    instance_response = (
                                        BaseResponse.create_with_logging(
                                            state="SUCCESS",
                                            resource_type="inventory.CloudService",
                                            resource=instance_resource,
                                            match_rules={
                                                "1": [
                                                    "reference.resource_id",
                                                    "provider",
                                                    "cloud_service_type",
                                                    "cloud_service_group",
                                                ]
                                            },
                                        )
                                    )

                                    collected_cloud_services.append(instance_response)
                                    _LOGGER.info(
                                        f"Successfully collected App Engine instance: {instance_id} (status: {instance_data.get('vm_status', 'unknown')})"
                                    )
                                    _LOGGER.info(
                                        f"Instance response data - Service ID: {instance_data.get('service_id')}, Version ID: {instance_data.get('version_id')}, VM Status: {instance_data.get('vm_status')}"
                                    )

                                except Exception as e:
                                    _LOGGER.error(
                                        f"[collect_cloud_service] Instance {instance_id} => {e}",
                                        exc_info=True,
                                    )
                                    error_response = (
                                        ErrorResourceResponse.create_with_logging(
                                            error_message=str(e),
                                            error_code="INSTANCE_COLLECTION_ERROR",
                                            resource_type="inventory.ErrorResource",
                                            additional_data={
                                                "cloud_service_group": "AppEngine",
                                                "cloud_service_type": "Instance",
                                                "resource_id": instance_id or "unknown",
                                            },
                                        )
                                    )
                                    error_responses.append(error_response)

                        except Exception as e:
                            _LOGGER.error(
                                f"[collect_cloud_service] Version {service_id}/{version_id} => {e}",
                                exc_info=True,
                            )
                            error_response = ErrorResourceResponse.create_with_logging(
                                error_message=str(e),
                                error_code="VERSION_COLLECTION_ERROR",
                                resource_type="inventory.ErrorResource",
                                additional_data={
                                    "cloud_service_group": "AppEngine",
                                    "cloud_service_type": "Instance",
                                    "resource_id": f"{service_id}/{version_id}",
                                },
                            )
                            error_responses.append(error_response)

                except Exception as e:
                    _LOGGER.error(
                        f"[collect_cloud_service] Service {service_id} => {e}",
                        exc_info=True,
                    )
                    error_response = ErrorResourceResponse.create_with_logging(
                        error_message=str(e),
                        error_code="SERVICE_COLLECTION_ERROR",
                        resource_type="inventory.ErrorResource",
                        additional_data={
                            "cloud_service_group": "AppEngine",
                            "cloud_service_type": "Instance",
                            "resource_id": service_id or "unknown",
                        },
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(f"[collect_cloud_service] => {e}", exc_info=True)
            error_response = ErrorResourceResponse.create_with_logging(
                error_message=str(e),
                error_code="COLLECTION_ERROR",
                resource_type="inventory.ErrorResource",
                additional_data={
                    "cloud_service_group": "AppEngine",
                    "cloud_service_type": "Instance",
                    "resource_id": "AppEngine Instance Collection",
                },
            )
            error_responses.append(error_response)

        # 수집 결과 요약 로깅
        log_state_summary()

        _LOGGER.debug("** AppEngine Instance V1 END **")
        _LOGGER.info(
            f"Collected {len(collected_cloud_services)} App Engine instances, {len(error_responses)} errors"
        )
        return collected_cloud_services, error_responses
