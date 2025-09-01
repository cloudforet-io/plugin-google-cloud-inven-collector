"""KubernetesEngine 도메인 매니저들의 단위 테스트."""

import unittest
from unittest.mock import Mock, patch
from typing import Dict, Any

# KubernetesEngine 매니저들 임포트
from spaceone.inventory.manager.kubernetes_engine.cluster_v1_manager import GKEClusterV1Manager
from spaceone.inventory.manager.kubernetes_engine.cluster_v1beta_manager import GKEClusterV1BetaManager


class TestGKEClusterV1Manager(unittest.TestCase):
    """GKEClusterV1Manager 테스트 클래스."""

    def setUp(self):
        """테스트 설정."""
        self.manager = GKEClusterV1Manager()
        self.mock_params = {
            "secret_data": {
                "project_id": "test-project-id"
            }
        }

    def test_list_clusters_success(self):
        """클러스터 목록 조회 성공 테스트."""
        with patch.object(self.manager, 'locator') as mock_locator:
            mock_connector = Mock()
            mock_connector.list_clusters.return_value = [
                {"name": "cluster1", "location": "us-central1"},
                {"name": "cluster2", "location": "us-east1"}
            ]
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.list_clusters(self.mock_params)
            
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)

    def test_list_node_pools_success(self):
        """노드풀 목록 조회 성공 테스트."""
        with patch.object(self.manager, 'locator') as mock_locator:
            mock_connector = Mock()
            mock_connector.list_node_pools.return_value = [
                {"name": "pool1", "config": {"machineType": "e2-medium"}},
                {"name": "pool2", "config": {"machineType": "e2-standard-2"}}
            ]
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.list_node_pools("test-cluster", "us-central1", self.mock_params)
            
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)

    def test_get_cluster_success(self):
        """클러스터 조회 성공 테스트."""
        with patch.object(self.manager, 'locator') as mock_locator:
            mock_connector = Mock()
            mock_connector.get_cluster.return_value = {
                "name": "test-cluster",
                "location": "us-central1",
                "status": "RUNNING"
            }
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.get_cluster("test-cluster", "us-central1", self.mock_params)
            
            self.assertIsInstance(result, dict)
            self.assertEqual(result["name"], "test-cluster")

    def test_list_operations_success(self):
        """작업 목록 조회 성공 테스트."""
        with patch.object(self.manager, 'locator') as mock_locator:
            mock_connector = Mock()
            mock_connector.list_operations.return_value = [
                {"name": "op1", "status": "DONE"},
                {"name": "op2", "status": "RUNNING"}
            ]
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.list_operations(self.mock_params)
            
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)

    def test_get_cluster_empty_result(self):
        """클러스터 조회 결과가 비어있는 경우 테스트."""
        with patch.object(self.manager, 'locator') as mock_locator:
            mock_connector = Mock()
            mock_connector.get_cluster.return_value = None
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.get_cluster("test-cluster", "us-central1", self.mock_params)
            
            self.assertEqual(result, {})


class TestGKEClusterV1BetaManager(unittest.TestCase):
    """GKEClusterV1BetaManager 테스트 클래스."""

    def setUp(self):
        """테스트 설정."""
        self.manager = GKEClusterV1BetaManager()
        self.mock_params = {
            "secret_data": {
                "project_id": "test-project-id"
            }
        }

    def test_list_clusters_success(self):
        """클러스터 목록 조회 성공 테스트 (v1beta1)."""
        with patch.object(self.manager, 'locator') as mock_locator:
            mock_connector = Mock()
            mock_connector.list_clusters.return_value = [
                {"name": "cluster1", "location": "us-central1"},
                {"name": "cluster2", "location": "us-east1"}
            ]
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.list_clusters(self.mock_params)
            
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)

    def test_list_node_pools_success(self):
        """노드풀 목록 조회 성공 테스트 (v1beta1)."""
        with patch.object(self.manager, 'locator') as mock_locator:
            mock_connector = Mock()
            mock_connector.list_node_pools.return_value = [
                {"name": "pool1", "config": {"machineType": "e2-medium"}},
                {"name": "pool2", "config": {"machineType": "e2-standard-2"}}
            ]
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.list_node_pools("test-cluster", "us-central1", self.mock_params)
            
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)

    def test_get_cluster_success(self):
        """클러스터 조회 성공 테스트 (v1beta1)."""
        with patch.object(self.manager, 'locator') as mock_locator:
            mock_connector = Mock()
            mock_connector.get_cluster.return_value = {
                "name": "test-cluster",
                "location": "us-central1",
                "status": "RUNNING"
            }
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.get_cluster("test-cluster", "us-central1", self.mock_params)
            
            self.assertIsInstance(result, dict)
            self.assertEqual(result["name"], "test-cluster")

    def test_list_operations_success(self):
        """작업 목록 조회 성공 테스트 (v1beta1)."""
        with patch.object(self.manager, 'locator') as mock_locator:
            mock_connector = Mock()
            mock_connector.list_operations.return_value = [
                {"name": "op1", "status": "DONE"},
                {"name": "op2", "status": "RUNNING"}
            ]
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.list_operations(self.mock_params)
            
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)

    def test_list_fleets_success(self):
        """Fleet 목록 조회 성공 테스트 (v1beta1)."""
        with patch.object(self.manager, 'locator') as mock_locator:
            mock_connector = Mock()
            mock_connector.list_fleets.return_value = [
                {"name": "fleet1", "displayName": "Fleet 1"},
                {"name": "fleet2", "displayName": "Fleet 2"}
            ]
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.list_fleets(self.mock_params)
            
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)

    def test_list_memberships_success(self):
        """Membership 목록 조회 성공 테스트 (v1beta1)."""
        with patch.object(self.manager, 'locator') as mock_locator:
            mock_connector = Mock()
            mock_connector.list_memberships.return_value = [
                {"name": "membership1", "endpoint": {"gkeCluster": {"resourceLink": "link1"}}},
                {"name": "membership2", "endpoint": {"gkeCluster": {"resourceLink": "link2"}}}
            ]
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.list_memberships(self.mock_params)
            
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)


if __name__ == "__main__":
    unittest.main()
