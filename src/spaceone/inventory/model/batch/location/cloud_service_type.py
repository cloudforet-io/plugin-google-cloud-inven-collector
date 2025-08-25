import os

from spaceone.inventory.conf.cloud_service_conf import *
from spaceone.inventory.libs.common_parser import *
from spaceone.inventory.libs.schema.cloud_service_type import (
    CloudServiceTypeMeta,
    CloudServiceTypeResource,
    CloudServiceTypeResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    SearchField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_widget import (
    CardWidget,
    ChartWidget,
)

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, "widget/total_count.yml")
count_by_account_conf = os.path.join(current_dir, "widget/count_by_account.yml")
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yml")

cst_batch_location = CloudServiceTypeResource()
cst_batch_location.name = "Location"
cst_batch_location.provider = "google_cloud"
cst_batch_location.group = "Batch"
cst_batch_location.service_code = "Batch"
cst_batch_location.labels = ["Compute", "Batch"]
cst_batch_location.is_primary = True
cst_batch_location.is_major = True
cst_batch_location.tags = {
    "spaceone:icon": f"{ASSET_URL}/Batch.svg",
}

cst_batch_location._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Location ID", "data.location_id"),
        TextDyField.data_source("Display Name", "data.display_name"),
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("Project ID", "data.project_id"),
        TextDyField.data_source("Job Count", "data.job_count"),
        TextDyField.data_source("Account ID", "account", options={"is_optional": True}),
    ],
    search=[
        SearchField.set(name="Location ID", key="data.location_id"),
        SearchField.set(name="Display Name", key="data.display_name"),
        SearchField.set(name="Project ID", key="data.project_id"),
        SearchField.set(name="Account ID", key="account"),
        SearchField.set(
            name="Project Group",
            key="project_group_id",
            reference="identity.ProjectGroup",
        ),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_account_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_batch_location}),
]
