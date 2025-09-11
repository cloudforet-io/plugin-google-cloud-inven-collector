from schematics.types import ModelType, PolyModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    DateTimeDyField,
    EnumDyField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout
from spaceone.inventory.model.firestore.database.data import Database

"""
Firestore Database Cloud Service 모델 정의

Google Cloud Firestore 데이터베이스 리소스를 SpaceONE에서 표현하기 위한 모델을 정의합니다.
- DatabaseResource: Firestore 데이터베이스 리소스 데이터 구조
- DatabaseResponse: Firestore 데이터베이스 응답 형식
"""

"""
Firestore Database UI 메타데이터 레이아웃 정의

SpaceONE 콘솔에서 Firestore 데이터베이스 정보를 표시하기 위한 UI 레이아웃을 정의합니다.
"""

# TAB - Database Details
firestore_database_details = ItemDynamicLayout.set_fields(
    "Database Details",
    fields=[
        TextDyField.data_source("Database ID", "data.name"),
        TextDyField.data_source("Name", "data.full_name"),
        TextDyField.data_source("UID", "data.uid"),
        EnumDyField.data_source(
            "Type",
            "data.type",
            default_badge={
                "indigo.500": ["FIRESTORE_NATIVE"],
                "coral.600": ["DATASTORE_MODE"],
            },
        ),
        EnumDyField.data_source(
            "Concurrency Mode",
            "data.concurrency_mode",
            default_badge={
                "indigo.500": ["OPTIMISTIC"],
                "coral.600": ["PESSIMISTIC"],
            },
        ),
        EnumDyField.data_source(
            "App Engine Integration",
            "data.app_engine_integration_mode",
            default_badge={
                "indigo.500": ["ENABLED"],
                "gray.400": ["DISABLED"],
            },
        ),
        TextDyField.data_source("Location", "data.location_id"),
    ],
)

# TAB - Security & Backup
firestore_security_backup = ItemDynamicLayout.set_fields(
    "Security & Backup",
    fields=[
        EnumDyField.data_source(
            "Delete Protection",
            "data.delete_protection_state",
            default_badge={
                "indigo.500": ["DELETE_PROTECTION_ENABLED"],
                "coral.600": ["DELETE_PROTECTION_DISABLED"],
                "gray.400": ["DELETE_PROTECTION_STATE_UNSPECIFIED"],
            },
        ),
        EnumDyField.data_source(
            "Point-in-time Recovery",
            "data.point_in_time_recovery_enablement",
            default_badge={
                "indigo.500": ["POINT_IN_TIME_RECOVERY_ENABLED"],
                "coral.600": ["POINT_IN_TIME_RECOVERY_DISABLED"],
                "gray.400": ["POINT_IN_TIME_RECOVERY_ENABLEMENT_UNSPECIFIED"],
            },
        ),
        TextDyField.data_source(
            "Version Retention Period", "data.version_retention_period"
        ),
        DateTimeDyField.data_source(
            "Earliest Version Time", "data.earliest_version_time"
        ),
    ],
)

# TAB - Timestamps
firestore_timestamps = ItemDynamicLayout.set_fields(
    "Timestamps",
    fields=[
        DateTimeDyField.data_source("Created", "data.create_time"),
        DateTimeDyField.data_source("Updated", "data.update_time"),
    ],
)

# Unified metadata layout
firestore_database_meta = CloudServiceMeta.set_layouts(
    [
        firestore_database_details,
        firestore_security_backup,
        firestore_timestamps,
    ]
)


"""
Firestore Database 리소스 모델

Google Cloud Firestore 데이터베이스의 모든 정보를 포함하는 리소스 모델입니다.
CloudServiceResource의 기본 구조를 상속받아 사용합니다.
"""


class FirestoreResource(CloudServiceResource):
    cloud_service_group = StringType(default="Firestore")


class DatabaseResource(FirestoreResource):
    cloud_service_type = StringType(default="Database")
    data = ModelType(Database)
    _metadata = ModelType(
        CloudServiceMeta, default=firestore_database_meta, serialized_name="metadata"
    )


class DatabaseResponse(CloudServiceResponse):
    """
    Firestore Database 응답 모델

    Firestore 데이터베이스 수집 결과를 반환하는 응답 모델입니다.
    """

    resource = PolyModelType(DatabaseResource)
