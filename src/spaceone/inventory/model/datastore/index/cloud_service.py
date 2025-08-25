from schematics.types import ModelType, PolyModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    EnumDyField,
    ListDyField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    TableDynamicLayout,
)
from spaceone.inventory.model.datastore.index.data import DatastoreIndexData

"""
Datastore Index Cloud Service 모델 정의

Google Cloud Datastore Index 리소스를 SpaceONE에서 표현하기 위한 모델을 정의합니다.
- DatastoreIndexResource: Datastore Index 리소스 데이터 구조
- DatastoreIndexResponse: Datastore Index 응답 형식
"""

"""
Datastore Index UI 메타데이터 레이아웃 정의

SpaceONE 콘솔에서 Datastore Index 정보를 표시하기 위한 UI 레이아웃을 정의합니다.
"""

# TAB - Index Details
datastore_index_details = ItemDynamicLayout.set_fields(
    "Index Details",
    fields=[
        TextDyField.data_source("Index ID", "data.indexId"),
        TextDyField.data_source("Kind", "data.kind"),
        TextDyField.data_source("Ancestor", "data.ancestor"),
        EnumDyField.data_source(
            "State",
            "data.state",
            default_state={
                "safe": ["READY", "SERVING"],
                "warning": ["CREATING", "DELETING"],
                "alert": ["ERROR"],
                "disable": ["UNKNOWN"],
            },
        ),
        TextDyField.data_source("Project ID", "data.project_id"),
        TextDyField.data_source("Property Count", "data.property_count"),
    ],
)

# TAB - Properties
datastore_index_properties = TableDynamicLayout.set_fields(
    "Properties",
    root_path="data.properties",
    fields=[
        TextDyField.data_source("Property Name", "name"),
        TextDyField.data_source("Direction", "direction"),
    ],
)

# TAB - Sorted Properties
datastore_index_sorted_properties = ItemDynamicLayout.set_fields(
    "Sorted Properties",
    fields=[
        ListDyField.data_source(
            "Sorted Properties", "data.sorted_properties", options={"delimiter": "<br>"}
        ),
    ],
)

# CloudService 메타데이터 정의
datastore_index_meta = CloudServiceMeta.set_layouts(
    [
        datastore_index_details,
        datastore_index_properties,
        datastore_index_sorted_properties,
    ]
)


class DatastoreIndexResource(CloudServiceResource):
    """Datastore Index 리소스 모델"""

    cloud_service_type = StringType(default="Index")
    cloud_service_group = StringType(default="Datastore")
    data = ModelType(DatastoreIndexData)
    _metadata = ModelType(
        CloudServiceMeta, default=datastore_index_meta, serialized_name="metadata"
    )


class DatastoreIndexResponse(CloudServiceResponse):
    """Datastore Index 응답 모델"""

    resource = PolyModelType(DatastoreIndexResource)
