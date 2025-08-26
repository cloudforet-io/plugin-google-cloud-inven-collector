import os

from spaceone.inventory.conf.cloud_service_conf import ASSET_URL
from spaceone.inventory.libs.common_parser import get_data_from_yaml
from spaceone.inventory.libs.schema.cloud_service_type import (
    CloudServiceTypeMeta,
    CloudServiceTypeResource,
    CloudServiceTypeResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    EnumDyField,
    SearchField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_widget import ChartWidget

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, "widget/total_count.yaml")
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yaml")
count_by_project_conf = os.path.join(current_dir, "widget/count_by_project.yaml")

cst_cluster = CloudServiceTypeResource()
cst_cluster.name = "Cluster"
cst_cluster.provider = "google_cloud"
cst_cluster.group = "Dataproc"
cst_cluster.service_code = "dataproc"
cst_cluster.labels = ["Analytics", "Compute"]
cst_cluster.is_primary = True
cst_cluster.is_major = True
cst_cluster.resource_type = "inventory.CloudService"

cst_cluster.metadata = CloudServiceTypeMeta.set_meta(
    fields=[
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
        TextDyField.data_source(
            "Image Version", "data.config.software_config.image_version"
        ),
        TextDyField.data_source(
            "Master Instances", "data.config.master_config.num_instances"
        ),
        TextDyField.data_source(
            "Worker Instances", "data.config.worker_config.num_instances"
        ),
        TextDyField.data_source("Project", "data.project_id"),
    ],
    search=[
        SearchField.set(name="Cluster Name", key="data.cluster_name"),
        SearchField.set(name="Status", key="data.status.state"),
        SearchField.set(name="Location", key="data.location"),
        SearchField.set(name="Project ID", key="data.project_id"),
        SearchField.set(
            name="Image Version", key="data.config.software_config.image_version"
        ),
        SearchField.set(
            name="Master Machine Type", key="data.config.master_config.machine_type_uri"
        ),
        SearchField.set(
            name="Worker Machine Type", key="data.config.worker_config.machine_type_uri"
        ),
    ],
    widget=[
        ChartWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf)),
    ],
)

cst_cluster.tags = {
    "spaceone:icon": f"{ASSET_URL}/google_dataproc.svg",
}

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_cluster}),
]
