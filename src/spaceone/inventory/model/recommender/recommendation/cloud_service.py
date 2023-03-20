from schematics.types import ModelType, StringType, PolyModelType, DictType
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, ListDynamicLayout, \
    TableDynamicLayout, SimpleTableDynamicLayout
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, EnumDyField, DateTimeDyField, MoreField
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
    TextDyField.data_source('Recommender name', 'data.display.recommender_id_name'),
    TextDyField.data_source('Short description', 'data.display.recommender_id_description'),
    TextDyField.data_source('Recommender id', 'data.display.recommender_id'),
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

content_detail = ItemDynamicLayout.set_fields('Overview', fields=[
    MoreField.data_source('Overview', 'data.display.output_display', options={
        'sub_key': 'data.display.overview',
        'layout': {
            'name': 'Overview',
            'type': 'popup',
            'options': {
                'layout': {
                    'type': 'raw'
                }
            }
        }
    }),
    MoreField.data_source('Operations', 'data.display.output_display', options={
        'sub_key': 'data.display.operations',
        'layout': {
            'name': 'Overview',
            'type': 'popup',
            'options': {
                'layout': {
                    'type': 'raw'
                }
            }
        }
    })
])

detail_meta = ListDynamicLayout.set_layouts('Details',
                                            layouts=[recommendation_detail, primary_impact_detail, content_detail])

insight_table_meta = TableDynamicLayout.set_fields('Insights', root_path='data.display.insights', fields=[
    TextDyField.data_source('Description', 'description'),
    EnumDyField.data_source('State', 'state', default_state={
        'safe': ['ACTIVE'],
        'disable': ['ACCEPTED'],
        'alert': ['STATE_UNSPECIFIED', 'DISMISSED'],
    }),
    EnumDyField.data_source('Severity', 'severity', default_badge={
        'red.500': ['CRITICAL', 'HIGH', 'SEVERITY_UNSPECIFIED'], 'gray.500': ['MEDIUM', 'LOW']
    }),
    EnumDyField.data_source('Category', 'category', default_badge={
        'indigo.500': ['COST'],
        'peacock.500': ['SUSTAINABILITY'],
        'violet.500': ['RELIABILITY'],
        'blue.500': ['PERFORMANCE'],
        'green.500': ['MANAGEABILITY'],
        'yellow.500': ['SECURITY'],
        'coral.500': ['CATEGORY_UNSPECIFIED']
    }),
    TextDyField.data_source('Insight subtype', 'insight_subtype'),
    TextDyField.data_source('Name', 'name'),
    TextDyField.data_source('Last refresh time', 'last_refresh_time'),
    TextDyField.data_source('etag', 'etag')
])

resource_table_meta = TableDynamicLayout.set_fields('Target resources',
                                                    root_path='data.display.insights.target_resources',
                                                    fields=[
                                                        TextDyField.data_source('Resource name', 'name'),
                                                        TextDyField.data_source('Link', 'display_name', reference={
                                                            'resource_type': 'inventory.CloudService',
                                                            'reference_key': 'data.name'
                                                        }),
                                                    ])

insight_meta = ListDynamicLayout.set_layouts('Insight',
                                             layouts=[insight_table_meta, resource_table_meta])
recommendation_meta = CloudServiceMeta.set_layouts([detail_meta, insight_meta])


class RecommenderResource(CloudServiceResource):
    tags = DictType(StringType, serialize_when_none=False)
    cloud_service_group = StringType(default='Recommender')


class RecommendationResource(RecommenderResource):
    cloud_service_type = StringType(default='Recommendation')
    data = ModelType(Recommendation)
    _metadata = ModelType(CloudServiceMeta, default=recommendation_meta, serialized_name='metadata')


class RecommendationResponse(CloudServiceResponse):
    resource = PolyModelType(RecommendationResource)
