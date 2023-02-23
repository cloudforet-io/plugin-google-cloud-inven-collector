from schematics.types import ModelType, StringType, PolyModelType, DictType
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, ListDynamicLayout, \
    TableDynamicLayout
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, EnumDyField, DateTimeDyField
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta
from spaceone.inventory.model.recommender.insight.data import Insight

insight_detail = ItemDynamicLayout.set_fields('Insight Details', fields=[])

insight_a_meta = TableDynamicLayout.set_fields('', root_path='', fields=[])
insight_b_meta = TableDynamicLayout.set_fields('', root_path='', fields=[])

detail_meta = ListDynamicLayout.set_layouts('Details', layouts=[insight_detail])
insight_meta = CloudServiceMeta.set_layouts([detail_meta, insight_a_meta, insight_b_meta])


class RecommenderResource(CloudServiceResource):
    tags = DictType(StringType, serialize_when_none=False)
    cloud_service_group = StringType(default='Recommender')


class InsightResource(RecommenderResource):
    cloud_service_type = StringType(default='Insight')
    data = ModelType(Insight)
    _metadata = ModelType(CloudServiceMeta, default=insight_meta, serialized_name='metadata')


class InsightResponse(CloudServiceResponse):
    resource = PolyModelType(InsightResource)
