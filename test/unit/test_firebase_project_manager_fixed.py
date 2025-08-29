#!/usr/bin/env python3
"""
Firebase Project Manager 단위 테스트 (수정된 버전)
"""

import unittest
from unittest.mock import Mock, patch

from spaceone.inventory.manager.firebase.project_manager import FirebaseProjectManager


class TestFirebaseProjectManagerFixed(unittest.TestCase):
    """Firebase Project Manager 테스트 클래스 (수정된 버전)"""

    def setUp(self):
        """각 테스트 메서드 실행 전 설정"""
        self.manager = FirebaseProjectManager()
        self.mock_locator = Mock()
        self.manager.locator = self.mock_locator

    @patch("spaceone.inventory.manager.firebase.project_manager.time")
    def test_collect_cloud_service_with_firebase_apps(self, mock_time):
        """Firebase 앱이 있는 프로젝트 테스트"""
        # Given
        mock_time.time.return_value = 1000.0

        mock_connector = Mock()
        mock_firebase_project_info = {
            "projectId": "test-project",
            "displayName": "Test Project",
            "projectNumber": "123456789",
            "state": "ACTIVE",
            "name": "projects/test-project",
            "firebaseApps": [
                {
                    "name": "projects/test-project/iosApps/1:123456789:ios:abc123",
                    "displayName": "Test iOS App",
                    "platform": "IOS",
                    "appId": "1:123456789:ios:abc123",
                    "state": "ACTIVE",
                }
            ],
            "appCount": 1,
            "hasFirebaseServices": "True",
            "platformStats": {"IOS": 1, "ANDROID": 0, "WEB": 0},
        }

        mock_connector.get_firebase_project_info.return_value = (
            mock_firebase_project_info
        )
        self.mock_locator.get_connector.return_value = mock_connector

        params = {
            "secret_data": {"project_id": "test-project"},
            "options": {},
            "schema": None,
            "filter": {},
        }

        # When
        cloud_services, error_responses = self.manager.collect_cloud_service(params)

        # Then
        self.assertEqual(len(cloud_services), 1)
        self.assertEqual(len(error_responses), 0)

        # Cloud service 데이터 검증
        cloud_service = cloud_services[0]
        self.assertEqual(cloud_service.resource.data.project_id, "test-project")
        self.assertEqual(cloud_service.resource.data.app_count, 1)
        self.assertEqual(cloud_service.resource.data.has_firebase_services, "True")
        self.assertEqual(cloud_service.resource.data.display_name, "Test Project")
        self.assertEqual(cloud_service.resource.data.state, "ACTIVE")

    @patch("spaceone.inventory.manager.firebase.project_manager.time")
    def test_collect_cloud_service_without_firebase_apps(self, mock_time):
        """Firebase 앱이 없는 프로젝트 테스트"""
        # Given
        mock_time.time.return_value = 1000.0

        mock_connector = Mock()
        mock_firebase_project_info = {
            "projectId": "test-project-no-firebase",
            "displayName": "Test Project Without Firebase",
            "projectNumber": "987654321",
            "state": "ACTIVE",
            "name": "projects/test-project-no-firebase",
            "firebaseApps": [],
            "appCount": 0,
            "hasFirebaseServices": False,
            "platformStats": {"IOS": 0, "ANDROID": 0, "WEB": 0},
        }

        mock_connector.get_firebase_project_info.return_value = (
            mock_firebase_project_info
        )
        self.mock_locator.get_connector.return_value = mock_connector

        params = {
            "secret_data": {"project_id": "test-project-no-firebase"},
            "options": {},
            "schema": None,
            "filter": {},
        }

        # When
        cloud_services, error_responses = self.manager.collect_cloud_service(params)

        # Then
        self.assertEqual(
            len(cloud_services), 0
        )  # Firebase 서비스가 없으므로 수집되지 않음
        self.assertEqual(len(error_responses), 0)

    @patch("spaceone.inventory.manager.firebase.project_manager.time")
    def test_collect_cloud_service_with_connector_error(self, mock_time):
        """커넥터에서 에러 발생 시 테스트"""
        # Given
        mock_time.time.return_value = 1000.0

        mock_connector = Mock()
        mock_connector.get_firebase_project_info.side_effect = Exception(
            "Firebase API 에러"
        )
        self.mock_locator.get_connector.return_value = mock_connector

        # generate_error_response 메서드 모킹
        self.manager.generate_error_response = Mock(return_value="error_response")

        params = {
            "secret_data": {"project_id": "test-project-error"},
            "options": {},
            "schema": None,
            "filter": {},
        }

        # When
        cloud_services, error_responses = self.manager.collect_cloud_service(params)

        # Then
        self.assertEqual(len(cloud_services), 0)
        self.assertEqual(len(error_responses), 1)
        self.manager.generate_error_response.assert_called_once()

    @patch("spaceone.inventory.manager.firebase.project_manager.time")
    @patch("spaceone.inventory.model.firebase.project.data.Project")
    def test_collect_cloud_service_with_parsing_error(
        self, mock_project_class, mock_time
    ):
        """데이터 파싱 중 에러 발생 시 테스트"""
        # Given
        mock_time.time.return_value = 1000.0

        mock_connector = Mock()
        mock_firebase_project_info = {
            "projectId": "test-project",
            "hasFirebaseServices": "True",
            "invalidField": "invalid",  # 잘못된 데이터로 파싱 에러 유발
        }

        mock_connector.get_firebase_project_info.return_value = (
            mock_firebase_project_info
        )
        self.mock_locator.get_connector.return_value = mock_connector

        # Project 클래스에서 에러 발생
        mock_project_class.side_effect = Exception("파싱 에러")

        # generate_error_response 메서드 모킹
        self.manager.generate_error_response = Mock(
            return_value="parsing_error_response"
        )

        params = {
            "secret_data": {"project_id": "test-project-parsing-error"},
            "options": {},
            "schema": None,
            "filter": {},
        }

        # When
        cloud_services, error_responses = self.manager.collect_cloud_service(params)

        # Then
        self.assertEqual(len(cloud_services), 0)
        self.assertEqual(len(error_responses), 1)
        self.manager.generate_error_response.assert_called_once()

    @patch("spaceone.inventory.manager.firebase.project_manager.time")
    def test_collect_cloud_service_with_multiple_apps(self, mock_time):
        """여러 Firebase 앱이 있는 프로젝트 테스트"""
        # Given
        mock_time.time.return_value = 1000.0

        mock_connector = Mock()
        mock_firebase_project_info = {
            "projectId": "test-project-multi-apps",
            "displayName": "Test Project Multi Apps",
            "projectNumber": "123456789",
            "state": "ACTIVE",
            "name": "projects/test-project-multi-apps",
            "firebaseApps": [
                {
                    "name": "projects/test-project/iosApps/1:123456789:ios:abc123",
                    "displayName": "Test iOS App",
                    "platform": "IOS",
                    "appId": "1:123456789:ios:abc123",
                    "state": "ACTIVE",
                },
                {
                    "name": "projects/test-project/androidApps/1:123456789:android:def456",
                    "displayName": "Test Android App",
                    "platform": "ANDROID",
                    "appId": "1:123456789:android:def456",
                    "state": "ACTIVE",
                },
                {
                    "name": "projects/test-project/webApps/1:123456789:web:ghi789",
                    "displayName": "Test Web App",
                    "platform": "WEB",
                    "appId": "1:123456789:web:ghi789",
                    "state": "ACTIVE",
                },
            ],
            "appCount": 3,
            "hasFirebaseServices": "True",
            "platformStats": {"IOS": 1, "ANDROID": 1, "WEB": 1},
        }

        mock_connector.get_firebase_project_info.return_value = (
            mock_firebase_project_info
        )
        self.mock_locator.get_connector.return_value = mock_connector

        params = {
            "secret_data": {"project_id": "test-project-multi-apps"},
            "options": {},
            "schema": None,
            "filter": {},
        }

        # When
        cloud_services, error_responses = self.manager.collect_cloud_service(params)

        # Then
        self.assertEqual(len(cloud_services), 1)
        self.assertEqual(len(error_responses), 0)

        # Cloud service 데이터 검증
        cloud_service = cloud_services[0]
        self.assertEqual(
            cloud_service.resource.data.project_id, "test-project-multi-apps"
        )
        self.assertEqual(cloud_service.resource.data.app_count, 3)
        self.assertEqual(cloud_service.resource.data.has_firebase_services, "True")
        self.assertEqual(len(cloud_service.resource.data.firebase_apps), 3)

        # 플랫폼별 통계 검증
        self.assertEqual(cloud_service.resource.data.platform_stats["IOS"], 1)
        self.assertEqual(cloud_service.resource.data.platform_stats["ANDROID"], 1)
        self.assertEqual(cloud_service.resource.data.platform_stats["WEB"], 1)

    def test_cloud_service_types(self):
        """Cloud Service Types 설정 테스트"""
        # When & Then
        self.assertIsNotNone(self.manager.cloud_service_types)
        self.assertEqual(self.manager.connector_name, "FirebaseProjectConnector")


if __name__ == "__main__":
    unittest.main()
