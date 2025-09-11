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
    EnumDyField,
    SearchField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_widget import (
    CardWidget,
    ChartWidget,
)

current_dir = os.path.abspath(os.path.dirname(__file__))

"""
DATABASE
"""
total_count_conf = os.path.join(current_dir, "widget/total_count.yaml")
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yaml")
count_by_project_conf = os.path.join(current_dir, "widget/count_by_project.yaml")

cst_database = CloudServiceTypeResource()
cst_database.name = "Database"
cst_database.provider = "google_cloud"
cst_database.group = "Firestore"
cst_database.service_code = "Cloud Firestore"
cst_database.is_primary = True
cst_database.is_major = True
cst_database.labels = ["Database", "NoSQL"]
cst_database.tags = {
    "spaceone:icon": f"{ASSET_URL}/Firestore.svg",
}

cst_database._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        EnumDyField.data_source(
            "Type",
            "data.type",
            default_badge={
                "indigo.500": ["FIRESTORE_NATIVE"],
                "coral.600": ["DATASTORE_MODE"],
            },
        ),
        EnumDyField.data_source(
            "Concurrency Mode",
            "data.concurrency_mode",
            default_badge={
                "indigo.500": ["OPTIMISTIC"],
                "coral.600": ["PESSIMISTIC"],
            },
        ),
        EnumDyField.data_source(
            "Delete Protection",
            "data.delete_protection_state",
            default_badge={
                "indigo.500": ["DELETE_PROTECTION_ENABLED"],
                "coral.600": ["DELETE_PROTECTION_DISABLED"],
                "gray.400": ["DELETE_PROTECTION_STATE_UNSPECIFIED"],
            },
        ),
        DateTimeDyField.data_source("Created", "data.create_time"),
    ],
    search=[
        SearchField.set(name="Type", key="data.type"),
        SearchField.set(name="Concurrency Mode", key="data.concurrency_mode"),
        SearchField.set(
            name="Delete Protection State", key="data.delete_protection_state"
        ),
        SearchField.set(
            name="Created Time", key="data.create_time", data_type="datetime"
        ),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_database}),
]
