"""
이 모듈은 다양한 구성 요소의 상세 설정 및 상태를 나타내는 Dataproc 클러스터의 데이터 모델을 정의합니다.
"""
from schematics import Model
from schematics.types import (
    BooleanType,
    DateTimeType,
    DictType,
    IntType,
    ListType,
    ModelType,
    StringType,
)


class DiskConfig(Model):
    """Dataproc 클러스터 인스턴스의 디스크 구성을 나타냅니다."""
    boot_disk_type = StringType()
    boot_disk_size_gb = IntType()
    num_local_ssds = IntType()


class InstanceGroupConfig(Model):
    """Dataproc 클러스터의 인스턴스 그룹에 대한 구성을 나타냅니다."""
    num_instances = StringType()
    instance_names = ListType(StringType())
    image_uri = StringType()
    machine_type_uri = StringType()
    disk_config = ModelType(DiskConfig)
    is_preemptible = BooleanType()
    min_cpu_platform = StringType()


class GceClusterConfig(Model):
    """Dataproc 클러스터의 Google Compute Engine 구성을 나타냅니다."""
    zone_uri = StringType()
    network_uri = StringType()
    subnetwork_uri = StringType()
    internal_ip_only = StringType()
    service_account = StringType()
    service_account_scopes = ListType(StringType())
    tags = ListType(StringType())
    metadata = DictType(StringType())


class SoftwareConfig(Model):
    """Dataproc 클러스터의 소프트웨어 구성을 나타냅니다."""
    image_version = StringType()
    properties = DictType(StringType())
    optional_components = ListType(StringType())


class ClusterConfig(Model):
    """Dataproc 클러스터의 전체적인 구성을 나타냅니다."""
    config_bucket = StringType()
    temp_bucket = StringType()
    gce_cluster_config = ModelType(GceClusterConfig)
    master_config = ModelType(InstanceGroupConfig)
    worker_config = ModelType(InstanceGroupConfig)
    secondary_worker_config = ModelType(InstanceGroupConfig)
    software_config = ModelType(SoftwareConfig)
    initialization_actions = ListType(DictType(StringType()))
    encryption_config = DictType(StringType())
    autoscaling_policy = StringType()
    security_config = DictType(StringType())
    lifecycle_config = DictType(StringType())


class ClusterStatus(Model):
    """Dataproc 클러스터의 상태를 나타냅니다."""
    state = StringType()
    detail = StringType()
    state_start_time = DateTimeType()
    substate = StringType()


class ClusterMetrics(Model):
    """Dataproc 클러스터의 메트릭을 나타냅니다."""
    hdfs_metrics = DictType(StringType())
    yarn_metrics = DictType(StringType())


class DataprocCluster(Model):
    """Dataproc 클러스터 리소스의 기본 데이터 모델입니다."""
    project_id = StringType()
    cluster_name = StringType()
    cluster_uuid = StringType()
    config = ModelType(ClusterConfig)
    labels = DictType(StringType())
    status = ModelType(ClusterStatus)
    status_history = ListType(ModelType(ClusterStatus))
    metrics = ModelType(ClusterMetrics)
    location = StringType()

    def reference(self):
        return {
            "resource_id": self.cluster_uuid,
            "external_link": f"https://console.cloud.google.com/dataproc/clusters/details/{self.location}/{self.cluster_name}?project={self.project_id}",
        }
