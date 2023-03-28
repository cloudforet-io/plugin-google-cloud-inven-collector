from schematics import Model
from schematics.types import ModelType, ListType, StringType, DictType, IntType, UnionType, FloatType
from spaceone.inventory.libs.schema.cloud_service import BaseResource


class TargetResource(Model):
    name = StringType()
    display_name = StringType()


class Insight(Model):
    name = StringType()
    description = StringType()
    last_refresh_time = StringType()
    observation_period = StringType()
    state = StringType()
    category = StringType()
    insight_subtype = StringType()
    severity = StringType()
    etag = StringType()
    target_resources = ListType(ModelType(TargetResource))


class Display(Model):
    recommender_id = StringType()
    recommender_id_name = StringType()
    recommender_id_description = StringType()
    priority_display = StringType()
    resource = StringType()
    insights = ListType(ModelType(Insight), default=[])
    output_display = StringType(serialize_when_none=False, default='show')
    overview = StringType()
    operations = StringType()
    cost_description = StringType()


class Money(Model):
    currency_code = StringType(deserialize_from='currencyCode')
    units = StringType()
    nanos = IntType()


class CostProjection(Model):
    cost = ModelType(Money)
    duration = StringType()


class SecurityProjection(Model):
    details = ListType(DictType(StringType), default=[])


class SustainabilityProjection(Model):
    kgCO2e = StringType()
    duration = StringType()


class ReliabilityProjection(Model):
    risks = ListType(StringType(choices=('RISK_TYPE_UNSPECIFIED', 'SERVICE_DISRUPTION', 'DATA_LOSS', 'ACCESS_DENY')))
    details = ListType(DictType(StringType), default=[])


class Impact(Model):
    category = StringType(choices=(
        'CATEGORY_UNSPECIFIED', 'COST', 'SECURITY', 'PERFORMANCE', 'MANAGEABILITY', 'SUSTAINABILITY', 'RELIABILITY'
    ))
    cost_projection = ModelType(CostProjection, deserialize_from='costProjection')
    security_projection = ModelType(CostProjection, deserialize_from='securityProjection')
    sustainability_projection = ModelType(SustainabilityProjection, deserialize_from='sustainabilityProjection')
    reliability_projection = ModelType(ReliabilityProjection, deserialize_from='reliabilityProjection')


class Resources(Model):
    type = StringType()
    amount = FloatType()


class Value(Model):
    name = StringType()
    description = StringType()
    plan = StringType()
    resources = ListType(ModelType(Resources), default=[])
    type = StringType()


class Operation(Model):
    action = StringType()
    resource_type = StringType(deserialize_from='resourceType')
    resource = StringType()
    path = StringType()
    source_resource = StringType(deserialize_from='sourceResource')
    source_path = StringType(deserialize_from='sourcePath')
    path_filters = DictType(StringType, deserialize_from='pathFilters')
    path_value_matchers = DictType(StringType, deserialize_from='pathValueMatchers')
    value_matcher = DictType(StringType, deserialize_from='valueMatcher')


class OperationGroup(Model):
    operations = ListType(ModelType(Operation))


class RecommendationContent(Model):
    operation_groups = ListType(ModelType(OperationGroup), deserialize_from='operationGroups')
    overview = DictType(
        UnionType([StringType(), IntType(), FloatType(), ListType(StringType()), DictType(StringType())])
    )


class RecommendationStateInfo(Model):
    state = StringType(choices=('STATE_UNSPECIFIED', 'ACTIVE', 'CLAIMED', 'SUCCEEDED', 'FAILED', 'DISMISSED'))
    state_metadata = DictType(StringType, deserialize_from='stateMetadata')


class InsightReference(Model):
    insight = StringType()


class Recommendation(BaseResource):
    name = StringType()
    description = StringType()
    recommender_subtype = StringType(deserialize_from='recommenderSubtype')
    last_refresh_time = StringType(deserialize_from='lastRefreshTime')
    primary_impact = ModelType(Impact, deserialize_from='primaryImpact')
    additional_impact = ListType(ModelType(Impact), deserialize_from='additionalImpact')
    priority = StringType(choices=('PRIORITY_UNSPECIFIED', 'P4', 'P3', 'P2', 'P1'))
    content = ModelType(RecommendationContent)
    state_info = ModelType(RecommendationStateInfo, deserialize_from='stateInfo')
    etag = StringType()
    associated_insights = ListType(ModelType(InsightReference), deserialize_from='associatedInsights')
    xor_group_id = StringType(deserialize_from='xorGroupId')
    display = ModelType(Display)

    def reference(self):
        return {
            "resource_id": self.name,
            "external_link": f'https://console.cloud.google.com/home/recommendations'
        }

    class Options:
        serialize_when_none = False
