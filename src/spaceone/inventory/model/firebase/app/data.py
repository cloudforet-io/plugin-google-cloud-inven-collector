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


class ProjectInfo(Model):
    """Firebase 앱이 속한 프로젝트 정보"""

    project_id = StringType()
    display_name = StringType()
    project_number = StringType()
    state = StringType()


class AppConfig(Model):
    """Firebase 앱 설정 정보"""

    package_name = StringType(deserialize_from="packageName")
    bundle_id = StringType(deserialize_from="bundleId")
    web_id = StringType(deserialize_from="webId")


class App(Model):
    """Firebase 앱 정보 모델"""

    # 핵심 식별 정보
    name = StringType()
    display_name = StringType(deserialize_from="displayName")
    platform = StringType()
    app_id = StringType(deserialize_from="appId")
    state = StringType()
    
    # 프로젝트 및 설정 정보
    project_info = ModelType(ProjectInfo, deserialize_from="projectInfo")
    app_config = ModelType(AppConfig, deserialize_from="appConfig")
    
    # API 메타데이터
    etag = StringType()
    namespace = StringType()
    api_key_id = StringType(deserialize_from="apiKeyId")
    expire_time = StringType(deserialize_from="expireTime")
    
    # Firebase API 원본 필드들 (호환성 유지)
    project_id = StringType(deserialize_from="projectId")
    package_name = StringType(deserialize_from="packageName")  
    bundle_id = StringType(deserialize_from="bundleId")
    web_id = StringType(deserialize_from="webId")

    def reference(self):
        project_id = self.project_info.project_id if self.project_info else ""
        return {
            "resource_id": self.app_id,
            "external_link": f"https://console.firebase.google.com/project/{project_id}/settings/general",
        }


# Firebase App 메타데이터 레이아웃
firebase_app_meta = CloudServiceMeta.set_layouts(
    layouts=[
        ItemDynamicLayout.set_fields(
            "App Information",
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
                TextDyField.data_source("Name", "data.name"),
                TextDyField.data_source("Namespace", "data.namespace"),
                BadgeDyField.data_source("State", "data.state"),
                TextDyField.data_source("API Key ID", "data.api_key_id"),
                TextDyField.data_source("Expire Time", "data.expire_time"),
            ],
        ),
        ItemDynamicLayout.set_fields(
            "Project Information",
            fields=[
                TextDyField.data_source("Project ID", "data.project_info.project_id"),
                TextDyField.data_source(
                    "Project Display Name", "data.project_info.display_name"
                ),
                TextDyField.data_source(
                    "Project Number", "data.project_info.project_number"
                ),
                BadgeDyField.data_source("Project State", "data.project_info.state"),
            ],
        ),
        ItemDynamicLayout.set_fields(
            "App Configuration",
            fields=[
                TextDyField.data_source("Package Name", "data.app_config.package_name"),
                TextDyField.data_source("Bundle ID", "data.app_config.bundle_id"),
                TextDyField.data_source("Web ID", "data.app_config.web_id"),
            ],
        ),
    ]
)
