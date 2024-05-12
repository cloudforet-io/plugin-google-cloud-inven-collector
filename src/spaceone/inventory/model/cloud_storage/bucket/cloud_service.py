from schematics.types import PolyModelType

from spaceone.inventory.model.cloud_storage.bucket.data import *
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    TextDyField,
    DateTimeDyField,
    EnumDyField,
    SizeField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    TableDynamicLayout,
    ListDynamicLayout,
    SimpleTableDynamicLayout,
)
from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceResource,
    CloudServiceResponse,
    CloudServiceMeta,
)

"""
Bucket
"""

# TAB - Bucket
bucket_configuration_meta = ItemDynamicLayout.set_fields(
    "Configurations",
    fields=[
        TextDyField.data_source("Location Type", "data.location.location_type"),
        TextDyField.data_source("Location", "data.location.location_display"),
        EnumDyField.data_source(
            "Default Storage Class",
            "data.default_storage_class",
            default_outline_badge=["Standard", "Nearline", "Coldline", "Archive"],
        ),
        TextDyField.data_source("Encryption Type", "data.encryption"),
        TextDyField.data_source("Object Total Counts", "data.object_count"),
        SizeField.data_source("Object Size", "data.object_total_size"),
        EnumDyField.data_source(
            "Public Access",
            "data.public_access",
            default_state={
                "safe": ["Subject to object ACLs", "Not public"],
                "warning": ["Not authorized"],
                "alert": ["Public to internet"],
            },
        ),
        EnumDyField.data_source(
            "Requester Pays",
            "data.requester_pays",
            default_badge={"indigo.500": ["OFF"], "coral.600": ["ON"]},
        ),
        TextDyField.data_source("Access Control", "data.access_control"),
        TextDyField.data_source("Link URL", "data.links.link_url"),
        TextDyField.data_source("Link for gsutil", "data.links.gsutil_link"),
        DateTimeDyField.data_source("Created", "data.creation_timestamp"),
        DateTimeDyField.data_source("Updated", "data.update_timestamp"),
    ],
)


bucket_permission_info_meta = ItemDynamicLayout.set_fields(
    "Details",
    fields=[
        TextDyField.data_source("Public Access", "data.public_access"),
        TextDyField.data_source("Access Control", "data.access_control"),
    ],
)

bucket_permission_member_meta = SimpleTableDynamicLayout.set_fields(
    "Permissions Member",
    root_path="data.iam_policy_binding",
    fields=[
        TextDyField.data_source("Member", "member"),
        TextDyField.data_source("role", "role"),
    ],
)


bucket_permission_meta = ListDynamicLayout.set_layouts(
    "Permission", layouts=[bucket_permission_info_meta, bucket_permission_member_meta]
)


bucket_retention_meta = ItemDynamicLayout.set_fields(
    "Retention",
    fields=[
        TextDyField.data_source("Retention Period", "data.retention_policy_display"),
        EnumDyField.data_source(
            "Lock Status",
            "data.retention_policy.is_locked",
            default_badge={"indigo.500": ["true"], "coral.600": ["false"]},
        ),
        DateTimeDyField.data_source(
            "Effective Date", "data.retention_policy.effective_time"
        ),
        EnumDyField.data_source(
            "Default Event-Based Hold Option",
            "data.default_event_based_hold",
            default_badge={"indigo.500": ["Enabled"], "coral.600": ["Disabled"]},
        ),
    ],
)

bucket_life_cycle_meta = TableDynamicLayout.set_fields(
    "Lifecycle",
    root_path="data.lifecycle_rule.rule",
    fields=[
        TextDyField.data_source("Action", "action_display"),
        TextDyField.data_source("Object Condition", "condition_display"),
    ],
)

bucket_labels_meta = TableDynamicLayout.set_fields(
    "Labels",
    root_path="data.labels",
    fields=[
        TextDyField.data_source("Key", "key"),
        TextDyField.data_source("Value", "value"),
    ],
)

instance_template_meta = CloudServiceMeta.set_layouts(
    [
        bucket_configuration_meta,
        bucket_permission_meta,
        bucket_retention_meta,
        bucket_life_cycle_meta,
        bucket_labels_meta,
    ]
)


class StorageGroupResource(CloudServiceResource):
    cloud_service_group = StringType(default="CloudStorage")


class StorageResource(StorageGroupResource):
    cloud_service_type = StringType(default="Bucket")
    data = ModelType(Storage)
    _metadata = ModelType(
        CloudServiceMeta, default=instance_template_meta, serialized_name="metadata"
    )


class StorageResponse(CloudServiceResponse):
    resource = PolyModelType(StorageResource)
