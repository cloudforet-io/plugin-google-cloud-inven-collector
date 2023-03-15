from schematics.types import ModelType, StringType, PolyModelType, DictType
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, ListDynamicLayout, \
    TableDynamicLayout, SimpleTableDynamicLayout
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, EnumDyField, DateTimeDyField
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta
from spaceone.inventory.model.recommender.recommendation.data import Recommendation

recommendation_detail = ItemDynamicLayout.set_fields('Recommendation Details', fields=[
    TextDyField.data_source('name', 'data.name'),
    TextDyField.data_source('description', 'data.description'),
    EnumDyField.data_source('State', 'data.state_info.state', default_state={
        'safe': ['ACTIVE', 'SUCCEEDED'],
        'disable': ['CLAIMED'],
        'alert': ['STATE_UNSPECIFIED', 'DISMISSED', 'FAILED'],
    }),
    TextDyField.data_source('Recommender subtype', 'data.recommender_subtype'),
    TextDyField.data_source('Instance type name', 'data.display.instance_type_name'),
    TextDyField.data_source('Short description', 'data.display.instance_type_description'),
    TextDyField.data_source('instance_type', 'data.display.instance_type'),
    DateTimeDyField.data_source('Last refresh time', 'data.last_refresh_time'),
    TextDyField.data_source('Priority', 'data.priority'),
    EnumDyField.data_source('Priority level', 'data.display.priority_display', default_badge={
        'red.500': ['Highest'],
        'coral.500': ['Second Highest'],
        'yellow.300': ['Second Lowest'],
        'gray.500': ['Lowest'],
        'black': ['Unspecified']
    })
])

primary_impact_detail = ItemDynamicLayout.set_fields('Primary impact', fields=[
    EnumDyField.data_source('Category', 'data.primary_impact.category', default_badge={
        'indigo.500': ['COST'],
        'peacock.500': ['SUSTAINABILITY'],
        'violet.500': ['RELIABILITY'],
        'blue.500': ['PERFORMANCE'],
        'green.500': ['MANAGEABILITY'],
        'yellow.500': ['SECURITY'],
        'coral.500': ['CATEGORY_UNSPECIFIED']
    }),
    TextDyField.data_source('Cost Currency code', 'data.primary_impact.cost_projection.cost.currency_code'),
    TextDyField.data_source('Cost units', 'data.primary_impact.cost_projection.cost.units'),
    TextDyField.data_source('Cost nanos', 'data.primary_impact.cost_projection.cost.nanos'),
    TextDyField.data_source('Cost duration', 'data.primary_impact.cost_projection.cost.duration'),
    TextDyField.data_source('Security projection', 'data.primary_impact.security_projection'),
    TextDyField.data_source('Sustainability projection', 'data.primary_impact.sustainability_projection'),
    TextDyField.data_source('Reliability projection', 'data.primary_impact.reliability_projection'),
])

overview_detail = ItemDynamicLayout.set_fields('Content overview', root_path='data.content.overview', fields=[
    TextDyField.data_source('Location', 'location'),
    TextDyField.data_source('Resource', 'resource'),
    TextDyField.data_source('Resource name', 'resourceName'),
    TextDyField.data_source('Recommendation action', 'recommendedAction'),
])
operation_detail = SimpleTableDynamicLayout.set_tags('Operations', root_path='data.content.operation_groups',
                                                     fields=[
                                                         TextDyField.data_source('Action', 'action'),
                                                         TextDyField.data_source('Resource type', 'resource_type'),
                                                         TextDyField.data_source('Resource', 'resource'),
                                                         TextDyField.data_source('Path', 'path'),
                                                         TextDyField.data_source('Source resource', 'source_resource'),
                                                         TextDyField.data_source('Source path', 'source_path'),
                                                         TextDyField.data_source('Path filters', 'path_filters'),
                                                         TextDyField.data_source('Path value matchers',
                                                                                 'path_value_matchers'),
                                                         TextDyField.data_source('Value', 'value'),
                                                         TextDyField.data_source('Value matcher', 'value_matcher'),
                                                     ])

recommendation_insight_meta = TableDynamicLayout.set_fields('Insights', root_path='data.associated_insights', fields=[
    TextDyField.data_source('Name', 'insight')
])

detail_meta = ListDynamicLayout.set_layouts('Details',
                                            layouts=[recommendation_detail, primary_impact_detail, overview_detail,
                                                     operation_detail])
recommendation_meta = CloudServiceMeta.set_layouts([detail_meta, recommendation_insight_meta])


class RecommenderResource(CloudServiceResource):
    tags = DictType(StringType, serialize_when_none=False)
    cloud_service_group = StringType(default='Recommender')


class RecommendationResource(RecommenderResource):
    cloud_service_type = StringType(default='Recommendation')
    data = ModelType(Recommendation)
    _metadata = ModelType(CloudServiceMeta, default=recommendation_meta, serialized_name='metadata')


class RecommendationResponse(CloudServiceResponse):
    resource = PolyModelType(RecommendationResource)
