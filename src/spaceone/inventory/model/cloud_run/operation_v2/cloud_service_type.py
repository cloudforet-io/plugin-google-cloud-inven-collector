from spaceone.inventory.conf.cloud_service_conf import ASSET_URL
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

cst_operation = CloudServiceTypeResource()
cst_operation.name = "Operation"
cst_operation.provider = "google_cloud"
cst_operation.group = "CloudRun"
cst_operation.service_code = "Cloud Run"
cst_operation.labels = ["Serverless"]
cst_operation.is_primary = False
cst_operation.is_major = False
cst_operation.tags = {
    "spaceone:icon": f"{ASSET_URL}/Cloud-Run.svg",
}

cst_operation._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("Status", "data.status"),
        EnumDyField.data_source(
            "Done",
            "data.done",
            default_badge={
                "indigo.500": ["true"],
                "coral.600": ["false"],
            },
        ),
        TextDyField.data_source("Operation Type", "data.operation_type"),
        TextDyField.data_source("Target Resource", "data.target_resource"),
        TextDyField.data_source("Project", "data.project"),
        TextDyField.data_source("Location", "data.location"),
        TextDyField.data_source("Region", "data.region"),
    ],
    search=[
        SearchField.set("Name", "data.name"),
        SearchField.set("Status", "data.status"),
        SearchField.set("Operation Type", "data.operation_type"),
        SearchField.set("Project", "data.project"),
        SearchField.set("Location", "data.location"),
        SearchField.set("Region", "data.region"),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_operation}),
]
