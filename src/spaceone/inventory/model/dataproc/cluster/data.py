"""
이 모듈은 다양한 구성 요소의 상세 설정 및 상태를 나타내는 Dataproc 클러스터의 데이터 모델을 정의합니다.
"""

from typing import Dict

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


class AutoscalingPolicy(Model):
    """Dataproc 오토스케일링 정책을 나타냅니다."""

    id = StringType()
    name = StringType()
    secondary_worker_config = DictType(StringType())
    basic_algorithm = DictType(StringType())


class WorkflowTemplate(Model):
    """Dataproc 워크플로 템플릿을 나타냅니다."""

    id = StringType()
    name = StringType()
    version = IntType()
    create_time = DateTimeType()
    update_time = DateTimeType()
    labels = DictType(StringType())
    placement = DictType(StringType())
    jobs = ListType(DictType(StringType()))


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


class JobReference(Model):
    """Dataproc 작업 참조 정보를 나타냅니다."""

    project_id = StringType()
    job_id = StringType()


class JobStatus(Model):
    """Dataproc 작업 상태를 나타냅니다."""

    state = StringType()
    detail = StringType()
    state_start_time = DateTimeType()
    substate = StringType()


class JobPlacement(Model):
    """Dataproc 작업 배치 정보를 나타냅니다."""

    cluster_name = StringType()
    cluster_uuid = StringType()


class DataprocJob(Model):
    """Dataproc 작업 정보를 나타냅니다."""

    reference = ModelType(JobReference)
    placement = ModelType(JobPlacement)
    status = ModelType(JobStatus)
    labels = DictType(StringType())
    driver_output_resource_uri = StringType()
    driver_control_files_uri = StringType()
    job_uuid = StringType()


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
    jobs = ListType(ModelType(DataprocJob))
    workflow_templates = ListType(ModelType(WorkflowTemplate))
    autoscaling_policies = ListType(ModelType(AutoscalingPolicy))

    def reference(self) -> Dict[str, str]:
        """
        클러스터 참조 정보를 생성합니다.

        Returns:
            리소스 ID와 외부 링크를 포함한 참조 정보
        """
        return {
            "resource_id": str(self.cluster_uuid or ""),
            "external_link": f"https://console.cloud.google.com/dataproc/clusters/details/{self.location}/{self.cluster_name}?project={self.project_id}",
        }
