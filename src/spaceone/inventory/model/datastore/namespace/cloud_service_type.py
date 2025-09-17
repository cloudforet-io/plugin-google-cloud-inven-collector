import os

from spaceone.inventory.conf.cloud_service_conf import ASSET_URL
from spaceone.inventory.libs.common_parser import get_data_from_yaml
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
count_by_database_conf = os.path.join(current_dir, "widget/count_by_database.yml")
count_by_kind_count_conf = os.path.join(current_dir, "widget/count_by_kind_count.yml")

# Cloud Service Type resource definition
cst_namespace = CloudServiceTypeResource()
cst_namespace.name = "Namespace"
cst_namespace.provider = "google_cloud"
cst_namespace.group = "Datastore"
cst_namespace.labels = ["Database", "NoSQL", "Namespace"]
cst_namespace.service_code = "Datastore"
cst_namespace.is_primary = False
cst_namespace.is_major = True
cst_namespace.resource_type = "inventory.CloudService"
cst_namespace.tags = {
    "spaceone:icon": f"{ASSET_URL}/Datastore.svg",
}

cst_namespace._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Database ID", "data.database_id"),
        TextDyField.data_source("Kind Count", "data.kind_count"),
    ],
    search=[
        SearchField.set(name="Database ID", key="data.database_id"),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_database_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_kind_count_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_namespace}),
]
