from schematics.types import StringType

from spaceone.inventory.libs.schema.cloud_service import BaseResource

__all__ = ["FirestoreIndex"]


class FirestoreIndex(BaseResource):
    database_id = StringType()
    full_name = StringType()

    query_scope = StringType(deserialize_from="queryScope")
    state = StringType()
    density = StringType()

    fields_summary = StringType()

    collection_group = StringType()

    def reference(self):
        return {
            "resource_id": f"https://firestore.googleapis.com/v1/{self.full_name}",
            "external_link": f"https://console.cloud.google.com/firestore/databases/{self.database_id}/indexes?project={self.project}",
        }

    @staticmethod
    def filter_internal_fields(fields):
        """GCP internal fields (__로 시작하는 필드) 제거"""
        filtered_fields = []
        for field in fields:
            field_path = field.get("fieldPath", "")
            if not field_path.startswith("__"):
                filtered_fields.append(field)
        return filtered_fields
