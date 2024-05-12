from schematics import Model
from schematics.types import ModelType, ListType, StringType, IntType, FloatType
from spaceone.inventory.libs.schema.cloud_service import BaseResource


class RedefinedInsight(Model):
    description = StringType()
    severity = StringType()
    category = StringType(
        choices=(
            "CATEGORY_UNSPECIFIED",
            "COST",
            "SECURITY",
            "PERFORMANCE",
            "MANAGEABILITY",
            "SUSTAINABILITY",
            "RELIABILITY",
        )
    )


class RedefinedRecommendation(Model):
    description = StringType()
    state = StringType(
        choices=(
            "STATE_UNSPECIFIED",
            "ACTIVE",
            "CLAIMED",
            "SUCCEEDED",
            "FAILED",
            "DISMISSED",
        )
    )
    affected_resource = StringType()
    location = StringType()
    priority_level = StringType()
    operations = StringType()
    cost = FloatType()
    cost_savings = StringType()
    insights = ListType(ModelType(RedefinedInsight), default=[])


class Recommender(BaseResource):
    name = StringType()
    id = StringType()
    description = StringType()
    state = StringType(choices=("ok", "warning", "error"))
    primary_priority_level = StringType()
    category = StringType(
        choices=(
            "CATEGORY_UNSPECIFIED",
            "COST",
            "SECURITY",
            "PERFORMANCE",
            "MANAGEABILITY",
            "SUSTAINABILITY",
            "RELIABILITY",
        )
    )
    resource_count = IntType()
    cost_savings = StringType()
    recommendations = ListType(ModelType(RedefinedRecommendation), default=[])

    def reference(self):
        return {
            "resource_id": self.id,
            "external_link": f"https://console.cloud.google.com/home/recommendations",
        }
