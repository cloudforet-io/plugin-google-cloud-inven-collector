"""
이 모듈은 SpaceONE 콘솔을 위한 메타데이터를 포함하여, Dataproc 클러스터의 클라우드 서비스 리소스 및 응답 모델을 정의합니다.
"""

from schematics.types import ModelType, PolyModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    DateTimeDyField,
    EnumDyField,
    ListDyField,
    SizeField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    ListDynamicLayout,
)
from spaceone.inventory.model.dataproc.cluster.data import DataprocCluster

"""
CLUSTER
"""
cluster_info_meta = ItemDynamicLayout.set_fields(
    "Cluster Overview",
    fields=[
        TextDyField.data_source("Name", "data.cluster_name"),
        TextDyField.data_source("UUID", "data.cluster_uuid"),
        EnumDyField.data_source(
            "Status",
            "data.status.state",
            default_state={
                "safe": ["RUNNING"],
                "warning": ["CREATING", "UPDATING", "DELETING", "STOPPING"],
                "alert": ["ERROR", "ERROR_DUE_TO_UPDATE", "STOPPED"],
            },
        ),
        TextDyField.data_source("Location", "data.location"),
        TextDyField.data_source("Project ID", "data.project_id"),
        DateTimeDyField.data_source("Created", "data.status.state_start_time"),
    ],
)

# Configuration 섹션들을 개별적으로 정의
cluster_basic_config_meta = ItemDynamicLayout.set_fields(
    "Basic Configuration",
    fields=[
        TextDyField.data_source("Config Bucket", "data.config.config_bucket"),
        TextDyField.data_source("Temp Bucket", "data.config.temp_bucket"),
        TextDyField.data_source(
            "Image Version", "data.config.software_config.image_version"
        ),
        ListDyField.data_source(
            "Optional Components", "data.config.software_config.optional_components"
        ),
    ],
)

cluster_network_config_meta = ItemDynamicLayout.set_fields(
    "Network Configuration",
    fields=[
        TextDyField.data_source("Zone", "data.config.gce_cluster_config.zone_uri"),
        TextDyField.data_source(
            "Network", "data.config.gce_cluster_config.network_uri"
        ),
        TextDyField.data_source(
            "Subnetwork", "data.config.gce_cluster_config.subnetwork_uri"
        ),
        TextDyField.data_source(
            "Internal IP Only", "data.config.gce_cluster_config.internal_ip_only"
        ),
        TextDyField.data_source(
            "Service Account", "data.config.gce_cluster_config.service_account"
        ),
    ],
)

# Configuration을 ListDynamicLayout으로 통합
cluster_config_meta = ListDynamicLayout.set_layouts(
    "Configuration", layouts=[cluster_basic_config_meta, cluster_network_config_meta]
)

cluster_master_config_meta = ItemDynamicLayout.set_fields(
    "Master Configuration",
    fields=[
        TextDyField.data_source("Instances", "data.config.master_config.num_instances"),
        TextDyField.data_source(
            "Machine Type", "data.config.master_config.machine_type_uri"
        ),
        TextDyField.data_source("Image URI", "data.config.master_config.image_uri"),
        TextDyField.data_source(
            "Boot Disk Type", "data.config.master_config.disk_config.boot_disk_type"
        ),
        SizeField.data_source(
            "Boot Disk Size", "data.config.master_config.disk_config.boot_disk_size_gb"
        ),
        TextDyField.data_source(
            "Min CPU Platform", "data.config.master_config.min_cpu_platform"
        ),
        EnumDyField.data_source(
            "Preemptibility",
            "data.config.master_config.preemptibility",
            default_state={
                "safe": ["NON_PREEMPTIBLE"],
                "warning": ["PREEMPTIBLE"],
            },
        ),
    ],
)

cluster_worker_config_meta = ItemDynamicLayout.set_fields(
    "Worker Configuration",
    fields=[
        TextDyField.data_source("Instances", "data.config.worker_config.num_instances"),
        TextDyField.data_source(
            "Machine Type", "data.config.worker_config.machine_type_uri"
        ),
        TextDyField.data_source("Image URI", "data.config.worker_config.image_uri"),
        TextDyField.data_source(
            "Boot Disk Type", "data.config.worker_config.disk_config.boot_disk_type"
        ),
        SizeField.data_source(
            "Boot Disk Size", "data.config.worker_config.disk_config.boot_disk_size_gb"
        ),
        TextDyField.data_source(
            "Min CPU Platform", "data.config.worker_config.min_cpu_platform"
        ),
        EnumDyField.data_source(
            "Preemptibility",
            "data.config.worker_config.preemptibility",
            default_state={
                "safe": ["NON_PREEMPTIBLE"],
                "warning": ["PREEMPTIBLE"],
            },
        ),
    ],
)

cluster_labels_meta = ItemDynamicLayout.set_fields(
    "Labels",
    root_path="data.labels",
    fields=[
        TextDyField.data_source("Key", "key"),
        TextDyField.data_source("Value", "value"),
    ],
)

cluster_meta = CloudServiceMeta.set_layouts(
    [
        cluster_info_meta,
        cluster_config_meta,
        cluster_master_config_meta,
        cluster_worker_config_meta,
        cluster_labels_meta,
    ]
)


class DataprocClusterResource(CloudServiceResource):
    cloud_service_type = StringType(default="Cluster")
    cloud_service_group = StringType(default="Dataproc")
    data = ModelType(DataprocCluster)
    _metadata = ModelType(
        CloudServiceMeta, default=cluster_meta, serialized_name="metadata"
    )


class DataprocClusterResponse(CloudServiceResponse):
    resource = PolyModelType(DataprocClusterResource)
