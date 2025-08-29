#!/usr/bin/env python3
"""
Firebase Project Connector 단위 테스트 (수정된 버전)
"""

import unittest
from unittest.mock import Mock, patch

from spaceone.inventory.connector.firebase.project import FirebaseProjectConnector


class TestFirebaseProjectConnectorFixed(unittest.TestCase):
    """Firebase Project Connector 테스트 클래스 (수정된 버전)"""

    def setUp(self):
        """각 테스트 메서드 실행 전 설정"""
        self.secret_data = {
            "project_id": "test-project",
            "type": "service_account",
            "private_key": "test-key",
        }

        self.mock_credentials = Mock()
        self.mock_credentials.with_scopes.return_value = self.mock_credentials

        # Firebase API 클라이언트 모킹
        self.mock_client = Mock()

    @patch("googleapiclient.discovery.build")
    @patch("spaceone.inventory.libs.connector.GoogleCloudConnector.__init__")
    def test_init_with_scopes(self, mock_super_init, mock_discovery_build):
        """초기화 시 Firebase 스코프 설정 테스트"""
        # Given
        mock_super_init.return_value = None
        mock_discovery_build.return_value = self.mock_client

        # When
        connector = FirebaseProjectConnector(secret_data=self.secret_data)
        connector.credentials = self.mock_credentials
        connector.project_id = "test-project"

        # Then
        self.assertIsNotNone(connector)
        self.assertEqual(connector.google_client_service, "firebase")
        self.assertEqual(connector.version, "v1beta1")

    @patch("spaceone.inventory.libs.connector.GoogleCloudConnector.__init__")
    def test_list_firebase_apps_success(self, mock_super_init):
        """Firebase 앱 목록 조회 성공 테스트"""
        # Given
        mock_super_init.return_value = None
        connector = FirebaseProjectConnector(secret_data=self.secret_data)
        connector.project_id = "test-project"
        connector.client = self.mock_client

        mock_response = {
            "apps": [
                {
                    "name": "projects/test-project/iosApps/1:123456789:ios:abc123",
                    "displayName": "Test iOS App",
                    "platform": "IOS",
                    "appId": "1:123456789:ios:abc123",
                    "state": "ACTIVE",
                }
            ]
        }

        mock_request = Mock()
        mock_request.execute.return_value = mock_response

        self.mock_client.projects.return_value.searchApps.return_value = mock_request
        self.mock_client.projects.return_value.searchApps_next.return_value = None

        # When
        apps = connector.list_firebase_apps()

        # Then
        self.assertEqual(len(apps), 1)
        self.assertEqual(apps[0]["displayName"], "Test iOS App")
        self.assertEqual(apps[0]["platform"], "IOS")

    @patch("spaceone.inventory.libs.connector.GoogleCloudConnector.__init__")
    def test_list_firebase_apps_with_pagination(self, mock_super_init):
        """페이지네이션이 있는 Firebase 앱 목록 조회 테스트"""
        # Given
        mock_super_init.return_value = None
        connector = FirebaseProjectConnector(secret_data=self.secret_data)
        connector.project_id = "test-project"
        connector.client = self.mock_client

        # 첫 번째 페이지
        mock_response_1 = {
            "apps": [
                {
                    "name": "projects/test-project/iosApps/1:123456789:ios:abc123",
                    "displayName": "Test iOS App 1",
                    "platform": "IOS",
                }
            ]
        }

        # 두 번째 페이지
        mock_response_2 = {
            "apps": [
                {
                    "name": "projects/test-project/androidApps/1:123456789:android:def456",
                    "displayName": "Test Android App 2",
                    "platform": "ANDROID",
                }
            ]
        }

        mock_request_1 = Mock()
        mock_request_1.execute.return_value = mock_response_1

        mock_request_2 = Mock()
        mock_request_2.execute.return_value = mock_response_2

        self.mock_client.projects.return_value.searchApps.return_value = mock_request_1
        self.mock_client.projects.return_value.searchApps_next.side_effect = [
            mock_request_2,
            None,
        ]

        # When
        apps = connector.list_firebase_apps()

        # Then
        self.assertEqual(len(apps), 2)
        self.assertEqual(apps[0]["displayName"], "Test iOS App 1")
        self.assertEqual(apps[1]["displayName"], "Test Android App 2")

    @patch("spaceone.inventory.libs.connector.GoogleCloudConnector.__init__")
    def test_list_firebase_apps_error(self, mock_super_init):
        """Firebase 앱 목록 조회 에러 테스트"""
        # Given
        mock_super_init.return_value = None
        connector = FirebaseProjectConnector(secret_data=self.secret_data)
        connector.project_id = "test-project"
        connector.client = self.mock_client

        mock_request = Mock()
        mock_request.execute.side_effect = Exception("API 에러")

        self.mock_client.projects.return_value.searchApps.return_value = mock_request

        # When & Then
        with self.assertRaises(Exception) as context:
            connector.list_firebase_apps()

        self.assertIn("API 에러", str(context.exception))

    @patch("googleapiclient.discovery.build")
    @patch("spaceone.inventory.libs.connector.GoogleCloudConnector.__init__")
    def test_get_firebase_project_info_success(
        self, mock_super_init, mock_discovery_build
    ):
        """Firebase 프로젝트 정보 조회 성공 테스트"""
        # Given
        mock_super_init.return_value = None
        connector = FirebaseProjectConnector(secret_data=self.secret_data)
        connector.project_id = "test-project"
        connector.credentials = self.mock_credentials

        # Resource Manager API 모킹
        mock_resource_manager = Mock()
        mock_project_info = {
            "name": "Test Project",
            "projectNumber": "123456789",
            "lifecycleState": "ACTIVE",
        }
        mock_resource_manager.projects.return_value.get.return_value.execute.return_value = mock_project_info
        mock_discovery_build.return_value = mock_resource_manager

        # Firebase 앱 목록 모킹
        mock_firebase_apps = [
            {"platform": "IOS", "displayName": "Test iOS App"},
            {"platform": "ANDROID", "displayName": "Test Android App"},
        ]

        # When
        with patch.object(
            connector, "list_firebase_apps", return_value=mock_firebase_apps
        ):
            result = connector.get_firebase_project_info()

        # Then
        self.assertEqual(result["projectId"], "test-project")
        self.assertEqual(result["displayName"], "Test Project")
        self.assertEqual(result["projectNumber"], "123456789")
        self.assertEqual(result["state"], "ACTIVE")
        self.assertEqual(result["appCount"], 2)
        self.assertEqual(result["hasFirebaseServices"], "True")
        self.assertEqual(result["platformStats"]["IOS"], 1)
        self.assertEqual(result["platformStats"]["ANDROID"], 1)
        self.assertEqual(result["platformStats"]["WEB"], 0)

    @patch("googleapiclient.discovery.build")
    @patch("spaceone.inventory.libs.connector.GoogleCloudConnector.__init__")
    def test_get_firebase_project_info_no_apps(
        self, mock_super_init, mock_discovery_build
    ):
        """Firebase 앱이 없는 프로젝트 정보 조회 테스트"""
        # Given
        mock_super_init.return_value = None
        connector = FirebaseProjectConnector(secret_data=self.secret_data)
        connector.project_id = "test-project-no-apps"
        connector.credentials = self.mock_credentials

        # Resource Manager API 모킹
        mock_resource_manager = Mock()
        mock_project_info = {
            "name": "Test Project No Apps",
            "projectNumber": "987654321",
            "lifecycleState": "ACTIVE",
        }
        mock_resource_manager.projects.return_value.get.return_value.execute.return_value = mock_project_info
        mock_discovery_build.return_value = mock_resource_manager

        # Firebase 앱 없음
        mock_firebase_apps = []

        # When
        with patch.object(
            connector, "list_firebase_apps", return_value=mock_firebase_apps
        ):
            result = connector.get_firebase_project_info()

        # Then
        self.assertEqual(result["projectId"], "test-project-no-apps")
        self.assertEqual(result["appCount"], 0)
        self.assertEqual(result["hasFirebaseServices"], "False")
        self.assertEqual(result["platformStats"]["IOS"], 0)
        self.assertEqual(result["platformStats"]["ANDROID"], 0)
        self.assertEqual(result["platformStats"]["WEB"], 0)

    @patch("spaceone.inventory.libs.connector.GoogleCloudConnector.__init__")
    def test_get_project_success(self, mock_super_init):
        """특정 Firebase 프로젝트 조회 성공 테스트"""
        # Given
        mock_super_init.return_value = None
        connector = FirebaseProjectConnector(secret_data=self.secret_data)
        connector.client = self.mock_client

        mock_response = {
            "name": "projects/test-project",
            "projectId": "test-project",
            "displayName": "Test Firebase Project",
            "resources": {
                "hostingSite": "test-project",
                "storageBucket": "test-project.appspot.com",
            },
        }

        mock_request = Mock()
        mock_request.execute.return_value = mock_response

        self.mock_client.projects.return_value.get.return_value = mock_request

        # When
        result = connector.get_project("test-project")

        # Then
        self.assertEqual(result["projectId"], "test-project")
        self.assertEqual(result["displayName"], "Test Firebase Project")
        self.assertIn("resources", result)

    @patch("spaceone.inventory.libs.connector.GoogleCloudConnector.__init__")
    def test_get_project_error(self, mock_super_init):
        """특정 Firebase 프로젝트 조회 에러 테스트"""
        # Given
        mock_super_init.return_value = None
        connector = FirebaseProjectConnector(secret_data=self.secret_data)
        connector.client = self.mock_client

        mock_request = Mock()
        mock_request.execute.side_effect = Exception("프로젝트를 찾을 수 없습니다")

        self.mock_client.projects.return_value.get.return_value = mock_request

        # When & Then
        with self.assertRaises(Exception) as context:
            connector.get_project("non-existent-project")

        self.assertIn("프로젝트를 찾을 수 없습니다", str(context.exception))


if __name__ == "__main__":
    unittest.main()
