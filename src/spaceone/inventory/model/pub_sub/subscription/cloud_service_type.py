import os

from spaceone.inventory.libs.common_parser import get_data_from_yaml
from spaceone.inventory.libs.schema.cloud_service_type import *
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    EnumDyField,
    TextDyField,
    SearchField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_widget import (
    CardWidget,
    ChartWidget,
)
from spaceone.inventory.conf.cloud_service_conf import *

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, "widget/total_count.yml")
count_by_region_conf = os.path.join(current_dir, "widget/count_by_region.yml")
count_by_project_conf = os.path.join(current_dir, "widget/count_by_project.yml")

cst_subscription = CloudServiceTypeResource()
cst_subscription.name = "Subscription"
cst_subscription.provider = "google_cloud"
cst_subscription.group = "PubSub"
cst_subscription.service_code = "Cloud Pub/Sub"
cst_subscription.labels = ["Application Integration"]
cst_subscription.is_primary = True
cst_subscription.is_major = True
cst_subscription.tags = {"spaceone:icon": f"{ASSET_URL}/cloud_pubsub.svg"}

cst_subscription._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        EnumDyField.data_source(
            "Status",
            "data.state",
            default_state={
                "safe": ["ACTIVE"],
                "warning": [],
                "alert": ["RESOURCE_ERROR", "STATE_UNSPECIFIED"],
            },
        ),
        TextDyField.data_source("Subscription ID", "data.id"),
        EnumDyField.data_source(
            "Delivery type",
            "data.display.delivery_type",
            default_outline_badge=["Pull", "Push", "BigQuery"],
        ),
        TextDyField.data_source("Topic name", "data.topic"),
        TextDyField.data_source("Ack deadline", "data.display.ack_deadline_seconds"),
        TextDyField.data_source("Retention", "data.display.retention_duration"),
        TextDyField.data_source("Message ordering", "data.display.message_ordering"),
        TextDyField.data_source(
            "Exactly once delivery", "data.display.exactly_once_delivery"
        ),
        TextDyField.data_source("Expiration", "data.display.ttl"),
        EnumDyField.data_source(
            "Attachment",
            "data.display.attachment",
            default_badge={"indigo.500": ["Attached"], "coral.600": ["Unattached"]},
        ),
        TextDyField.data_source("Push endpoint", "data.push_config.push_endpoint"),
        TextDyField.data_source(
            "Subscription name", "name", options={"is_optional": True}
        ),
        TextDyField.data_source(
            "Project", "data.project", options={"is_optional": True}
        ),
        TextDyField.data_source(
            "Dead letter topic",
            "data.dead_letter_policy.dead_letter_topic",
            options={"is_optional": True},
        ),
        TextDyField.data_source(
            "Maximum delivery attempts",
            "data.dead_letter_policy.max_delivery_attempts",
            options={"is_optional": True},
        ),
        TextDyField.data_source(
            "Retry policy",
            "data.display.retry_policy.description",
            options={"is_optional": True},
        ),
        TextDyField.data_source(
            "Minimum backoff duration",
            "data.display.retry_policy.minimum_backoff",
            options={"is_optional": True},
        ),
        TextDyField.data_source(
            "Maximum backoff duration",
            "data.display.retry_policy.maximum_backoff",
            options={"is_optional": True},
        ),
    ],
    search=[
        SearchField.set(name="Subscription ID", key="data.id"),
        SearchField.set(name="Status", key="data.status"),
        SearchField.set(name="Delivery type", key="data.display.delivery_type"),
        SearchField.set(
            name="Ack deadline", key="data.ack_deadline_seconds", data_type="integer"
        ),
        SearchField.set(name="Retention", key="data.display.retention_duration"),
        SearchField.set(name="Message ordering", key="data.display.message_ordering"),
        SearchField.set(
            name="Exactly once delivery", key="data.display.exactly_once_delivery"
        ),
        SearchField.set(name="Expiration", key="data.display.ttl"),
        SearchField.set(name="Attachment", key="data.display.attachment"),
        SearchField.set(name="Subscription name", key="name"),
        SearchField.set(name="Project", key="data.project"),
        SearchField.set(
            name="Max delivery attempts (dead_letter)",
            key="data.dead_letter_policy.max_delivery_attempts",
        ),
    ],
    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf)),
    ],
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({"resource": cst_subscription}),
]
