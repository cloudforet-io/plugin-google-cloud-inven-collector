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
count_by_state_conf = os.path.join(current_dir, "widget/count_by_state.yml")
count_by_kind_conf = os.path.join(current_dir, "widget/count_by_kind.yml")

# Cloud Service Type resource definition
cst_index = CloudServiceTypeResource()
cst_index.name = "Index"
cst_index.provider = "google_cloud"
cst_index.group = "Datastore"
cst_index.labels = ["Database", "NoSQL", "Index"]
cst_index.service_code = "Datastore"
cst_index.resource_type = "inventory.CloudService"
cst_index.tags = {
    "spaceone:icon": f"{ASSET_URL}/Datastore.svg",
    "spaceone:display_name": "Datastore Index",
}

cst_index._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Kind", "data.kind"),
        TextDyField.data_source("Ancestor", "data.ancestor"),
        EnumDyField.data_source(
            "State",
            "data.state",
            default_badge={
                "safe": ["READY", "SERVING"],
                "warning": ["CREATING", "DELETING"],
                "alert": ["ERROR"],
                "disable": ["UNKNOWN"],
            },
        ),
        TextDyField.data_source("Property Count", "data.property_count"),
    ],
    search=[
        SearchField.set(name="Kind", key="data.kind"),
        SearchField.set(name="State", key="data.state"),
        SearchField.set(name="Ancestor", key="data.ancestor"),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_state_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_kind_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_index}),
]
