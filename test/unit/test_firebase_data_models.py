#!/usr/bin/env python3
"""
Firebase Data Models 단위 테스트
"""

import unittest

from spaceone.inventory.model.firebase.project.data import FirebaseApp, Project


class TestFirebaseDataModels(unittest.TestCase):
    """Firebase 데이터 모델 테스트 클래스"""

    def test_firebase_app_model(self):
        """FirebaseApp 모델 테스트"""
        # Given
        app_data = {
            "name": "projects/test-project/iosApps/1:123456789:ios:abc123",
            "displayName": "Test iOS App",
            "platform": "IOS",
            "appId": "1:123456789:ios:abc123",
            "namespace": "test-project",
            "apiKeyId": "api-key-123",
            "state": "ACTIVE",
            "expireTime": "2025-12-31T23:59:59Z",
        }

        # When
        firebase_app = FirebaseApp(app_data)

        # Then
        self.assertEqual(
            firebase_app.name, "projects/test-project/iosApps/1:123456789:ios:abc123"
        )
        self.assertEqual(firebase_app.display_name, "Test iOS App")
        self.assertEqual(firebase_app.platform, "IOS")
        self.assertEqual(firebase_app.app_id, "1:123456789:ios:abc123")
        self.assertEqual(firebase_app.namespace, "test-project")
        self.assertEqual(firebase_app.api_key_id, "api-key-123")
        self.assertEqual(firebase_app.state, "ACTIVE")
        self.assertEqual(firebase_app.expire_time, "2025-12-31T23:59:59Z")

    def test_firebase_app_model_with_minimal_data(self):
        """최소한의 데이터로 FirebaseApp 모델 테스트"""
        # Given
        app_data = {"platform": "ANDROID", "appId": "1:123456789:android:def456"}

        # When
        firebase_app = FirebaseApp(app_data)

        # Then
        self.assertEqual(firebase_app.platform, "ANDROID")
        self.assertEqual(firebase_app.app_id, "1:123456789:android:def456")
        self.assertIsNone(firebase_app.display_name)
        self.assertIsNone(firebase_app.namespace)

    def test_project_model_with_firebase_apps(self):
        """Firebase 앱이 있는 Project 모델 테스트"""
        # Given
        project_data = {
            "projectId": "test-project",
            "displayName": "Test Project",
            "projectNumber": "123456789",
            "state": "ACTIVE",
            "name": "projects/test-project",
            "firebaseApps": [
                {
                    "displayName": "Test iOS App",
                    "platform": "IOS",
                    "appId": "1:123456789:ios:abc123",
                    "state": "ACTIVE",
                },
                {
                    "displayName": "Test Android App",
                    "platform": "ANDROID",
                    "appId": "1:123456789:android:def456",
                    "state": "ACTIVE",
                },
            ],
            "appCount": 2,
            "hasFirebaseServices": "True",
            "platformStats": {"IOS": 1, "ANDROID": 1, "WEB": 0},
        }

        # When
        project = Project(project_data)

        # Then
        self.assertEqual(project.project_id, "test-project")
        self.assertEqual(project.display_name, "Test Project")
        self.assertEqual(project.project_number, "123456789")
        self.assertEqual(project.state, "ACTIVE")
        self.assertEqual(project.name, "projects/test-project")
        self.assertEqual(project.app_count, 2)
        self.assertEqual(project.has_firebase_services, "True")
        self.assertEqual(len(project.firebase_apps), 2)
        self.assertEqual(project.platform_stats["IOS"], 1)
        self.assertEqual(project.platform_stats["ANDROID"], 1)
        self.assertEqual(project.platform_stats["WEB"], 0)

    def test_project_model_without_firebase_apps(self):
        """Firebase 앱이 없는 Project 모델 테스트"""
        # Given
        project_data = {
            "projectId": "test-project-no-apps",
            "displayName": "Test Project No Apps",
            "projectNumber": "987654321",
            "state": "ACTIVE",
            "name": "projects/test-project-no-apps",
            "firebaseApps": [],
            "appCount": 0,
            "hasFirebaseServices": "False",
            "platformStats": {"IOS": 0, "ANDROID": 0, "WEB": 0},
        }

        # When
        project = Project(project_data)

        # Then
        self.assertEqual(project.project_id, "test-project-no-apps")
        self.assertEqual(project.app_count, 0)
        self.assertEqual(project.has_firebase_services, "False")
        self.assertEqual(len(project.firebase_apps), 0)
        self.assertEqual(project.platform_stats["IOS"], 0)
        self.assertEqual(project.platform_stats["ANDROID"], 0)
        self.assertEqual(project.platform_stats["WEB"], 0)

    def test_project_reference(self):
        """Project 참조 정보 테스트"""
        # Given
        project_data = {
            "projectId": "test-project-reference",
            "displayName": "Test Project Reference",
        }

        # When
        project = Project(project_data)
        reference = project.reference()

        # Then
        self.assertEqual(reference["resource_id"], "test-project-reference")
        self.assertEqual(
            reference["external_link"],
            "https://console.firebase.google.com/project/test-project-reference",
        )

    def test_project_model_with_minimal_data(self):
        """최소한의 데이터로 Project 모델 테스트"""
        # Given
        project_data = {"projectId": "minimal-project"}

        # When
        project = Project(project_data)

        # Then
        self.assertEqual(project.project_id, "minimal-project")
        self.assertIsNone(project.display_name)
        self.assertIsNone(project.project_number)
        self.assertIsNone(project.state)
        self.assertIsNone(project.name)
        self.assertIsNone(project.app_count)
        self.assertIsNone(project.has_firebase_services)

    def test_project_model_with_invalid_firebase_app_data(self):
        """잘못된 Firebase 앱 데이터로 Project 모델 테스트"""
        # Given
        project_data = {
            "projectId": "test-project-invalid-apps",
            "firebaseApps": [
                {
                    "platform": "IOS"
                    # appId가 누락된 잘못된 데이터
                },
                {"platform": "ANDROID", "appId": "1:123456789:android:valid456"},
            ],
            "appCount": 2,
        }

        # When
        project = Project(project_data)

        # Then
        self.assertEqual(project.project_id, "test-project-invalid-apps")
        self.assertEqual(len(project.firebase_apps), 2)
        self.assertEqual(project.app_count, 2)

        # 첫 번째 앱은 appId가 없어도 모델은 생성됨
        self.assertEqual(project.firebase_apps[0].platform, "IOS")
        self.assertIsNone(project.firebase_apps[0].app_id)

        # 두 번째 앱은 정상
        self.assertEqual(project.firebase_apps[1].platform, "ANDROID")
        self.assertEqual(
            project.firebase_apps[1].app_id, "1:123456789:android:valid456"
        )


if __name__ == "__main__":
    unittest.main()
