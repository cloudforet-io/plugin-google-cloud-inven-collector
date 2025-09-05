import logging
from datetime import datetime
from typing import Dict, List
from schematics import Model
from schematics.types import (
    ModelType,
    ListType,
    StringType,
    IntType,
    BooleanType,
    DictType,
)
from spaceone.inventory.libs.schema.cloud_service import BaseResource

_LOGGER = logging.getLogger(__name__)


def convert_datetime(iso_string: str) -> str:
    """ISO 8601 형식의 문자열을 datetime으로 변환"""
    if not iso_string:
        return None
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        _LOGGER.error(f"Failed to convert datetime {iso_string}: {e}")
        return iso_string


def parse_cluster_data(cluster_data: Dict, fleet_info: Dict = None, membership_info: Dict = None, api_version: str = "v1") -> Dict:
    """GKE 클러스터 데이터를 파싱합니다 (v1/v1beta API 통합)."""
    if not cluster_data:
        return {}
    
    # 기본 정보만 추출하여 안전하게 처리
    parsed_data = {
        "name": str(cluster_data.get("name", "")),
        "description": str(cluster_data.get("description", "")),
        "location": str(cluster_data.get("location", "")),
        "projectId": str(cluster_data.get("projectId", "")),
        "status": str(cluster_data.get("status", "")),
        "currentMasterVersion": str(cluster_data.get("currentMasterVersion", "")),
        "currentNodeVersion": str(cluster_data.get("currentNodeVersion", "")),
        "currentNodeCount": str(cluster_data.get("currentNodeCount", "")),
        "createTime": convert_datetime(cluster_data.get("createTime")),
        "updateTime": convert_datetime(cluster_data.get("updateTime")),
        "resourceLabels": {k: str(v) for k, v in cluster_data.get("resourceLabels", {}).items()},
        "api_version": str(api_version),
    }
    
    # 네트워크 설정 - 기본 정보만 추출
    if "networkConfig" in cluster_data:
        network_config = cluster_data["networkConfig"]
        parsed_data["networkConfig"] = {
            "network": str(network_config.get("network", "")),
            "subnetwork": str(network_config.get("subnetwork", "")),
            "enableIntraNodeVisibility": str(network_config.get("enableIntraNodeVisibility", "")),
            "enableL4ilbSubsetting": str(network_config.get("enableL4ilbSubsetting", "")),
        }
        parsed_data["network"] = str(network_config.get("network", ""))
        parsed_data["subnetwork"] = str(network_config.get("subnetwork", ""))
    
    # 클러스터 IP 설정
    if "clusterIpv4Cidr" in cluster_data:
        parsed_data["clusterIpv4Cidr"] = str(cluster_data["clusterIpv4Cidr"])
    if "servicesIpv4Cidr" in cluster_data:
        parsed_data["servicesIpv4Cidr"] = str(cluster_data["servicesIpv4Cidr"])
    
    # 마스터 인증 - 기본 정보만 추출
    if "masterAuth" in cluster_data:
        master_auth = cluster_data["masterAuth"]
        parsed_data["masterAuth"] = {
            "username": str(master_auth.get("username", "")),
            "password": str(master_auth.get("password", "")),
            "clusterCaCertificate": str(master_auth.get("clusterCaCertificate", "")),
        }
    
    # 워크로드 정책
    if "workloadPolicyConfig" in cluster_data:
        workload_policy = cluster_data["workloadPolicyConfig"]
        parsed_data["workloadPolicyConfig"] = {
            "allowNetAdmin": str(workload_policy.get("allowNetAdmin", "")),
        }
    
    # 리소스 사용량 내보내기
    if "resourceUsageExportConfig" in cluster_data:
        export_config = cluster_data["resourceUsageExportConfig"]
        parsed_data["resourceUsageExportConfig"] = {
            "enableNetworkEgressMetering": str(export_config.get("enableNetworkEgressMetering", "")),
        }
    
    # 인증자 그룹
    if "authenticatorGroupsConfig" in cluster_data:
        auth_config = cluster_data["authenticatorGroupsConfig"]
        parsed_data["authenticatorGroupsConfig"] = {
            "securityGroup": str(auth_config.get("securityGroup", "")),
        }
    
    # 모니터링 - 기본 정보만 추출
    if "monitoringConfig" in cluster_data:
        monitoring_config = cluster_data["monitoringConfig"]
        parsed_data["monitoringConfig"] = {
            "monitoringService": str(monitoring_config.get("monitoringService", "")),
            "loggingService": str(monitoring_config.get("loggingService", "")),
        }
    
    # 애드온 - 기본 정보만 추출
    if "addonsConfig" in cluster_data:
        addons_config = cluster_data["addonsConfig"]
        parsed_data["addonsConfig"] = {
            "httpLoadBalancing": str(addons_config.get("httpLoadBalancing", {})),
            "horizontalPodAutoscaling": str(addons_config.get("horizontalPodAutoscaling", {})),
            "kubernetesDashboard": str(addons_config.get("kubernetesDashboard", {})),
            "networkPolicyConfig": str(addons_config.get("networkPolicyConfig", {})),
        }
    
    # NodePool 정보는 별도의 NodePool 서비스에서 처리
    
    # v1beta 전용 정보 (Fleet, Membership)
    if api_version == "v1beta1":
        if fleet_info:
            parsed_data["fleet_info"] = {
                "fleetProject": str(fleet_info.get("fleetProject", "")),
                "membership": str(fleet_info.get("membership", "")),
            }
        if membership_info:
            parsed_data["membership_info"] = {
                "name": str(membership_info.get("name", "")),
                "description": str(membership_info.get("description", "")),
                "state": str(membership_info.get("state", {})),
            }
    
    return parsed_data





class Labels(Model):
    key = StringType()
    value = StringType()


# NodePool 관련 모델들은 별도의 NodePool 서비스에서 정의됨


class NetworkConfig(Model):
    network = StringType(serialize_when_none=False)
    subnetwork = StringType(serialize_when_none=False)
    enable_intra_node_visibility = BooleanType(
        deserialize_from="enableIntraNodeVisibility", serialize_when_none=False
    )
    enable_l4ilb_subsetting = BooleanType(
        deserialize_from="enableL4ilbSubsetting", serialize_when_none=False
    )
    default_snat_status = DictType(StringType, deserialize_from="defaultSnatStatus", serialize_when_none=False)
    network_performance_config = DictType(StringType, deserialize_from="networkPerformanceConfig", serialize_when_none=False)


class MasterAuth(Model):
    username = StringType(serialize_when_none=False)
    password = StringType(serialize_when_none=False)
    client_certificate_config = DictType(StringType, deserialize_from="clientCertificateConfig", serialize_when_none=False)
    cluster_ca_certificate = StringType(deserialize_from="clusterCaCertificate", serialize_when_none=False)
    client_certificate = StringType(deserialize_from="clientCertificate", serialize_when_none=False)
    client_key = StringType(deserialize_from="clientKey", serialize_when_none=False)


class WorkloadPolicy(Model):
    allow_net_admin = BooleanType(deserialize_from="allowNetAdmin", serialize_when_none=False)


class ResourceUsageExportConfig(Model):
    bigquery_destination = DictType(StringType, deserialize_from="bigqueryDestination", serialize_when_none=False)
    enable_network_egress_metering = BooleanType(deserialize_from="enableNetworkEgressMetering", serialize_when_none=False)
    consumption_metering_config = DictType(StringType, deserialize_from="consumptionMeteringConfig", serialize_when_none=False)


class AuthenticatorGroupsConfig(Model):
    security_group = StringType(deserialize_from="securityGroup", serialize_when_none=False)


class MonitoringConfig(Model):
    monitoring_service = StringType(deserialize_from="monitoringService", serialize_when_none=False)
    logging_service = StringType(deserialize_from="loggingService", serialize_when_none=False)
    managed_prometheus_config = DictType(StringType, deserialize_from="managedPrometheusConfig", serialize_when_none=False)


class AddonsConfig(Model):
    http_load_balancing = DictType(StringType, deserialize_from="httpLoadBalancing", serialize_when_none=False)
    horizontal_pod_autoscaling = DictType(StringType, deserialize_from="horizontalPodAutoscaling", serialize_when_none=False)
    kubernetes_dashboard = DictType(StringType, deserialize_from="kubernetesDashboard", serialize_when_none=False)
    network_policy_config = DictType(StringType, deserialize_from="networkPolicyConfig", serialize_when_none=False)
    cloud_run_config = DictType(StringType, deserialize_from="cloudRunConfig", serialize_when_none=False)
    dns_cache_config = DictType(StringType, deserialize_from="dnsCacheConfig", serialize_when_none=False)
    config_connector_config = DictType(StringType, deserialize_from="configConnectorConfig", serialize_when_none=False)
    gce_persistent_disk_csi_driver_config = DictType(StringType, deserialize_from="gcePersistentDiskCsiDriverConfig", serialize_when_none=False)
    gcp_filestore_csi_driver_config = DictType(StringType, deserialize_from="gcpFilestoreCsiDriverConfig", serialize_when_none=False)
    gke_backup_agent_config = DictType(StringType, deserialize_from="gkeBackupAgentConfig", serialize_when_none=False)
    gcs_fuse_csi_driver_config = DictType(StringType, deserialize_from="gcsFuseCsiDriverConfig", serialize_when_none=False)
    stateful_ha_config = DictType(StringType, deserialize_from="statefulHaConfig", serialize_when_none=False)


class FleetInfo(Model):
    fleet_project = StringType(deserialize_from="fleetProject", serialize_when_none=False)
    membership = StringType(serialize_when_none=False)


class MembershipInfo(Model):
    name = StringType(serialize_when_none=False)
    description = StringType(serialize_when_none=False)
    state = DictType(StringType, serialize_when_none=False)
    create_time = StringType(deserialize_from="createTime", serialize_when_none=False)
    update_time = StringType(deserialize_from="updateTime", serialize_when_none=False)


class GKECluster(BaseResource):
    """GKE Cluster 데이터 모델"""
    name = StringType(serialize_when_none=False)
    description = StringType(serialize_when_none=False)
    location = StringType(serialize_when_none=False)
    project_id = StringType(deserialize_from="projectId", serialize_when_none=False)
    status = StringType(serialize_when_none=False)
    current_master_version = StringType(deserialize_from="currentMasterVersion", serialize_when_none=False)
    current_node_version = StringType(deserialize_from="currentNodeVersion", serialize_when_none=False)
    current_node_count = IntType(deserialize_from="currentNodeCount", serialize_when_none=False)
    create_time = StringType(deserialize_from="createTime", serialize_when_none=False)
    update_time = StringType(deserialize_from="updateTime", serialize_when_none=False)
    resource_labels = DictType(StringType, deserialize_from="resourceLabels", serialize_when_none=False)
    api_version = StringType(serialize_when_none=False)
    
    # Network
    network = StringType(serialize_when_none=False)
    subnetwork = StringType(serialize_when_none=False)
    cluster_ipv4_cidr = StringType(deserialize_from="clusterIpv4Cidr", serialize_when_none=False)
    services_ipv4_cidr = StringType(deserialize_from="servicesIpv4Cidr", serialize_when_none=False)
    network_config = DictType(StringType, deserialize_from="networkConfig", serialize_when_none=False)
    
    # NodePool 정보는 별도의 NodePool 서비스에서 관리
    
    # Configurations
    master_auth = DictType(StringType, deserialize_from="masterAuth", serialize_when_none=False)
    workload_policy = DictType(StringType, deserialize_from="workloadPolicyConfig", serialize_when_none=False)
    resource_usage_export_config = DictType(StringType, deserialize_from="resourceUsageExportConfig", serialize_when_none=False)
    authenticator_groups_config = DictType(StringType, deserialize_from="authenticatorGroupsConfig", serialize_when_none=False)
    monitoring_config = DictType(StringType, deserialize_from="monitoringConfig", serialize_when_none=False)
    addons_config = DictType(StringType, deserialize_from="addonsConfig", serialize_when_none=False)
    
    # v1beta1 specific
    fleet_info = DictType(StringType, serialize_when_none=False)
    membership_info = DictType(StringType, serialize_when_none=False)

    def reference(self):
        return {
            "resource_id": self.self_link,
            "external_link": f"https://console.cloud.google.com/kubernetes/clusters/details/{self.location}/{self.name}?project={self.project_id}",
        }



