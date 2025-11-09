"""AppEngine 도메인 매니저들의 단위 테스트."""

import unittest
from unittest.mock import Mock, patch

# AppEngine 매니저들 임포트
from spaceone.inventory.manager.app_engine.application_v1_manager import (
    AppEngineApplicationV1Manager,
)
from spaceone.inventory.manager.app_engine.instance_v1_manager import (
    AppEngineInstanceV1Manager,
)
from spaceone.inventory.manager.app_engine.service_v1_manager import (
    AppEngineServiceV1Manager,
)
from spaceone.inventory.manager.app_engine.version_v1_manager import (
    AppEngineVersionV1Manager,
)


class TestAppEngineApplicationV1Manager(unittest.TestCase):
    """AppEngineApplicationV1Manager 테스트 클래스."""

    def setUp(self):
        """테스트 설정."""
        self.manager = AppEngineApplicationV1Manager()
        self.mock_params = {"secret_data": {"project_id": "test-project-id"}}

    def test_get_application_success(self):
        """애플리케이션 조회 성공 테스트."""
        with patch.object(self.manager, "locator") as mock_locator:
            mock_connector = Mock()
            mock_connector.get_application.return_value = {
                "name": "test-app",
                "projectId": "test-project-id",
            }
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.get_application(self.mock_params)

            self.assertIsInstance(result, dict)
            self.assertEqual(result["name"], "test-app")

    def test_get_application_empty_result(self):
        """애플리케이션 조회 결과가 비어있는 경우 테스트."""
        with patch.object(self.manager, "locator") as mock_locator:
            mock_connector = Mock()
            mock_connector.get_application.return_value = None
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.get_application(self.mock_params)

            self.assertEqual(result, {})

    def test_list_services_success(self):
        """서비스 목록 조회 성공 테스트."""
        with patch.object(self.manager, "locator") as mock_locator:
            mock_connector = Mock()
            mock_connector.list_services.return_value = [
                {"id": "service1", "name": "Service 1"},
                {"id": "service2", "name": "Service 2"},
            ]
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.list_services(self.mock_params)

            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)

    def test_list_versions_success(self):
        """버전 목록 조회 성공 테스트."""
        with patch.object(self.manager, "locator") as mock_locator:
            mock_connector = Mock()
            mock_connector.list_versions.return_value = [
                {"id": "v1", "name": "Version 1"},
                {"id": "v2", "name": "Version 2"},
            ]
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.list_versions("test-service", self.mock_params)

            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)

    def test_list_instances_success(self):
        """인스턴스 목록 조회 성공 테스트."""
        with patch.object(self.manager, "locator") as mock_locator:
            mock_connector = Mock()
            mock_connector.list_instances.return_value = [
                {"id": "instance1", "name": "Instance 1"},
                {"id": "instance2", "name": "Instance 2"},
            ]
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.list_instances(
                "test-service", "test-version", self.mock_params
            )

            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)


class TestAppEngineServiceV1Manager(unittest.TestCase):
    """AppEngineServiceV1Manager 테스트 클래스."""

    def setUp(self):
        """테스트 설정."""
        self.manager = AppEngineServiceV1Manager()
        self.mock_params = {"secret_data": {"project_id": "test-project-id"}}

    def test_list_services_success(self):
        """서비스 목록 조회 성공 테스트."""
        with patch.object(self.manager, "locator") as mock_locator:
            mock_connector = Mock()
            mock_connector.list_services.return_value = [
                {"id": "service1", "name": "Service 1"},
                {"id": "service2", "name": "Service 2"},
            ]
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.list_services(self.mock_params)

            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)

    def test_get_service_success(self):
        """서비스 조회 성공 테스트."""
        with patch.object(self.manager, "locator") as mock_locator:
            mock_connector = Mock()
            mock_connector.get_service.return_value = {
                "id": "test-service",
                "name": "Test Service",
            }
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.get_service("test-service", self.mock_params)

            self.assertIsInstance(result, dict)
            self.assertEqual(result["id"], "test-service")


class TestAppEngineVersionV1Manager(unittest.TestCase):
    """AppEngineVersionV1Manager 테스트 클래스."""

    def setUp(self):
        """테스트 설정."""
        self.manager = AppEngineVersionV1Manager()
        self.mock_params = {"secret_data": {"project_id": "test-project-id"}}

    def test_list_versions_success(self):
        """버전 목록 조회 성공 테스트."""
        with patch.object(self.manager, "locator") as mock_locator:
            mock_connector = Mock()
            mock_connector.list_versions.return_value = [
                {"id": "v1", "name": "Version 1"},
                {"id": "v2", "name": "Version 2"},
            ]
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.list_versions("test-service", self.mock_params)

            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)

    def test_get_version_success(self):
        """버전 조회 성공 테스트."""
        with patch.object(self.manager, "locator") as mock_locator:
            mock_connector = Mock()
            mock_connector.get_version.return_value = {
                "id": "test-version",
                "name": "Test Version",
            }
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.get_version(
                "test-service", "test-version", self.mock_params
            )

            self.assertIsInstance(result, dict)
            self.assertEqual(result["id"], "test-version")

    def test_environment_field_mapping(self):
        """environment 필드가 env 필드에서 올바르게 매핑되는지 테스트."""
        with patch.object(self.manager, "locator") as mock_locator:
            # Mock connector 설정
            mock_connector = Mock()
            mock_connector.list_versions.return_value = [
                {
                    "id": "test-version",
                    "name": "Test Version",
                    "env": "standard",  # env 필드로 environment 정보 제공
                    "runtime": "python39",
                    "servingStatus": "SERVING",
                    "createTime": "2023-01-01T00:00:00Z",
                }
            ]
            mock_connector.list_instances.return_value = []
            mock_connector.get_version_metrics.return_value = {}
            mock_locator.get_connector.return_value = mock_connector

            # Mock application connector
            with patch(
                "spaceone.inventory.connector.app_engine.application_v1.AppEngineApplicationV1Connector"
            ) as mock_app_connector_class:
                mock_app_connector = Mock()
                mock_app_connector.list_services.return_value = [{"id": "test-service"}]
                mock_app_connector_class.return_value = mock_app_connector

                # collect_cloud_service 호출
                collected_services, errors = self.manager.collect_cloud_service(
                    self.mock_params
                )

                # 결과 검증
                self.assertEqual(len(errors), 0)
                self.assertEqual(len(collected_services), 1)

                # environment 필드가 올바르게 매핑되었는지 확인
                service_data = collected_services[0].resource.data
                self.assertEqual(service_data.environment, "standard")


class TestAppEngineInstanceV1Manager(unittest.TestCase):
    """AppEngineInstanceV1Manager 테스트 클래스."""

    def setUp(self):
        """테스트 설정."""
        self.manager = AppEngineInstanceV1Manager()
        self.mock_params = {"secret_data": {"project_id": "test-project-id"}}

    def test_list_instances_success(self):
        """인스턴스 목록 조회 성공 테스트."""
        with patch.object(self.manager, "locator") as mock_locator:
            mock_connector = Mock()
            mock_connector.list_instances.return_value = [
                {"id": "instance1", "name": "Instance 1"},
                {"id": "instance2", "name": "Instance 2"},
            ]
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.list_instances(
                "test-service", "test-version", self.mock_params
            )

            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)

    def test_get_instance_success(self):
        """인스턴스 조회 성공 테스트."""
        with patch.object(self.manager, "locator") as mock_locator:
            mock_connector = Mock()
            mock_connector.get_instance.return_value = {
                "id": "test-instance",
                "name": "Test Instance",
            }
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.get_instance(
                "test-service", "test-version", "test-instance", self.mock_params
            )

            self.assertIsInstance(result, dict)
            self.assertEqual(result["id"], "test-instance")


if __name__ == "__main__":
    unittest.main()
