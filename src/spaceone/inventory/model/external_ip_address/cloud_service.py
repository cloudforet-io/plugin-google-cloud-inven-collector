from schematics.types import ModelType, StringType, PolyModelType

from spaceone.inventory.model.external_ip_address.data import *
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, EnumDyField, ListDyField, DateTimeDyField
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, TableDynamicLayout
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta

'''
INSTANCE
'''

# TAB - Bucket
external_ip_address_detail_meta = ItemDynamicLayout.set_fields('External IP Address Details', fields=[
    TextDyField.data_source('ID', 'data.id'),
    TextDyField.data_source('Name', 'data.name'),
    EnumDyField.data_source('Version', 'data.status_display', default_state={
            'safe': ['Reserved'],
            'warning': ['In Use'],
            'disable':['Reserving'],

    }),
    TextDyField.data_source('Region', 'data.region'),
    EnumDyField.data_source('Type', 'data.is_ephemeral', default_badge={
        'indigo.500': ['Static'], 'coral.600': ['Ephemeral']
    }),
    EnumDyField.data_source('Version', 'data.ip_version_display', default_badge={
        'indigo.500': ['IPv4'], 'coral.600': ['IPv6']
    }),
    ListDyField.data_source('In Used By', 'data.used_by'),
    ListDyField.data_source('In Used By (Details)', 'data.users'),
    TextDyField.data_source('Network Tier', 'data.network_tier_display'),
    DateTimeDyField.data_source('Creation Time', 'data.creation_timestamp'),
])


instance_template_meta = CloudServiceMeta.set_layouts([external_ip_address_detail_meta])


class VPCResource(CloudServiceResource):
    cloud_service_group = StringType(default='Networking')


class ExternalIpAddressResource(VPCResource):
    cloud_service_type = StringType(default='ExternalIPAddress')
    data = ModelType(ExternalIpAddress)
    _metadata = ModelType(CloudServiceMeta, default=instance_template_meta, serialized_name='metadata')


class ExternalIpAddressResponse(CloudServiceResponse):
    resource = PolyModelType(ExternalIpAddressResource)
