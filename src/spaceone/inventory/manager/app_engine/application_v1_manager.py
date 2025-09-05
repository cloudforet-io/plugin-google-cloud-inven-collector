import logging
from typing import List, Dict, Any, Tuple

from spaceone.inventory.connector.app_engine.application_v1 import (
    AppEngineApplicationV1Connector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager

from spaceone.inventory.model.app_engine.application.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)

from spaceone.inventory.model.app_engine.application.cloud_service import (
    AppEngineApplicationResource,
    AppEngineApplicationResponse,
)
from spaceone.inventory.model.app_engine.application.data import (
    AppEngineApplication,
)
from spaceone.inventory.model.kubernetes_engine.cluster.data import convert_datetime
from spaceone.inventory.libs.schema.cloud_service import ErrorResourceResponse

_LOGGER = logging.getLogger(__name__)


class AppEngineApplicationV1Manager(GoogleCloudManager):
    connector_name = "AppEngineApplicationV1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    cloud_service_group = "AppEngine"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_application(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """AppEngine 애플리케이션 정보를 조회합니다 (v1 API).

        Args:
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            App Engine 애플리케이션 정보 딕셔너리.

        Raises:
            Exception: App Engine API 호출 중 오류 발생 시.
        """
        app_connector: AppEngineApplicationV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            application = app_connector.get_application()
            if application:
                _LOGGER.info("Retrieved AppEngine application (v1)")
            return application or {}
        except Exception as e:
            _LOGGER.error(f"Failed to get AppEngine application (v1): {e}")
            return {}

    def list_services(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """AppEngine 서비스 목록을 조회합니다 (v1 API).

        Args:
            params: 조회에 필요한 파라미터 딕셔너리.

        Returns:
            App Engine 서비스 목록.

        Raises:
            Exception: App Engine API 호출 중 오류 발생 시.
        """
        app_connector: AppEngineApplicationV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            services = app_connector.list_services()
            _LOGGER.info(f"Found {len(services)} AppEngine services (v1)")
            return services
        except Exception as e:
            _LOGGER.error(f"Failed to list AppEngine services (v1): {e}")
            return []

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
        app_connector: AppEngineApplicationV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            versions = app_connector.list_versions(service_id)
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
        app_connector: AppEngineApplicationV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            instances = app_connector.list_instances(service_id, version_id)
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
        """AppEngine 애플리케이션 정보를 수집합니다 (v1 API).

        Args:
            params: 수집에 필요한 파라미터 딕셔너리.

        Returns:
            수집된 클라우드 서비스 목록과 오류 응답 목록의 튜플.

        Raises:
            Exception: 데이터 수집 중 오류 발생 시.
        """
        _LOGGER.debug("** AppEngine Application V1 START **")

        collected_cloud_services = []
        error_responses = []

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        # App Engine 애플리케이션 정보 조회
        application = self.get_application(params)

        if application:
            try:
                # 서비스 목록 조회
                services = self.list_services(params)

                # 버전 및 인스턴스 정보 수집
                total_versions = 0
                total_instances = 0

                for service in services:
                    service_id = service.get("id")
                    if service_id:
                        versions = self.list_versions(service_id, params)
                        total_versions += len(versions)

                        for version in versions:
                            version_id = version.get("id")
                            if version_id:
                                instances = self.list_instances(
                                    service_id, version_id, params
                                )
                                total_instances += len(instances)

                # 기본 애플리케이션 데이터 준비
                app_data = {
                    "name": str(application.get("name", "")),
                    "projectId": str(application.get("projectId", "")),
                    "locationId": str(application.get("locationId", "")),
                    "servingStatus": str(application.get("servingStatus", "")),
                    "defaultHostname": str(application.get("defaultHostname", "")),
                    "defaultCookieExpiration": str(
                        application.get("defaultCookieExpiration", "")
                    ),
                    "codeBucket": str(application.get("codeBucket", "")),
                    "gcrDomain": str(application.get("gcrDomain", "")),
                    "databaseType": str(application.get("databaseType", "")),
                    "createTime": convert_datetime(application.get("createTime")),
                    "updateTime": convert_datetime(application.get("updateTime")),
                    "version_count": str(total_versions),
                    "instance_count": str(total_instances),
                }

                # Feature Settings 추가
                if "featureSettings" in application:
                    feature_settings = application["featureSettings"]
                    app_data["featureSettings"] = {
                        "splitHealthChecks": str(
                            feature_settings.get("splitHealthChecks", "")
                        ),
                        "useContainerOptimizedOs": str(
                            feature_settings.get("useContainerOptimizedOs", "")
                        ),
                    }

                # IAP Settings 추가
                if "iap" in application:
                    iap_settings = application["iap"]
                    app_data["iap"] = {
                        "enabled": str(iap_settings.get("enabled", "")),
                        "oauth2ClientId": str(iap_settings.get("oauth2ClientId", "")),
                        "oauth2ClientSecret": str(
                            iap_settings.get("oauth2ClientSecret", "")
                        ),
                    }

                # URL Dispatch Rules 추가
                if "dispatchRules" in application:
                    dispatch_rules = application["dispatchRules"]
                    app_data["dispatchRules"] = []
                    for rule in dispatch_rules:
                        app_data["dispatchRules"].append(
                            {
                                "domain": str(rule.get("domain", "")),
                                "path": str(rule.get("path", "")),
                                "service": str(rule.get("service", "")),
                            }
                        )

                # AppEngineApplication 모델 생성
                app_engine_app_data = AppEngineApplication(app_data, strict=False)

                # AppEngineApplicationResource 생성
                app_resource = AppEngineApplicationResource(
                    {
                        "name": app_data.get("name"),
                        "data": app_engine_app_data,
                        "reference": {
                            "resource_id": application.get("name"),
                            "external_link": f"https://console.cloud.google.com/appengine/instances?project={project_id}",
                        },
                        "region_code": app_data.get("locationId"),
                        "account": app_data.get("projectId"),
                    }
                )

                ##################################
                # 4. Make Collected Region Code
                ##################################
                self.set_region_code(app_data.get("locationId"))

                # AppEngineApplicationResponse 생성
                app_response = AppEngineApplicationResponse({"resource": app_resource})

                collected_cloud_services.append(app_response)

            except Exception as e:
                _LOGGER.error(f"[collect_cloud_service] => {e}", exc_info=True)
                error_responses.append(
                    self.generate_error_response(
                        e, self.cloud_service_group, "Application"
                    )
                )

        _LOGGER.debug("** AppEngine Application V1 END **")
        return collected_cloud_services, error_responses
