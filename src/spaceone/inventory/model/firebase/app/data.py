from schematics import Model
from schematics.types import DictType, IntType, ListType, ModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import CloudServiceMeta
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    BadgeDyField,
    TextDyField,
    EnumDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    ListDynamicLayout,
)

"""
Firebase App Data Model
"""


class App(Model):
    """Firebase 앱 정보 모델"""

    # 핵심 식별 정보
    name = StringType()
    display_name = StringType(deserialize_from="displayName")
    platform = StringType()
    app_id = StringType(deserialize_from="appId")
    state = StringType()
    
    # 플랫폼별 설정 정보 (조건부 포함)
    package_name = StringType(deserialize_from="packageName", serialize_when_none=False)  # Android만
    bundle_id = StringType(deserialize_from="bundleId", serialize_when_none=False)        # iOS만
    web_id = StringType(deserialize_from="webId", serialize_when_none=False)              # Web만
    
    # API 메타데이터
    namespace = StringType()
    api_key_id = StringType(deserialize_from="apiKeyId")
    expire_time = StringType(deserialize_from="expireTime", serialize_when_none=False)
    
    # 프로젝트 정보
    project_id = StringType(deserialize_from="projectId")

    def reference(self):
        project_id = self.project_id or ""
        app_id = self.app_id or ""
        return {
            "resource_id": self.app_id,
            "external_link": f"https://console.firebase.google.com/project/{project_id}/settings/general/{app_id}",
        }


# Firebase App 메타데이터 레이아웃
firebase_app_meta = CloudServiceMeta.set_layouts(
    layouts=[
        ItemDynamicLayout.set_fields(
            "App Information",
            fields=[
                TextDyField.data_source("Display Name", "data.display_name"),
                TextDyField.data_source("App ID", "data.app_id"),
                EnumDyField.data_source(
                    "Platform",
                    "data.platform",
                    default_badge={
                        "indigo.500": ["IOS"],
                        "green.500": ["ANDROID"],
                        "blue.500": ["WEB"],
                    },
                ),
                TextDyField.data_source("Namespace", "data.namespace"),
                BadgeDyField.data_source("State", "data.state"),
                TextDyField.data_source("API Key ID", "data.api_key_id"),
            ],
        ),
        ItemDynamicLayout.set_fields(
            "Platform Configuration",
            fields=[
                TextDyField.data_source("Package Name", "data.package_name"),  # Android
                TextDyField.data_source("Bundle ID", "data.bundle_id"),        # iOS
                TextDyField.data_source("Web ID", "data.web_id"),              # Web
            ],
        ),
    ]
)
