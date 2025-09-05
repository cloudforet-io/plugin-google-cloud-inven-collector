import os

from spaceone.inventory.conf.cloud_service_conf import ASSET_URL
from spaceone.inventory.libs.schema.cloud_service_type import (
    CloudServiceTypeMeta,
    CloudServiceTypeResource,
    CloudServiceTypeResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    DateTimeDyField,
    SearchField,
    TextDyField,
)

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, "widget/total_count.yml")
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yml")
count_by_project_conf = os.path.join(current_dir, "widget/count_by_project.yml")

"""
CONFIGURATION V1
"""
cst_configuration_v1 = CloudServiceTypeResource()
cst_configuration_v1.name = "ConfigurationV1"
cst_configuration_v1.provider = "google_cloud"
cst_configuration_v1.group = "CloudRun"
cst_configuration_v1.labels = ["Compute", "Container"]
cst_configuration_v1.is_primary = True
cst_configuration_v1.service_code = "Cloud Run"
cst_configuration_v1.tags = {
    "spaceone:icon": f"{ASSET_URL}/google_cloud/icons/Cloud-Run.svg"
}

cst_configuration_v1._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("Kind", "data.kind"),
        TextDyField.data_source("Namespace", "data.metadata.namespace"),
        DateTimeDyField.data_source("Created", "data.metadata.creation_timestamp"),
        TextDyField.data_source("Latest Ready Revision", "data.status.latest_ready_revision_name"),
        TextDyField.data_source("Latest Created Revision", "data.status.latest_created_revision_name"),
    ],
    search=[
        SearchField.set(name="Name", key="data.name"),
        SearchField.set(name="Kind", key="data.kind"),
        SearchField.set(name="Namespace", key="data.metadata.namespace"),
        SearchField.set(name="Latest Ready Revision", key="data.status.latest_ready_revision_name"),
        SearchField.set(name="Project", key="data.project"),
        SearchField.set(name="Location", key="data.location"),
    ],
    widget=[
        # CardWidget.set(**get_data_from_yaml(total_count_conf)),
        # ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        # ChartWidget.set(**get_data_from_yaml(count_by_project_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_configuration_v1}),
]
