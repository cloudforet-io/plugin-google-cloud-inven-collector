from schematics import Model
from schematics.types import ModelType, ListType, StringType, DictType

from spaceone.inventory.libs.schema.cloud_service import BaseResource


class InsightStateInfo(Model):
    state = StringType(choices=('STATE_UNSPECIFIED', 'ACTIVE', 'ACCEPTED', 'DISMISSED'))
    state_metadata = DictType(StringType())


class RecommendationReference(Model):
    recommendation = StringType()


class Insight(BaseResource):
    name = StringType()
    description = StringType()
    target_resources = ListType(StringType(deserialize_from='targetResources'))
    insight_subtype = StringType(deserialize_from='insightSubtype')
    content = DictType(StringType())
    last_refresh_time = StringType(deserialize_from='lastRefreshTime')
    observation_period = StringType(deserialize_from='observationPeriod')
    state_info = ModelType(InsightStateInfo, deserialize_from='stateInfo')
    category = StringType(choices=(
        'CATEGORY_UNSPECIFIED', 'COST', 'SECURITY', 'PERFORMANCE', 'MANAGEABILITY', 'SUSTAINABILITY', 'RELIABILITY'
    ))
    severity = StringType(choices=(
        'SEVERITY_UNSPECIFIED', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    ))
    etag = StringType()
    associated_recommendations = ListType(ModelType(RecommendationReference),
                                          deserialize_from='associatedRecommendations')

    def reference(self):
        return {
            "resource_id": '',
            "external_link": f''
        }

    class Options:
        serialize_when_none = False
