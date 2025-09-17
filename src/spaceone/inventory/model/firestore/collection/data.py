from schematics import Model
from schematics.types import IntType, ListType, ModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import BaseResource

__all__ = ["FirestoreCollection", "DocumentInfo"]


class DocumentInfo(Model):
    """Document information in collection"""

    document_id = StringType()
    document_name = StringType()
    fields_summary = StringType()
    create_time = StringType()
    update_time = StringType()


class FirestoreCollection(BaseResource):
    full_name = StringType()
    database_id = StringType()
    collection_path = StringType()

    documents = ListType(ModelType(DocumentInfo), default=[], serialize_when_none=False)
    document_count = IntType(default=0)

    depth_level = IntType(default=0)
    parent_document_path = StringType()

    def reference(self):
        return {
            "resource_id": f"https://firestore.googleapis.com/v1/projects/{self.project}/databases/{self.database_id}/documents/{self.collection_path}",
            "external_link": f"https://console.cloud.google.com/firestore/databases/{self.database_id}/data/panel/{self.collection_path}?project={self.project}",
        }
