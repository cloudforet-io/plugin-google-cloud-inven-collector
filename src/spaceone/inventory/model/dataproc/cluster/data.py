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

from spaceone.inventory.libs.schema.google_cloud_logging import (
    GoogleCloudLoggingModel,
)
from spaceone.inventory.libs.schema.google_cloud_monitoring import (
    GoogleCloudMonitoringModel,
)


class DiskConfig(Model):
    """Dataproc 클러스터 인스턴스의 디스크 구성을 나타냅니다."""

    boot_disk_type = StringType()
    boot_disk_size_gb = IntType()


class InstanceGroupConfig(Model):
    """Dataproc 클러스터의 인스턴스 그룹에 대한 구성을 나타냅니다."""

    num_instances = StringType()
    instance_names = ListType(StringType())
    image_uri = StringType()
    machine_type_uri = StringType()
    disk_config = ModelType(DiskConfig)
    is_preemptible = BooleanType()
    preemptibility = StringType()  # 가변형 VM 여부 (PREEMPTIBLE/NON_PREEMPTIBLE)
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


class LifecycleConfig(Model):
    """Dataproc 클러스터의 생명주기 구성을 나타냅니다."""

    auto_delete_time = StringType()
    auto_delete_ttl = StringType()
    idle_delete_ttl = StringType()


class ClusterConfig(Model):
    """Dataproc 클러스터의 전체적인 구성을 나타냅니다."""

    config_bucket = StringType()
    temp_bucket = StringType()
    gce_cluster_config = ModelType(GceClusterConfig)
    master_config = ModelType(InstanceGroupConfig)
    worker_config = ModelType(InstanceGroupConfig)
    software_config = ModelType(SoftwareConfig)
    initialization_actions = ListType(DictType(StringType()))
    encryption_config = DictType(StringType())
    autoscaling_policy = StringType()
    security_config = DictType(StringType())
    lifecycle_config = ModelType(LifecycleConfig)


class AutoscalingPolicy(Model):
    """Dataproc 오토스케일링 정책을 나타냅니다."""

    id = StringType()
    name = StringType()
    worker_config = DictType(StringType())
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

    name = StringType()
    project_id = StringType()
    cluster_name = StringType()
    cluster_uuid = StringType()
    config = ModelType(ClusterConfig)
    labels = ListType(DictType(StringType()))
    status = ModelType(ClusterStatus)
    status_history = ListType(ModelType(ClusterStatus))
    metrics = ModelType(ClusterMetrics)
    location = StringType()
    jobs = ListType(ModelType(DataprocJob))
    workflow_templates = ListType(ModelType(WorkflowTemplate))
    autoscaling_policies = ListType(ModelType(AutoscalingPolicy))
    # Monitoring data
    google_cloud_monitoring = ModelType(
        GoogleCloudMonitoringModel, serialize_when_none=False
    )
    # Logging data
    google_cloud_logging = ModelType(GoogleCloudLoggingModel, serialize_when_none=False)

    def reference(self) -> Dict[str, str]:
        """
        클러스터 참조 정보를 생성합니다.

        Returns:
            리소스 ID와 외부 링크를 포함한 참조 정보
        """
        return {
            "resource_id": f"https://dataproc.googleapis.com/v1/projects/{self.project_id}/regions/{self.location}/clusters/{self.cluster_name}",
            # "external_link": f"https://console.cloud.google.com/dataproc/clusters?project={self.project_id}",
            "external_link": f"https://console.cloud.google.com/dataproc/clusters/{self.cluster_name}/monitoring?region={self.location}&project={self.project_id}",
        }
