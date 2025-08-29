#!/usr/bin/env python3
"""
KMS KeyRing 관련 단위 테스트

이 파일은 KMS KeyRing의 Connector, Manager, Data 모델 등의 기능을 테스트합니다.
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# 직접 import 경로 사용 (상대경로)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from spaceone.inventory.connector.kms.keyring_v1 import KMSKeyRingV1Connector
from spaceone.inventory.manager.kms.keyring_manager import KMSKeyRingManager
from spaceone.inventory.model.kms.keyring.data import (
    CryptoKeyData,
    CryptoKeyVersionData,
    KMSKeyRingData,
)


class TestKMSKeyRingConnector(unittest.TestCase):
    """KMS KeyRing Connector 테스트"""

    def test_common_kms_locations_defined(self):
        """COMMON_KMS_LOCATIONS가 올바르게 정의되었는지 테스트"""
        # Given & When
        locations = KMSKeyRingV1Connector.COMMON_KMS_LOCATIONS

        # Then
        self.assertIsInstance(locations, list)
        self.assertGreater(len(locations), 0)
        self.assertIn("global", locations)
        self.assertIn("us-central1", locations)
        self.assertIn("asia-northeast3", locations)

    @patch(
        "spaceone.inventory.libs.connector.google.oauth2.service_account.Credentials.from_service_account_info"
    )
    @patch("spaceone.inventory.libs.connector.googleapiclient.discovery.build")
    def test_get_location_display_name(self, mock_build, mock_credentials):
        """Location display name 생성 테스트"""
        # Given
        mock_credentials.return_value = Mock()
        mock_build.return_value = Mock()

        connector = KMSKeyRingV1Connector(
            secret_data={
                "type": "service_account",
                "project_id": "test-project-id",
                "client_email": "test@example.com",
                "token_uri": "https://oauth2.googleapis.com/token",
                "private_key": "dummy-key",
            }
        )

        # When
        global_name = connector._get_location_display_name("global")
        seoul_name = connector._get_location_display_name("asia-northeast3")
        unknown_name = connector._get_location_display_name("unknown-location")

        # Then
        self.assertEqual(global_name, "Global")
        self.assertEqual(seoul_name, "Seoul (asia-northeast3)")
        self.assertEqual(unknown_name, "unknown-location")


class TestKMSKeyRingManager(unittest.TestCase):
    """KMS KeyRing Manager 테스트"""

    def setUp(self):
        """테스트 초기화"""
        self.manager = KMSKeyRingManager()
        self.manager.locator = Mock()

    def test_manager_initialization(self):
        """Manager 초기화 테스트"""
        # Given & When & Then
        self.assertEqual(self.manager.connector_name, "KMSKeyRingV1Connector")
        self.assertEqual(self.manager.cloud_service_group, "KMS")
        self.assertEqual(self.manager.cloud_service_type, "KeyRing")

    def test_process_keyring_data(self):
        """KeyRing 데이터 처리 테스트"""
        # Given
        keyring_raw_data = {
            "name": "projects/test-project/locations/global/keyRings/test-keyring",
            "createTime": "2024-01-01T12:00:00Z",
            "location_id": "global",
            "location_data": {
                "locationId": "global",
                "displayName": "Global",
                "labels": {},
            },
        }

        # When
        processed_data = self.manager._process_keyring_data(keyring_raw_data)

        # Then
        self.assertIsNotNone(processed_data)
        self.assertEqual(processed_data["keyring_id"], "test-keyring")
        self.assertEqual(processed_data["project_id"], "test-project")
        self.assertEqual(processed_data["location_id"], "global")
        self.assertEqual(processed_data["location_display_name"], "Global")
        self.assertEqual(processed_data["display_name"], "test-keyring (Global)")

    def test_process_crypto_key_data(self):
        """CryptoKey 데이터 처리 테스트"""
        # Given
        crypto_key_raw_data = {
            "name": "projects/test-project/locations/global/keyRings/test-keyring/cryptoKeys/test-key",
            "purpose": "ENCRYPT_DECRYPT",
            "createTime": "2024-01-01T12:00:00Z",
            "nextRotationTime": "2025-01-01T12:00:00Z",
            "primary": {
                "name": "projects/test-project/locations/global/keyRings/test-keyring/cryptoKeys/test-key/cryptoKeyVersions/1",
                "state": "ENABLED",
            },
            "versionTemplate": {
                "protectionLevel": "SOFTWARE",
                "algorithm": "GOOGLE_SYMMETRIC_ENCRYPTION",
            },
        }

        # When
        processed_data = self.manager._process_crypto_key_data(crypto_key_raw_data)

        # Then
        self.assertIsNotNone(processed_data)
        self.assertEqual(processed_data["crypto_key_id"], "test-key")
        self.assertEqual(processed_data["purpose"], "ENCRYPT_DECRYPT")
        self.assertEqual(processed_data["primary_state"], "ENABLED")
        self.assertEqual(processed_data["protection_level"], "SOFTWARE")
        self.assertEqual(processed_data["algorithm"], "GOOGLE_SYMMETRIC_ENCRYPTION")

    def test_process_crypto_key_version_data(self):
        """CryptoKeyVersion 데이터 처리 테스트"""
        # Given
        version_raw_data = {
            "name": "projects/test-project/locations/global/keyRings/test-keyring/cryptoKeys/test-key/cryptoKeyVersions/1",
            "state": "ENABLED",
            "protectionLevel": "SOFTWARE",
            "algorithm": "GOOGLE_SYMMETRIC_ENCRYPTION",
            "createTime": "2024-01-01T12:00:00Z",
            "generateTime": "2024-01-01T12:00:00Z",
            "reimportEligible": False,
        }

        # When
        processed_data = self.manager._process_crypto_key_version_data(version_raw_data)

        # Then
        self.assertIsNotNone(processed_data)
        self.assertEqual(processed_data["version_id"], "1")
        self.assertEqual(processed_data["state"], "ENABLED")
        self.assertEqual(processed_data["protection_level"], "SOFTWARE")
        self.assertEqual(processed_data["algorithm"], "GOOGLE_SYMMETRIC_ENCRYPTION")
        self.assertEqual(processed_data["reimport_eligible"], "False")


class TestKMSKeyRingDataModels(unittest.TestCase):
    """KMS KeyRing 데이터 모델 테스트"""

    def test_crypto_key_version_data_model(self):
        """CryptoKeyVersionData 모델 테스트"""
        # Given
        data = {
            "name": "projects/test-project/locations/global/keyRings/test-keyring/cryptoKeys/test-key/cryptoKeyVersions/1",
            "version_id": "1",
            "state": "ENABLED",
            "create_time": "2024-01-01T12:00:00Z",
            "protection_level": "SOFTWARE",
            "algorithm": "GOOGLE_SYMMETRIC_ENCRYPTION",
        }

        # When
        model = CryptoKeyVersionData(data, strict=False)

        # Then
        self.assertEqual(model.version_id, "1")
        self.assertEqual(model.state, "ENABLED")
        self.assertEqual(model.protection_level, "SOFTWARE")

    def test_crypto_key_data_model(self):
        """CryptoKeyData 모델 테스트"""
        # Given
        data = {
            "name": "projects/test-project/locations/global/keyRings/test-keyring/cryptoKeys/test-key",
            "crypto_key_id": "test-key",
            "purpose": "ENCRYPT_DECRYPT",
            "create_time": "2024-01-01T12:00:00Z",
            "crypto_key_version_count": 2,
            "crypto_key_versions": [],
        }

        # When
        model = CryptoKeyData(data, strict=False)

        # Then
        self.assertEqual(model.crypto_key_id, "test-key")
        self.assertEqual(model.purpose, "ENCRYPT_DECRYPT")
        self.assertEqual(model.crypto_key_version_count, 2)

    def test_kms_keyring_data_model(self):
        """KMSKeyRingData 모델 테스트"""
        # Given
        data = {
            "name": "projects/test-project/locations/global/keyRings/test-keyring",
            "keyring_id": "test-keyring",
            "project_id": "test-project",
            "location_id": "global",
            "location_display_name": "Global",
            "create_time": "2024-01-01T12:00:00Z",
            "crypto_key_count": 3,
            "crypto_keys": [],
        }

        # When
        model = KMSKeyRingData(data, strict=False)

        # Then
        self.assertEqual(model.keyring_id, "test-keyring")
        self.assertEqual(model.project_id, "test-project")
        self.assertEqual(model.location_id, "global")
        self.assertEqual(model.crypto_key_count, 3)

    def test_kms_keyring_data_reference(self):
        """KMSKeyRingData reference 메서드 테스트"""
        # Given
        data = {
            "keyring_id": "test-keyring",
            "project_id": "test-project",
            "location_id": "global",
        }
        model = KMSKeyRingData(data, strict=False)

        # When
        reference = model.reference()

        # Then
        self.assertIn("resource_id", reference)
        self.assertIn("external_link", reference)
        self.assertEqual(reference["resource_id"], "test-project:global:test-keyring")
        self.assertIn("console.cloud.google.com", reference["external_link"])


if __name__ == "__main__":
    unittest.main()
