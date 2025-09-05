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
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_widget import (
    CardWidget,
    ChartWidget,
)

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, "widget/total_count.yml")
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yml")

cst_database = CloudServiceTypeResource()
cst_database.name = "Database"
cst_database.provider = "google_cloud"
cst_database.group = "Datastore"
cst_database.service_code = "Datastore"
cst_database.is_primary = True
cst_database.is_major = True
cst_database.labels = ["Database", "NoSQL"]
cst_database.tags = {
    "spaceone:icon": f"{ASSET_URL}/Datastore.svg",
}

cst_database._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Database ID", "data.database_id"),
        EnumDyField.data_source(
            "Type",
            "data.type",
            default_badge={
                "indigo.500": ["DATASTORE_MODE"],
                "coral.600": ["FIRESTORE_NATIVE"],
            },
        ),
        TextDyField.data_source("Location", "data.location_id"),
        EnumDyField.data_source(
            "Concurrency Mode",
            "data.concurrency_mode",
            default_badge={
                "indigo.500": ["OPTIMISTIC"],
                "coral.600": ["PESSIMISTIC"],
                "peacock.500": ["OPTIMISTIC_WITH_ENTITY_GROUPS"],
            },
        ),
        DateTimeDyField.data_source("Created", "data.create_time"),
    ],
    search=[
        SearchField.set(name="Database ID", key="data.database_id"),
        SearchField.set(name="Type", key="data.type"),
        SearchField.set(name="Location", key="data.location_id"),
        SearchField.set(name="Concurrency Mode", key="data.concurrency_mode"),
        SearchField.set(name="Project ID", key="data.project_id"),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_database}),
]
