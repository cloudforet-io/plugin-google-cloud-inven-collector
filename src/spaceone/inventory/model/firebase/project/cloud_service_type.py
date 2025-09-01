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
from spaceone.inventory.libs.schema.metadata.dynamic_widget import (
    CardWidget,
    ChartWidget,
)

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, "widget/total_count.yml")
count_by_account_conf = os.path.join(current_dir, "widget/count_by_account.yml")
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yml")

cst_firebase_project = CloudServiceTypeResource()
cst_firebase_project.name = "Project"
cst_firebase_project.provider = "google_cloud"
cst_firebase_project.group = "Firebase"
cst_firebase_project.service_code = "Firebase"
cst_firebase_project.labels = ["Application Integration", "Firebase"]
cst_firebase_project.is_primary = True
cst_firebase_project.is_major = True
cst_firebase_project.tags = {
    "spaceone:icon": f"{ASSET_URL}/Firebase.svg",
}

cst_firebase_project._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Project ID", "data.project_id"),
        TextDyField.data_source("Display Name", "data.display_name"),
        TextDyField.data_source("Project Number", "data.project_number"),
        EnumDyField.data_source(
            "State",
            "data.state",
            default_state={
                "safe": ["ACTIVE"],
                "warning": [],
                "disable": ["DELETED"],
                "alert": [],
            },
        ),
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("ETag", "data.etag"),
        TextDyField.data_source(
            "Hosting Site", "data.resources.hostingSite", options={"is_optional": True}
        ),
        TextDyField.data_source(
            "Realtime Database Instance",
            "data.resources.realtimeDatabaseInstance",
            options={"is_optional": True},
        ),
        TextDyField.data_source(
            "Storage Bucket",
            "data.resources.storageBucket",
            options={"is_optional": True},
        ),
        TextDyField.data_source(
            "Location ID", "data.resources.locationId", options={"is_optional": True}
        ),
        TextDyField.data_source("Account ID", "account", options={"is_optional": True}),
    ],
    search=[
        SearchField.set(name="Project ID", key="data.project_id"),
        SearchField.set(name="Display Name", key="data.display_name"),
        SearchField.set(name="Project Number", key="data.project_number"),
        SearchField.set(
            name="State",
            key="data.state",
            enums={
                "ACTIVE": {"label": "Active"},
                "DELETED": {"label": "Deleted"},
            },
        ),
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
    CloudServiceTypeResponse({"resource": cst_firebase_project}),
]
