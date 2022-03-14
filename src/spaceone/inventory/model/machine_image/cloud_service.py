from schematics.types import ModelType, StringType, PolyModelType

from spaceone.inventory.model.machine_image.data import MachineImage
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, DateTimeDyField, EnumDyField, ListDyField, SizeField
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, TableDynamicLayout, ListDynamicLayout
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta

'''
INSTANCE
'''
# TAB - Instance Template
meta_machine_image = ItemDynamicLayout.set_fields('Instance', fields=[
    TextDyField.data_source('ID', 'data.id'),
    TextDyField.data_source('Name', 'data.name'),
    TextDyField.data_source('Description', 'data.description'),
    ListDyField.data_source('Location', 'data.storage_locations',
                            default_badge={'type': 'outline', 'delimiter': '<br>'}),
    TextDyField.data_source('Machine Type', 'data.machine.machine_type'),
    ListDyField.data_source('Network Tags', 'data.network_tags',
                            default_badge={'type': 'outline', 'delimiter': '<br>'}),
    EnumDyField.data_source('Status', 'data.status', default_badge={
        'primary': ['READY'], 'indigo.500': ['UPLOADING', 'CREATING'], 'coral.600': ['DELETING', 'INVALID']
    }),
    EnumDyField.data_source('Delete Protection', 'data.deletion_protection', default_badge={
        'indigo.500': ['true'], 'coral.600': ['false']
    }),
    TextDyField.data_source('Service accounts', 'data.service_account.email'),
    TextDyField.data_source('Total Storage Bytes', 'data.total_storage_bytes'),
    TextDyField.data_source('Fingerprint', 'data.fingerprint'),
    TextDyField.data_source('Self Link', 'data.self_link'),
    DateTimeDyField.data_source('Creation Time', 'data.creation_timestamp'),
])

# TAB - Network
# instance_template_meta_network
meta_available_policy = ItemDynamicLayout.set_fields('Available policies', fields=[
    EnumDyField.data_source('Preemptibility', 'data.scheduling.preemptibility', default_badge={
        'primary': ['On'], 'coral.600': ['Off']
    }),
    EnumDyField.data_source('Automatic Restart', 'data.scheduling.automatic_restart', default_badge={
        'primary': ['On'], 'coral.600': ['Off']
    }),
    EnumDyField.data_source('Host Maintenance', 'data.on_host_maintenance', default_badge={
        'primary': ['MIGRATE'], 'coral.600': ['TERMINATE']
    })
])


meta_machine_template = ListDynamicLayout.set_layouts('Machine Images', layouts=[meta_machine_image, meta_available_policy])


# TAB - Disk
# instance_template_meta_disk
it_meta_disk = TableDynamicLayout.set_fields('Disks',  root_path='data.disks', fields=[
    TextDyField.data_source('Index', 'device_index'),
    TextDyField.data_source('Name', 'device'),
    SizeField.data_source('Size', 'size'),
    EnumDyField.data_source('Disk Type', 'tags.disk_type',
                            default_outline_badge=['local-ssd', 'pd-balanced', 'pd-ssd', 'pd-standard']),
    EnumDyField.data_source('Mode', 'device_mode', default_badge={
        'indigo.500': ['READ_WRITE'], 'coral.600': ['READ_ONLY']
    }),
    TextDyField.data_source('Boot Image', 'boot_image.name'),
    EnumDyField.data_source('Encryption', 'encryption', default_badge={
        'primary': ['Google managed'], 'indigo.500': ['Customer managed'], 'coral.600': ['Customer supplied']
    }),
    EnumDyField.data_source('Boot Image', 'is_boot_image', default_badge={
        'indigo.500': ['true'], 'coral.600': ['false']
    }),
    TextDyField.data_source('Read IOPS', 'tags.read_iops'),
    TextDyField.data_source('Write IOPS', 'tags.write_iops'),
    TextDyField.data_source('Read Throughput(MB/s)', 'tags.read_throughput'),
    TextDyField.data_source('Write Throughput(MB/s)', 'tags.write_throughput'),
    EnumDyField.data_source('Auto Delete', 'tags.auto_delete', default_badge={
        'indigo.500': ['true'], 'coral.600': ['false']
    }),
])

# TAB - Network
# instance_template_meta_network
it_meta_network = TableDynamicLayout.set_fields('Network Interface', root_path='data.network_interfaces', fields=[
    TextDyField.data_source('Name', 'name'),
    TextDyField.data_source('Network', 'network_display'),
    TextDyField.data_source('Subnetwork', 'subnetwork_display'),
    TextDyField.data_source('Primary internal IP', 'primary_ip_address'),
    ListDyField.data_source('Alias IP range', 'alias_ip_ranges',
                            default_badge={'type': 'outline', 'delimiter': '<br>'}),
    TextDyField.data_source('Public IP', 'public_ip_address'),
    ListDyField.data_source('Access Configs', 'configs'),
    ListDyField.data_source('Network Tier', 'network_tier_display'),
    ListDyField.data_source('IP forwarding', 'ip_forward')
])

instance_template_meta = CloudServiceMeta.set_layouts([meta_machine_template,
                                                       it_meta_disk,
                                                       it_meta_network])


class ComputeEngineResource(CloudServiceResource):
    cloud_service_group = StringType(default='ComputeEngine')


class MachineImageResource(ComputeEngineResource):
    cloud_service_type = StringType(default='MachineImage')
    data = ModelType(MachineImage)
    _metadata = ModelType(CloudServiceMeta, default=instance_template_meta, serialized_name='metadata')


class MachineImageResponse(CloudServiceResponse):
    resource = PolyModelType(MachineImageResource)
