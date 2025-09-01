"""KubernetesEngine Node Group 매니저들의 단위 테스트."""

import unittest
from unittest.mock import Mock, patch
from typing import Dict, Any

# KubernetesEngine Node Group 매니저들 임포트
from spaceone.inventory.manager.kubernetes_engine.nodegroup_v1_manager import GKENodeGroupV1Manager
from spaceone.inventory.manager.kubernetes_engine.nodegroup_v1beta_manager import GKENodeGroupV1BetaManager


class TestGKENodeGroupV1Manager(unittest.TestCase):
    """GKENodeGroupV1Manager 테스트 클래스."""

    def setUp(self):
        """테스트 설정."""
        self.manager = GKENodeGroupV1Manager()
        self.mock_params = {
            "secret_data": {
                "project_id": "test-project-id"
            }
        }

    def test_list_node_groups_success(self):
        """노드 그룹 목록 조회 성공 테스트."""
        with patch.object(self.manager, 'locator') as mock_locator:
            mock_connector = Mock()
            mock_connector.list_clusters.return_value = [
                {
                    "name": "cluster1",
                    "location": "us-central1",
                    "projectId": "test-project-id"
                }
            ]
            mock_connector.list_node_pools.return_value = [
                {
                    "name": "pool1",
                    "version": "1.24.0",
                    "status": "RUNNING"
                },
                {
                    "name": "pool2", 
                    "version": "1.24.0",
                    "status": "RUNNING"
                }
            ]
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.list_node_groups(self.mock_params)
            
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["clusterName"], "cluster1")
            self.assertEqual(result[0]["clusterLocation"], "us-central1")

    def test_get_node_group_success(self):
        """노드 그룹 조회 성공 테스트."""
        with patch.object(self.manager, 'locator') as mock_locator:
            mock_connector = Mock()
            mock_connector.list_node_pools.return_value = [
                {
                    "name": "test-pool",
                    "version": "1.24.0",
                    "status": "RUNNING"
                }
            ]
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.get_node_group("test-cluster", "us-central1", "test-pool", self.mock_params)
            
            self.assertIsInstance(result, dict)
            self.assertEqual(result["name"], "test-pool")
            self.assertEqual(result["clusterName"], "test-cluster")

    def test_list_node_group_operations_success(self):
        """노드 그룹 작업 목록 조회 성공 테스트."""
        with patch.object(self.manager, 'locator') as mock_locator:
            mock_connector = Mock()
            mock_connector.list_operations.return_value = [
                {"name": "op1", "operationType": "nodePool"},
                {"name": "op2", "operationType": "nodePool"},
                {"name": "op3", "operationType": "CLUSTER_UPGRADE"}
            ]
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.list_node_group_operations(self.mock_params)
            
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)  # nodePool 관련 작업만 필터링됨
            self.assertTrue(all("nodePool" in op.get("operationType", "") for op in result))

    def test_get_node_group_metrics_success(self):
        """노드 그룹 메트릭 조회 성공 테스트."""
        result = self.manager.get_node_group_metrics("test-cluster", "us-central1", "test-pool", self.mock_params)
        
        self.assertIsInstance(result, dict)
        self.assertIn("cpu_usage", result)
        self.assertIn("memory_usage", result)
        self.assertIn("disk_usage", result)
        self.assertIn("node_count", result)


class TestGKENodeGroupV1BetaManager(unittest.TestCase):
    """GKENodeGroupV1BetaManager 테스트 클래스."""

    def setUp(self):
        """테스트 설정."""
        self.manager = GKENodeGroupV1BetaManager()
        self.mock_params = {
            "secret_data": {
                "project_id": "test-project-id"
            }
        }

    def test_list_node_groups_success(self):
        """노드 그룹 목록 조회 성공 테스트 (v1beta1)."""
        with patch.object(self.manager, 'locator') as mock_locator:
            mock_connector = Mock()
            mock_connector.list_clusters.return_value = [
                {
                    "name": "cluster1",
                    "location": "us-central1",
                    "projectId": "test-project-id"
                }
            ]
            mock_connector.list_node_pools.return_value = [
                {
                    "name": "pool1",
                    "version": "1.24.0",
                    "status": "RUNNING"
                },
                {
                    "name": "pool2", 
                    "version": "1.24.0",
                    "status": "RUNNING"
                }
            ]
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.list_node_groups(self.mock_params)
            
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["clusterName"], "cluster1")
            self.assertEqual(result[0]["clusterLocation"], "us-central1")

    def test_get_node_group_success(self):
        """노드 그룹 조회 성공 테스트 (v1beta1)."""
        with patch.object(self.manager, 'locator') as mock_locator:
            mock_connector = Mock()
            mock_connector.list_node_pools.return_value = [
                {
                    "name": "test-pool",
                    "version": "1.24.0",
                    "status": "RUNNING"
                }
            ]
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.get_node_group("test-cluster", "us-central1", "test-pool", self.mock_params)
            
            self.assertIsInstance(result, dict)
            self.assertEqual(result["name"], "test-pool")
            self.assertEqual(result["clusterName"], "test-cluster")

    def test_list_node_group_operations_success(self):
        """노드 그룹 작업 목록 조회 성공 테스트 (v1beta1)."""
        with patch.object(self.manager, 'locator') as mock_locator:
            mock_connector = Mock()
            mock_connector.list_operations.return_value = [
                {"name": "op1", "operationType": "nodePool"},
                {"name": "op2", "operationType": "nodePool"},
                {"name": "op3", "operationType": "CLUSTER_UPGRADE"}
            ]
            mock_locator.get_connector.return_value = mock_connector

            result = self.manager.list_node_group_operations(self.mock_params)
            
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)  # nodePool 관련 작업만 필터링됨
            self.assertTrue(all("nodePool" in op.get("operationType", "") for op in result))

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

    def test_get_node_group_metrics_success(self):
        """노드 그룹 메트릭 조회 성공 테스트 (v1beta1)."""
        result = self.manager.get_node_group_metrics("test-cluster", "us-central1", "test-pool", self.mock_params)
        
        self.assertIsInstance(result, dict)
        self.assertIn("cpu_usage", result)
        self.assertIn("memory_usage", result)
        self.assertIn("disk_usage", result)
        self.assertIn("node_count", result)


if __name__ == "__main__":
    unittest.main()
