from schematics.types import ModelType, StringType, PolyModelType, DictType
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, ListDynamicLayout, \
    TableDynamicLayout
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, EnumDyField, DateTimeDyField
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta
from spaceone.inventory.model.recommender.recommendation.data import Recommendation

recommendation_detail = ItemDynamicLayout.set_fields('Recommendation Details', fields=[])

recommendation_a_meta = TableDynamicLayout.set_fields('', root_path='', fields=[])
recommendation_b_meta = TableDynamicLayout.set_fields('', root_path='', fields=[])

detail_meta = ListDynamicLayout.set_layouts('Details', layouts=[recommendation_detail])
recommendation_meta = CloudServiceMeta.set_layouts([detail_meta, recommendation_a_meta, recommendation_b_meta])


class RecommenderResource(CloudServiceResource):
    tags = DictType(StringType, serialize_when_none=False)
    cloud_service_group = StringType(default='Recommender')


class RecommendationResource(RecommenderResource):
    cloud_service_type = StringType(default='Recommendation')
    data = ModelType(Recommendation)
    _metadata = ModelType(CloudServiceMeta, default=recommendation_meta, serialized_name='metadata')


class RecommendationResponse(CloudServiceResponse):
    resource = PolyModelType(RecommendationResource)
