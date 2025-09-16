from schematics.types import StringType

from spaceone.inventory.libs.schema.cloud_service import CloudServiceMeta, BaseResource
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    BadgeDyField,
    TextDyField,
    EnumDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
)

"""
Firebase App Data Model
"""




class App(BaseResource):
    """Firebase 앱 정보 모델 (App Engine과 동일하게 BaseResource 상속)"""

    # 핵심 식별 정보 (BaseResource의 name 필드 재사용)
    display_name = StringType(deserialize_from="displayName")
    platform = StringType()
    app_id = StringType(deserialize_from="appId")
    state = StringType()

    # API 메타데이터
    namespace = StringType()
    api_key_id = StringType(deserialize_from="apiKeyId")
    expire_time = StringType(deserialize_from="expireTime", serialize_when_none=False)

    # 프로젝트 정보 (BaseResource의 project 필드 재사용 가능하지만 호환성을 위해 유지)
    project_id = StringType(deserialize_from="projectId")


    def reference(self):
        project_id = self.project_id or ""
        app_id = self.app_id or ""
        return {
            "resource_id": self.app_id,
            "external_link": f"https://console.firebase.google.com/project/{project_id}/settings/general/{app_id}",
        }


# Firebase App 메타데이터 레이아웃
# TAB - App Details
firebase_app_details = ItemDynamicLayout.set_fields(
    "App Details",
    fields=[
        TextDyField.data_source("App ID", "data.app_id"),
        TextDyField.data_source("Display Name", "data.display_name"),
        TextDyField.data_source("Name", "data.name"),
        EnumDyField.data_source(
            "Platform",
            "data.platform",
            default_badge={
                "indigo.500": ["IOS"],
                "green.500": ["ANDROID"],
                "blue.500": ["WEB"],
            },
        ),
        BadgeDyField.data_source("State", "data.state"),
        TextDyField.data_source("Namespace", "data.namespace"),
        TextDyField.data_source("API Key ID", "data.api_key_id"),
    ],
)

# TAB - Timestamps
firebase_app_timestamps = ItemDynamicLayout.set_fields(
    "Timestamps",
    fields=[
        TextDyField.data_source("Project ID", "data.project_id"),
        TextDyField.data_source("Full Name", "data.full_name"),
    ],
)

# Unified metadata layout
firebase_app_meta = CloudServiceMeta.set_layouts(
    [
        firebase_app_details,
        firebase_app_timestamps,
    ]
)
