from schematics.types import ModelType, StringType, PolyModelType

from spaceone.inventory.model.instance_template.data import InstanceTemplate
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, DateTimeDyField, EnumDyField, ListDyField, SizeField
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, TableDynamicLayout, ListDynamicLayout
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta

'''
INSTANCE
'''
# TAB - Instance Template
instance_template_meta = ItemDynamicLayout.set_fields('Instance', fields=[
    TextDyField.data_source('ID', 'data.id'),
    TextDyField.data_source('Name', 'data.name'),
    TextDyField.data_source('Description', 'data.description'),
    TextDyField.data_source('Machine Type', 'data.machine_type'),
    ListDyField.data_source('In Used By', 'data.in_used_by',
                            default_badge={'type': 'outline', 'delimiter': '<br>'}),
    EnumDyField.data_source('IP Forward', 'data.ip_forward', default_badge={
        'indigo.500': ['true'], 'coral.600': ['false']
    }),
    TextDyField.data_source('Self Link', 'data.self_link'),
    ListDyField.data_source('Network Tags', 'data.network_tags',
                            default_badge={'type': 'outline', 'delimiter': '<br>'}),
    TextDyField.data_source('Fingerprint', 'data.fingerprint'),
    DateTimeDyField.data_source('Creation Time', 'data.creation_timestamp'),
])

meta_available_policy = ItemDynamicLayout.set_fields('Available policies', fields=[
    EnumDyField.data_source('Preemptibility', 'data.scheduling.preemptibility', default_badge={
        'primary': ['On'], 'coral.600': ['Off']
    }),
    EnumDyField.data_source('Automatic Restart', 'data.scheduling.automatic_restart', default_badge={
        'primary': ['On'], 'coral.600': ['Off']
    }),
    EnumDyField.data_source('Host Maintenance', 'data.on_host_maintenance', default_badge={
        'primary': ['MIGRATE'], 'coral.600': ['TERMINATE']
    }),

])

# TAB - Service Account
it_meta_service_account = ItemDynamicLayout.set_fields('Service Account', root_path='data.service_account', fields=[
    TextDyField.data_source('E-mail', 'email'),
    ListDyField.data_source('Scopes', 'scopes',
                            default_badge={'type': 'outline', 'delimiter': '<br>'})
])

instance_template = ListDynamicLayout.set_layouts('Instance Template', layouts=[instance_template_meta,
                                                                                meta_available_policy,
                                                                                it_meta_service_account])

# TAB - Network
# instance_template_meta_network
it_meta_network = TableDynamicLayout.set_fields('Network Interface', root_path='data.network_interfaces', fields=[
    TextDyField.data_source('Name', 'name'),
    TextDyField.data_source('Network', 'network_display'),
    ListDyField.data_source('Access Configs', 'configs'),
    ListDyField.data_source('Network Tier', 'network_tier'),
    TextDyField.data_source('Kind', 'network'),
])

# TAB - Disk
# instance_template_meta_disk
meta_it_disk = TableDynamicLayout.set_fields('Disks',  root_path='data.disks', fields=[
    TextDyField.data_source('Index', 'device_index'),
    TextDyField.data_source('Device Name', 'device'),
    TextDyField.data_source('Source Image', 'tags.source_image_display'),
    SizeField.data_source('Size', 'size'),
    EnumDyField.data_source('Disk Type', 'tags.disk_type',
                            default_outline_badge=['local-ssd', 'pd-balanced', 'pd-ssd', 'pd-standard']),
    EnumDyField.data_source('Mode', 'device_mode', default_badge={
        'indigo.500': ['READ_WRITE'], 'coral.600': ['READ_ONLY']
    }),
    EnumDyField.data_source('Auto Delete', 'tags.auto_delete', default_badge={
        'indigo.500': ['true'], 'coral.600': ['false']
    }),
    TextDyField.data_source('Read IOPS', 'tags.read_iops'),
    TextDyField.data_source('Write IOPS', 'tags.write_iops'),
    TextDyField.data_source('Read Throughput(MB/s)', 'tags.read_throughput'),
    TextDyField.data_source('Write Throughput(MB/s)', 'tags.write_throughput'),

])

meta_it_labels = TableDynamicLayout.set_fields('Labels', root_path='data.labels', fields=[
    TextDyField.data_source('Key', 'key'),
    TextDyField.data_source('Value', 'value'),
])

instance_template_meta = CloudServiceMeta.set_layouts([instance_template, it_meta_network, meta_it_disk, meta_it_labels])


class ComputeEngineResource(CloudServiceResource):
    cloud_service_group = StringType(default='ComputeEngine')


class InstanceTemplateResource(ComputeEngineResource):
    cloud_service_type = StringType(default='InstanceTemplate')
    data = ModelType(InstanceTemplate)
    _metadata = ModelType(CloudServiceMeta, default=instance_template_meta, serialized_name='metadata')


class InstanceTemplateResponse(CloudServiceResponse):
    resource = PolyModelType(InstanceTemplateResource)
