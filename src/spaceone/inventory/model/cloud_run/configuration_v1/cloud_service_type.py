import os

from spaceone.inventory.libs.common_parser import get_data_from_yaml
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
from spaceone.inventory.libs.schema.metadata.dynamic_widget import (
    CardWidget,
    ChartWidget,
)

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, "widget/total_count.yml")
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yml")
count_by_project_conf = os.path.join(current_dir, "widget/count_by_project.yml")

"""
CONFIGURATION V1
"""
cst_configuration_v1 = CloudServiceTypeResource()
cst_configuration_v1.name = "Configuration"
cst_configuration_v1.provider = "google_cloud"
cst_configuration_v1.group = "CloudRun"
cst_configuration_v1.labels = ["Compute", "Container"]
cst_configuration_v1.is_primary = True
cst_configuration_v1.service_code = "Cloud Run"
cst_configuration_v1.tags = {
    "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/Cloud-Run.svg"
}

cst_configuration_v1._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Kind", "data.kind"),
        TextDyField.data_source("Namespace", "data.metadata.namespace"),
        DateTimeDyField.data_source("Created", "data.metadata.creation_timestamp"),
        TextDyField.data_source(
            "Latest Ready Revision", "data.status.latestReadyRevisionName"
        ),
        TextDyField.data_source(
            "Latest Created Revision", "data.status.latestCreatedRevisionName"
        ),
    ],
    search=[
        SearchField.set(name="Name", key="data.metadata.name"),
        SearchField.set(name="Kind", key="data.kind"),
        SearchField.set(name="Namespace", key="data.metadata.namespace"),
        SearchField.set(
            name="Latest Ready Revision", key="data.status.latestReadyRevisionName"
        ),
        SearchField.set(
            name="Latest Created Revision", key="data.status.latestCreatedRevisionName"
        ),
        SearchField.set(name="Project", key="data.project"),
        SearchField.set(name="Location", key="data.location"),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_configuration_v1}),
]
