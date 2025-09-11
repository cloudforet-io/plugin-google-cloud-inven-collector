from schematics.types import ModelType, PolyModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    DateTimeDyField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    TableDynamicLayout,
)
from spaceone.inventory.model.firestore.collection.data import FirestoreCollection

"""
Firestore Collection Cloud Service 모델 정의

Google Cloud Firestore 컬렉션 리소스를 SpaceONE에서 표현하기 위한 모델을 정의합니다.
- CollectionResource: Firestore 컬렉션 리소스 데이터 구조
- CollectionResponse: Firestore 컬렉션 응답 형식
"""

"""
Firestore Collection UI 메타데이터 레이아웃 정의

SpaceONE 콘솔에서 Firestore 컬렉션 정보를 표시하기 위한 UI 레이아웃을 정의합니다.
"""

# TAB - Collection Details
firestore_collection_details = ItemDynamicLayout.set_fields(
    "Collection Details",
    fields=[
        TextDyField.data_source("Collection ID(Name)", "data.name"),
        TextDyField.data_source("Database ID", "data.database_id"),
        TextDyField.data_source("Collection Path", "data.collection_path"),
        TextDyField.data_source("Document Count", "data.document_count"),
        TextDyField.data_source("Depth Level", "data.depth_level"),
        TextDyField.data_source("Parent Document", "data.parent_document_path"),
    ],
)

# TAB - Documents
firestore_collection_documents = TableDynamicLayout.set_fields(
    "Documents",
    root_path="data.documents",
    fields=[
        TextDyField.data_source("Document ID", "document_id"),
        TextDyField.data_source("Full Name", "document_name"),
        TextDyField.data_source("Fields Summary", "fields_summary"),
        DateTimeDyField.data_source("Created", "create_time"),
        DateTimeDyField.data_source("Updated", "update_time"),
    ],
)

# Unified metadata layout
firestore_collection_meta = CloudServiceMeta.set_layouts(
    [
        firestore_collection_details,
        firestore_collection_documents,
    ]
)


"""
Firestore Collection 리소스 모델

Google Cloud Firestore 컬렉션의 모든 정보를 포함하는 리소스 모델입니다.
CloudServiceResource의 기본 구조를 상속받아 사용합니다.
"""


class FirestoreResource(CloudServiceResource):
    cloud_service_group = StringType(default="Firestore")


class CollectionResource(FirestoreResource):
    cloud_service_type = StringType(default="Collection")
    data = ModelType(FirestoreCollection)
    _metadata = ModelType(
        CloudServiceMeta, default=firestore_collection_meta, serialized_name="metadata"
    )


class CollectionResponse(CloudServiceResponse):
    """
    Firestore Collection 응답 모델

    Firestore 컬렉션 수집 결과를 반환하는 응답 모델입니다.
    """

    resource = PolyModelType(CollectionResource)
