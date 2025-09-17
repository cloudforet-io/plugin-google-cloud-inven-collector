from schematics.types import BooleanType, StringType

from spaceone.inventory.libs.schema.cloud_service import BaseResource

__all__ = ["Database"]


class Database(BaseResource):
    full_name = StringType()
    uid = StringType()
    type = StringType()
    concurrency_mode = StringType(deserialize_from="concurrencyMode")
    location_id = StringType(deserialize_from="locationId")

    create_time = StringType(deserialize_from="createTime")
    update_time = StringType(deserialize_from="updateTime")

    version_retention_period = StringType(deserialize_from="versionRetentionPeriod")
    earliest_version_time = StringType(deserialize_from="earliestVersionTime")
    app_engine_integration_mode = StringType(
        deserialize_from="appEngineIntegrationMode"
    )
    point_in_time_recovery_enablement = StringType(
        deserialize_from="pointInTimeRecoveryEnablement"
    )
    delete_protection_state = StringType(deserialize_from="deleteProtectionState")
    database_edition = StringType(deserialize_from="databaseEdition")
    free_tier = BooleanType(deserialize_from="freeTier", serialize_when_none=False)

    etag = StringType()

    def reference(self):
        # database_id is "(default)" then convert to "-default-"
        url_database_id = "-default-" if self.name == "(default)" else self.name

        return {
            "resource_id": f"https://firestore.googleapis.com/v1/{self.full_name}",
            "external_link": f"https://console.cloud.google.com/firestore/databases/{url_database_id}?project={self.project}",
        }
