from schematics.types import ModelType, StringType, PolyModelType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceResource,
    CloudServiceResponse,
    CloudServiceMeta,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    TextDyField,
    EnumDyField,
    MoreField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    ListDynamicLayout,
)
from spaceone.inventory.model.pub_sub.schema.data import Schema

schema_details = ItemDynamicLayout.set_fields(
    "Schema",
    fields=[
        TextDyField.data_source("Schema ID", "data.id"),
        EnumDyField.data_source(
            "Schema type",
            "data.schema_type",
            default_outline_badge=["AVRO", "PROTOCOL_BUFFER", "TYPE_UNSPECIFIED"],
        ),
        TextDyField.data_source("Project", "data.project"),
    ],
)

definition = ItemDynamicLayout.set_fields(
    "Definition",
    fields=[
        MoreField.data_source(
            "Definition",
            "data.display.output_display",
            options={
                "sub_key": "data.definition",
                "layout": {
                    "name": "Definition",
                    "type": "popup",
                    "options": {"layout": {"type": "raw"}},
                },
            },
        )
    ],
)

schema_meta = ListDynamicLayout.set_layouts(
    "Details", layouts=[schema_details, definition]
)
schema_meta = CloudServiceMeta.set_layouts([schema_meta])


class PubSubResource(CloudServiceResource):
    cloud_service_group = StringType(default="PubSub")


class SchemaResource(PubSubResource):
    cloud_service_type = StringType(default="Schema")
    data = ModelType(Schema)
    _metadata = ModelType(
        CloudServiceMeta, default=schema_meta, serialized_name="metadata"
    )


class SchemaResponse(CloudServiceResponse):
    resource = PolyModelType(SchemaResource)
