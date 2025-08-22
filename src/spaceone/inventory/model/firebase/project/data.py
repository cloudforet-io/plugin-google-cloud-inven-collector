from schematics import Model
from schematics.types import DictType, IntType, ListType, ModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    BadgeDyField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    TableDynamicLayout,
)

"""
Firebase Project Data Model
"""


class FirebaseApp(Model):
    """Firebase 앱 정보 모델"""

    name = StringType()
    display_name = StringType(deserialize_from="displayName")
    platform = StringType()
    app_id = StringType(deserialize_from="appId")
    namespace = StringType()
    api_key_id = StringType(deserialize_from="apiKeyId")
    state = StringType()
    expire_time = StringType(deserialize_from="expireTime")


class Project(Model):
    project_id = StringType(deserialize_from="projectId")
    display_name = StringType(deserialize_from="displayName")
    project_number = StringType(deserialize_from="projectNumber")
    state = StringType()
    name = StringType()
    firebase_apps = ListType(ModelType(FirebaseApp), deserialize_from="firebaseApps")
    app_count = IntType(deserialize_from="appCount")
    has_firebase_services = StringType(
        deserialize_from="hasFirebaseServices", serialize_when_none=False
    )
    platform_stats = DictType(IntType, deserialize_from="platformStats")

    def reference(self):
        return {
            "resource_id": self.project_id,
            "external_link": f"https://console.firebase.google.com/project/{self.project_id}",
        }


# Firebase Project 메타데이터 레이아웃
firebase_project_meta = CloudServiceMeta.set_layouts(
    layouts=[
        ItemDynamicLayout.set_fields(
            "Project Info",
            fields=[
                TextDyField.data_source("Project ID", "data.project_id"),
                TextDyField.data_source("Display Name", "data.display_name"),
                TextDyField.data_source("Project Number", "data.project_number"),
                TextDyField.data_source("State", "data.state"),
                TextDyField.data_source("Name", "data.name"),
                BadgeDyField.data_source(
                    "Has Firebase Services", "data.has_firebase_services"
                ),
                TextDyField.data_source("App Count", "data.app_count"),
            ],
        ),
        ItemDynamicLayout.set_fields(
            "Platform Statistics",
            fields=[
                TextDyField.data_source("iOS Apps", "data.platform_stats.IOS"),
                TextDyField.data_source("Android Apps", "data.platform_stats.ANDROID"),
                TextDyField.data_source("Web Apps", "data.platform_stats.WEB"),
            ],
        ),
        TableDynamicLayout.set_fields(
            "Firebase Apps",
            root_path="data.firebase_apps",
            fields=[
                TextDyField.data_source("App Name", "display_name"),
                BadgeDyField.data_source("Platform", "platform"),
                TextDyField.data_source("App ID", "app_id"),
                TextDyField.data_source("Namespace", "namespace"),
                BadgeDyField.data_source("State", "state"),
            ],
        ),
    ]
)
