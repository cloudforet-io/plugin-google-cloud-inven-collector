import os

from spaceone.inventory.libs.common_parser import get_data_from_yaml
from spaceone.inventory.libs.schema.metadata.dynamic_widget import (
    CardWidget,
    ChartWidget,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    TextDyField,
    EnumDyField,
    SearchField,
)
from spaceone.inventory.libs.schema.cloud_service_type import (
    CloudServiceTypeResource,
    CloudServiceTypeResponse,
    CloudServiceTypeMeta,
)

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, "widget/total_count.yml")
count_by_account_conf = os.path.join(current_dir, "widget/count_by_account.yml")
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yml")
count_by_platform_conf = os.path.join(current_dir, "widget/count_by_platform.yml")

cst_firebase_app = CloudServiceTypeResource()
cst_firebase_app.name = "App"
cst_firebase_app.provider = "google_cloud"
cst_firebase_app.group = "Firebase"
cst_firebase_app.service_code = "Firebase"
cst_firebase_app.is_primary = True
cst_firebase_app.is_major = True
cst_firebase_app.labels = ["Application", "Mobile"]
cst_firebase_app.tags = {
    "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/Firebase.svg",
}

cst_firebase_app._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source("App ID", "data.app_id"),
        TextDyField.data_source("Display Name", "data.display_name"),
        EnumDyField.data_source(
            "Platform",
            "data.platform",
            default_badge={
                "indigo.500": ["IOS"],
                "green.500": ["ANDROID"],
                "blue.500": ["WEB"],
            },
        ),
        EnumDyField.data_source(
            "State",
            "data.state",
            default_state={
                "safe": ["ACTIVE"],
                "warning": ["PENDING_DELETE"],
                "alert": ["DELETED"],
            },
        ),
     ],
    search=[
        SearchField.set(name="App ID", key="data.app_id"),
        SearchField.set(name="Display Name", key="data.display_name"),
        SearchField.set(
            name="Platform", 
            key="data.platform", 
            enums={
                "IOS": {"label": "iOS"},
                "ANDROID": {"label": "Android"},
                "WEB": {"label": "Web"},
            }
        ),
        SearchField.set(
            name="State", 
            key="data.state", 
            enums={
                "ACTIVE": {"label": "Active"},
                "PENDING_DELETE": {"label": "Pending Delete"},
                "DELETED": {"label": "Deleted"},
            }
        ),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_account_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_platform_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_firebase_app}),
]
