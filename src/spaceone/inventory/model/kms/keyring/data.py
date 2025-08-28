from schematics import Model
from schematics.types import DictType, IntType, ListType, ModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import BaseResource

"""
KMS KeyRing Data 모델 정의

Google Cloud KMS KeyRing의 상세 데이터를 표현하기 위한 schematics 모델입니다.
"""


class CryptoKeyVersionData(Model):
    """CryptoKey Version 정보 모델"""

    name = StringType()
    version_id = StringType()
    state = StringType()
    create_time = StringType()
    generate_time = StringType()
    protection_level = StringType()
    algorithm = StringType()
    import_job = StringType()
    import_time = StringType()
    import_failure_reason = StringType()
    reimport_eligible = StringType()
    destroy_time = StringType()
    destroy_event_time = StringType()
    raw_data = StringType(default="")


class CryptoKeyData(Model):
    """CryptoKey 정보 모델"""

    name = StringType()
    crypto_key_id = StringType()
    purpose = StringType()
    create_time = StringType()
    next_rotation_time = StringType()
    primary_state = StringType()
    primary_name = StringType()
    protection_level = StringType()
    algorithm = StringType()
    display_name = StringType()
    crypto_key_version_count = IntType(default=0)
    crypto_key_versions = ListType(ModelType(CryptoKeyVersionData), default=[])
    raw_data = StringType(default="")


class KMSKeyRingData(BaseResource):
    """KMS KeyRing 데이터 모델"""

    name = StringType()
    keyring_id = StringType()
    project_id = StringType()
    location_id = StringType()
    location_display_name = StringType()
    location_labels = DictType(StringType)
    create_time = StringType()
    display_name = StringType()
    full_location_path = StringType()
    crypto_keys = ListType(ModelType(CryptoKeyData), default=[])
    crypto_key_count = IntType(default=0)
    raw_data = StringType(default="")
    location_raw_data = StringType(default="")

    def reference(self):
        return {
            "resource_id": f"{self.project_id}:{self.location_id}:{self.keyring_id}",
            "external_link": f"https://console.cloud.google.com/security/kms/keyring/manage/{self.location_id}/{self.keyring_id}?project={self.project_id}",
        }
