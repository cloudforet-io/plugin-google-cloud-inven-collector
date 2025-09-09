import os

from spaceone.inventory.libs.common_parser import get_data_from_yaml
from spaceone.inventory.libs.schema.cloud_service_type import (
    CloudServiceTypeMeta,
    CloudServiceTypeResource,
    CloudServiceTypeResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    EnumDyField,
    SearchField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_widget import (
    CardWidget,
    ChartWidget,
)

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, "widget/total_count.yml")
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yml")
count_by_project_conf = os.path.join(current_dir, "widget/count_by_project.yml")

cst_domain_mapping = CloudServiceTypeResource()
cst_domain_mapping.name = "DomainMapping"
cst_domain_mapping.provider = "google_cloud"
cst_domain_mapping.group = "CloudRun"
cst_domain_mapping.service_code = "Cloud Run"
cst_domain_mapping.labels = ["Serverless"]
cst_domain_mapping.is_primary = True
cst_domain_mapping.is_major = True
cst_domain_mapping.tags = {
    "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/Cloud-Run.svg",
}

cst_domain_mapping._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        # TextDyField.data_source("Domain Mapping ID", "data.metadata.uid"),
        EnumDyField.data_source(
            "Status",
            "data.status.conditions.0.status",
            default_state={
                "safe": ["True"],
                "warning": ["False"],
                "alert": ["Unknown"],
            },
        ),
    ],
    search=[
        SearchField.set(name="Name", key="data.metadata.name"),
        # SearchField.set(name="Domain Mapping ID", key="data.metadata.uid"),
        SearchField.set(name="Status", key="data.status.conditions.0.status"),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_domain_mapping}),
]
