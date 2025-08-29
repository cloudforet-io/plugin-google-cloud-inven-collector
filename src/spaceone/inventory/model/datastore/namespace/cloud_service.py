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
)
from spaceone.inventory.model.datastore.namespace.data import DatastoreNamespaceData

"""
Datastore Namespace Cloud Service 모델 정의

Google Cloud Datastore Namespace 리소스를 SpaceONE에서 표현하기 위한 모델을 정의합니다.
"""

# TAB - Namespace Details
datastore_namespace_details = ItemDynamicLayout.set_fields(
    "Namespace Details",
    fields=[
        TextDyField.data_source("Namespace ID", "data.namespace_id"),
        TextDyField.data_source("Database ID", "data.database_id"),
        TextDyField.data_source("Display Name", "data.display_name"),
        TextDyField.data_source("Project ID", "data.project_id"),
        TextDyField.data_source("Kind Count", "data.kind_count"),
        DateTimeDyField.data_source("Created Time", "data.created_time"),
    ],
)

# TAB - Kinds
datastore_namespace_kinds = ItemDynamicLayout.set_fields(
    "Kinds",
    fields=[
        ListDyField.data_source(
            "Kind List", "data.kinds", options={"delimiter": "<br>"}
        ),
    ],
)

namespace_meta = CloudServiceMeta.set_layouts(
    [
        datastore_namespace_details,
        datastore_namespace_kinds,
    ]
)


class DatastoreNamespaceResource(CloudServiceResource):
    cloud_service_type = StringType(default="Namespace")
    cloud_service_group = StringType(default="Datastore")
    data = ModelType(DatastoreNamespaceData)
    _metadata = ModelType(
        CloudServiceMeta, default=namespace_meta, serialized_name="metadata"
    )


class DatastoreNamespaceResponse(CloudServiceResponse):
    resource = PolyModelType(DatastoreNamespaceResource)
