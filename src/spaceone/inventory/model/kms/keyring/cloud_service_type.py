import os

from spaceone.inventory.conf.cloud_service_conf import ASSET_URL
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

__all__ = ["CLOUD_SERVICE_TYPES"]

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, "widget/total_count.yml")
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yml")
count_by_project_conf = os.path.join(current_dir, "widget/count_by_project.yml")

cst_keyring = CloudServiceTypeResource()
cst_keyring.name = "KeyRing"
cst_keyring.provider = "google_cloud"
cst_keyring.group = "KMS"
cst_keyring.service_code = "Cloud KMS"
cst_keyring.labels = ["Security", "Encryption"]
cst_keyring.is_primary = True
cst_keyring.is_major = True
cst_keyring.tags = {
    "spaceone:icon": f"{ASSET_URL}/Cloud_KMS.svg",
}

cst_keyring._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("KeyRing ID", "data.keyring_id"),
        TextDyField.data_source("Location", "data.location_display_name"),
        TextDyField.data_source("Project", "data.project_id"),
        TextDyField.data_source("CryptoKey Count", "data.crypto_key_count"),
        DateTimeDyField.data_source("Created", "data.create_time"),
    ],
    search=[
        SearchField.set(name="KeyRing ID", key="data.keyring_id"),
        SearchField.set(name="Location ID", key="data.location_id"),
        SearchField.set(name="Location", key="data.location_display_name"),
        SearchField.set(name="Project ID", key="data.project_id"),
        SearchField.set(
            name="CryptoKey Count", key="data.crypto_key_count", data_type="integer"
        ),
        SearchField.set(
            name="Created Time", key="data.create_time", data_type="datetime"
        ),
        SearchField.set(name="Account", key="account"),
        SearchField.set(name="Region", key="region_code"),
        SearchField.set(
            name="Project Group",
            key="project_group_id",
            reference="identity.ProjectGroup",
        ),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_keyring}),
]
