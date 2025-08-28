from schematics.types import ModelType, PolyModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    DateTimeDyField,
    ListDyField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    TableDynamicLayout,
)
from spaceone.inventory.model.kms.keyring.data import KMSKeyRingData

__all__ = ["KMSResource", "KMSKeyRingResource", "KMSKeyRingResponse"]

"""
KMS KeyRing CloudService
"""

# TAB - Default
# 기본 KeyRing 정보를 표시하는 탭
kms_keyring_info_meta = ItemDynamicLayout.set_fields(
    "KeyRing Information",
    fields=[
        TextDyField.data_source("Name", "data.keyring_id"),
        TextDyField.data_source("Full Name", "data.name"),
        TextDyField.data_source("Project ID", "data.project_id"),
        TextDyField.data_source("Location", "data.location_display_name"),
        TextDyField.data_source("Location ID", "data.location_id"),
        TextDyField.data_source("CryptoKey Count", "data.crypto_key_count"),
        DateTimeDyField.data_source("Created", "data.create_time"),
    ],
)

# TAB - Location Details
# KeyRing이 속한 Location의 상세 정보를 표시하는 탭
kms_keyring_location_meta = ItemDynamicLayout.set_fields(
    "Location Details",
    fields=[
        TextDyField.data_source("Location Path", "data.full_location_path"),
        TextDyField.data_source("Display Name", "data.location_display_name"),
        ListDyField.data_source(
            "Location Labels",
            "data.location_labels",
            default_badge={
                "type": "secondary",
                "delimiter": " : ",
            },
        ),
    ],
)

# TAB - CryptoKeys
# KeyRing 내부의 CryptoKey 목록을 표시하는 탭
kms_keyring_crypto_keys_meta = TableDynamicLayout.set_fields(
    "CryptoKeys",
    root_path="data.crypto_keys",
    fields=[
        TextDyField.data_source("Name", "crypto_key_id"),
        TextDyField.data_source("Display Name", "display_name"),
        TextDyField.data_source("Purpose", "purpose"),
        TextDyField.data_source("Primary State", "primary_state"),
        TextDyField.data_source("Protection Level", "protection_level"),
        TextDyField.data_source("Algorithm", "algorithm"),
        TextDyField.data_source("Versions", "crypto_key_version_count"),
        DateTimeDyField.data_source("Created", "create_time"),
        DateTimeDyField.data_source("Next Rotation", "next_rotation_time"),
    ],
)

# TAB - CryptoKey Versions Summary
# 각 CryptoKey의 버전 개수와 주요 정보를 요약해서 표시하는 탭
kms_keyring_crypto_key_versions_meta = TableDynamicLayout.set_fields(
    "CryptoKey Versions Summary",
    root_path="data.crypto_keys",
    fields=[
        TextDyField.data_source("CryptoKey ID", "crypto_key_id"),
        TextDyField.data_source("Purpose", "purpose"),
        TextDyField.data_source("Total Versions", "crypto_key_version_count"),
        TextDyField.data_source("Primary State", "primary_state"),
        TextDyField.data_source("Protection Level", "protection_level"),
        TextDyField.data_source("Algorithm", "algorithm"),
        DateTimeDyField.data_source("Created", "create_time"),
        DateTimeDyField.data_source("Next Rotation", "next_rotation_time"),
    ],
)

# TAB - CryptoKey Versions Detail
# 각 CryptoKey의 버전 상세 정보를 표시하는 탭
kms_keyring_crypto_key_versions_detail_meta = TableDynamicLayout.set_fields(
    "CryptoKey Versions Detail",
    root_path="data.crypto_keys.crypto_key_versions",
    fields=[
        TextDyField.data_source("Version ID", "version_id"),
        TextDyField.data_source("Name", "name"),
        TextDyField.data_source("State", "state"),
        TextDyField.data_source("Protection Level", "protection_level"),
        TextDyField.data_source("Algorithm", "algorithm"),
        DateTimeDyField.data_source("Created", "create_time"),
        DateTimeDyField.data_source("Generated", "generate_time"),
        TextDyField.data_source("Import Job", "import_job"),
        DateTimeDyField.data_source("Import Time", "import_time"),
        TextDyField.data_source("Import Failure Reason", "import_failure_reason"),
        TextDyField.data_source("Reimport Eligible", "reimport_eligible"),
        DateTimeDyField.data_source("Destroy Time", "destroy_time"),
        DateTimeDyField.data_source("Destroy Event Time", "destroy_event_time"),
    ],
)

# TAB - Raw Data
# API에서 반환된 원본 데이터를 JSON 형태로 표시하는 탭
kms_keyring_raw_data_meta = ItemDynamicLayout.set_fields(
    "Raw Data",
    fields=[
        TextDyField.data_source("KeyRing Raw Data", "data.raw_data"),
        TextDyField.data_source("Location Raw Data", "data.location_raw_data"),
    ],
)

# 모든 탭을 포함하는 메타데이터 설정
kms_keyring_meta = CloudServiceMeta.set_layouts(
    [
        kms_keyring_info_meta,
        kms_keyring_crypto_keys_meta,
        kms_keyring_crypto_key_versions_meta,
        kms_keyring_crypto_key_versions_detail_meta,
        kms_keyring_location_meta,
        kms_keyring_raw_data_meta,
    ]
)


class KMSResource(CloudServiceResource):
    cloud_service_meta = ModelType(CloudServiceMeta, default=kms_keyring_meta)


class KMSKeyRingResource(KMSResource):
    cloud_service_type = StringType(default="KeyRing")
    data = ModelType(KMSKeyRingData)
    _metadata = ModelType(
        CloudServiceMeta, default=kms_keyring_meta, serialized_name="metadata"
    )


class KMSKeyRingResponse(CloudServiceResponse):
    resource = PolyModelType(KMSKeyRingResource)
