from schematics.types import ModelType, StringType, PolyModelType, DictType
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, ListDynamicLayout, \
    SimpleTableDynamicLayout
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, EnumDyField, DateTimeDyField
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta
from spaceone.inventory.model.recommender.insight.data import Insight

insight_detail = ItemDynamicLayout.set_fields('Insight Details', fields=[
    TextDyField.data_source('name', 'data.name'),
    TextDyField.data_source('description', 'data.description'),
    EnumDyField.data_source('State', 'data.state_info.state', default_state={
        'safe': ['ACTIVE'],
        'disable': ['ACCEPTED'],
        'alert': ['STATE_UNSPECIFIED', 'DISMISSED'],
    }),
    EnumDyField.data_source('Severity', 'data.severity', default_badge={
        'indigo.500': ['CRITICAL', 'HIGH', 'SEVERITY_UNSPECIFIED'], 'yellow.500': ['MEDIUM', 'LOW']
    }),
    EnumDyField.data_source('Category', 'data.category', default_badge={
        'indigo.500': ['COST'],
        'peacock.500': ['SUSTAINABILITY'],
        'violet.500': ['RELIABILITY'],
        'blue.500': ['PERFORMANCE'],
        'green.500': ['MANAGEABILITY'],
        'yellow.500': ['SECURITY'],
        'coral.500': ['CATEGORY_UNSPECIFIED']
    }),
    TextDyField.data_source('Insight subtype', 'data.insight_subtype'),
    TextDyField.data_source('Insight type', 'data.display.insight_type'),
    DateTimeDyField.data_source('Resource creation time', 'data.content.resource_creation_time'),
    TextDyField.data_source('Resource is external', 'data.content.resource_is_external'),
    DateTimeDyField.data_source('Last refresh time', 'data.last_refresh_time'),
    TextDyField.data_source('Etag', 'data.etag'),
])
detail_meta = ListDynamicLayout.set_layouts('Details', layouts=[insight_detail])

recommendations = SimpleTableDynamicLayout.set_tags('Recommendations', root_path='data.associated_recommendations',
                                                    fields=[
                                                        TextDyField.data_source('Name', 'recommendation'),
                                                    ])
insight_recommendation_meta = ListDynamicLayout.set_layouts('Recommendation', layouts=[recommendations])

target_resources = SimpleTableDynamicLayout.set_tags('Target resource', root_path='data.target_resources')
insight_target_resource_meta = ListDynamicLayout.set_layouts('Target resource', layouts=[target_resources])

insight_meta = CloudServiceMeta.set_layouts([detail_meta, insight_recommendation_meta, insight_target_resource_meta])


class RecommenderResource(CloudServiceResource):
    tags = DictType(StringType, serialize_when_none=False)
    cloud_service_group = StringType(default='Recommender')


class InsightResource(RecommenderResource):
    cloud_service_type = StringType(default='Insight')
    data = ModelType(Insight)
    _metadata = ModelType(CloudServiceMeta, default=insight_meta, serialized_name='metadata')


class InsightResponse(CloudServiceResponse):
    resource = PolyModelType(InsightResource)
