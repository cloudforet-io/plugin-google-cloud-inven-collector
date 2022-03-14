from schematics.types import ModelType, StringType, PolyModelType

from spaceone.inventory.model.route.data import *
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, EnumDyField, ListDyField, DateTimeDyField
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, TableDynamicLayout
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta

'''
INSTANCE
'''

# TAB - Route
route_detail_meta = ItemDynamicLayout.set_fields('Route Details', fields=[
    TextDyField.data_source('Name', 'data.id'),
    TextDyField.data_source('Name', 'data.name'),
    TextDyField.data_source('Description', 'data.description'),
    TextDyField.data_source('Network', 'data.display.network_display'),
    TextDyField.data_source('Destination IP Address Range', 'data.dest_range'),
    TextDyField.data_source('Priority', 'data.priority'),
    ListDyField.data_source('Instance Tags (Detail)', 'data.display.instance_tags'),
    DateTimeDyField.data_source('Creation Time', 'data.creation_timestamp'),
])

# instance_template_meta_disk
route_applicable_inst_meta= TableDynamicLayout.set_fields('Applicable to Instances',  root_path='data.applicable_instance', fields=[
    TextDyField.data_source('Name', 'name'),
    TextDyField.data_source('Subnetwork', 'subnetwork'),
    TextDyField.data_source('Internal IP', 'address'),
    ListDyField.data_source('Tags', 'tags',
                            default_badge={'type': 'outline', 'delimiter': '<br>'}),
    ListDyField.data_source('Service Accounts', 'service_accounts'),
    TextDyField.data_source('Project', 'project'),
    ListDyField.data_source('Label', 'labels_display',
                            default_badge={'type': 'outline', 'delimiter': '<br>'}),
    DateTimeDyField.data_source('Creation Time', 'creation_timestamp')
])

instance_template_meta = CloudServiceMeta.set_layouts([route_detail_meta,
                                                       route_applicable_inst_meta])


class VPCResource(CloudServiceResource):
    cloud_service_group = StringType(default='Networking')


class RouteResource(VPCResource):
    cloud_service_type = StringType(default='Route')
    data = ModelType(Route)
    _metadata = ModelType(CloudServiceMeta, default=instance_template_meta, serialized_name='metadata')


class RouteResponse(CloudServiceResponse):
    resource = PolyModelType(RouteResource)
