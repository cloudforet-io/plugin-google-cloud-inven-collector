from schematics.types import ModelType, StringType, PolyModelType

from spaceone.inventory.model.health_check.data import *
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, DateTimeDyField, EnumDyField, \
    ListDyField, SizeField
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, TableDynamicLayout, \
    ListDynamicLayout, SimpleTableDynamicLayout
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta

'''
HEALTH CHECK
'''

# Details
# Metadata
health_check_details_meta = ItemDynamicLayout.set_fields('Information', fields=[
    TextDyField.data_source('ID', 'data.id'),
    TextDyField.data_source('Name', 'data.name')
])

# Dynamic View Field
health_check_meta = CloudServiceMeta.set_layouts([health_check_details_meta])


# Collector plugin data construction
class ComputeEngineResource(CloudServiceResource):
    cloud_service_group = StringType(default='ComputeEngine')


class HealthCheckResource(ComputeEngineResource):
    cloud_service_type = StringType(default='HealthCheck')
    data = ModelType(HealthCheck)
    _metadata = ModelType(CloudServiceMeta, default=health_check_meta, serialized_name='metadata')


# Plugin response data struct
class HealthCheckResponse(CloudServiceResponse):
    resource = PolyModelType(HealthCheckResource)
