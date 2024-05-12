import os

from spaceone.inventory.libs.common_parser import *
from spaceone.inventory.libs.schema.metadata.dynamic_widget import (
    CardWidget,
    ChartWidget,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    TextDyField,
    SearchField,
    DateTimeDyField,
    EnumDyField,
    SizeField,
)
from spaceone.inventory.libs.schema.cloud_service_type import (
    CloudServiceTypeResource,
    CloudServiceTypeResponse,
    CloudServiceTypeMeta,
)
from spaceone.inventory.conf.cloud_service_conf import *

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, "widget/total_count.yml")
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yml")
count_by_project_conf = os.path.join(current_dir, "widget/count_by_project.yml")

cst_function = CloudServiceTypeResource()
cst_function.name = "Function"
cst_function.provider = "google_cloud"
cst_function.group = "CloudFunctions"
cst_function.service_code = "Cloud Functions"
cst_function.is_primary = True
cst_function.is_major = True
cst_function.labels = ["Compute"]
cst_function.tags = {
    "spaceone:icon": f"{ASSET_URL}/cloud_functions.svg",
    "spaceone:display_name": "CloudFunctions",
}

cst_function._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        EnumDyField.data_source(
            "Status",
            "data.display.state",
            default_state={
                "safe": ["ACTIVE"],
                "warning": [
                    "DEPLOYING",
                    "DELETING",
                    "DEPLOY_IN_PROGRESS",
                    "DELETE_IN_PROGRESS",
                ],
                "alert": [
                    "STATE_UNSPECIFIED",
                    "FAILED",
                    "UNKNOWN",
                    "CLOUD_FUNCTION_STATUS_UNSPECIFIED",
                    "OFFLINE",
                ],
            },
        ),
        TextDyField.data_source("Environment", "data.display.environment"),
        TextDyField.data_source("ID", "data.display.function_id"),
        TextDyField.data_source("Last deployed", "data.display.last_deployed"),
        TextDyField.data_source("Region", "region_code"),
        TextDyField.data_source("Trigger", "data.display.trigger"),
        TextDyField.data_source("Event type", "data.event_trigger.event_type"),
        TextDyField.data_source("Runtime", "data.display.runtime"),
        TextDyField.data_source("Memory allocated", "data.display.memory_allocated"),
        TextDyField.data_source("Timeout", "data.display.timeout"),
        TextDyField.data_source("Executed function", "data.display.executed_function"),
    ],
    search=[
        SearchField.set(name="Status", key="data.display.state"),
        SearchField.set(name="Environment", key="data.display.environment"),
        SearchField.set(name="ID", key="data.display.function_id"),
        SearchField.set(name="Last deployed", key="data.display.last_deployed"),
        SearchField.set(name="Region", key="region_code"),
        SearchField.set(name="Trigger", key="data.display.trigger"),
        SearchField.set(name="Event type", key="data.event_trigger.event_type"),
        SearchField.set(name="Runtime", key="data.display.runtime"),
        SearchField.set(name="Memory allocated", key="data.display.memory_allocated"),
        SearchField.set(name="Timeout", key="data.display.timeout"),
        SearchField.set(name="Executed function", key="data.display.executed_function"),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_function}),
]
