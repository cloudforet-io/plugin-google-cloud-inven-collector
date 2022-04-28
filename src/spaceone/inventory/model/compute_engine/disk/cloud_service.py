from schematics.types import ModelType, StringType, PolyModelType

from spaceone.inventory.model.compute_engine.disk.data import Disk
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, DateTimeDyField, \
    EnumDyField, ListDyField, SizeField
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, TableDynamicLayout, ListDynamicLayout
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta

'''
Disk
'''

disk_properties_meta = ItemDynamicLayout.set_fields('Properties', fields=[
    TextDyField.data_source('ID', 'data.id'),
    TextDyField.data_source('Name', 'data.name'),
    EnumDyField.data_source('Disk Type', 'data.disk_type',
                            default_outline_badge=['local-ssd', 'pd-balanced', 'pd-ssd', 'pd-standard']),
    SizeField.data_source('Size', 'data.size'),
    TextDyField.data_source('Zone', 'data.zone'),
    ListDyField.data_source('In Used By', 'data.in_used_by',
                            default_badge={'type': 'outline', 'delimiter': '<br>'}),
    ListDyField.data_source('Snapshot Schedule', 'data.snapshot_schedule_display',
                            default_badge={'type': 'outline', 'delimiter': '<br>'}),
    EnumDyField.data_source('Encryption Type', 'data.encryption', default_badge={
        'primary': ['Google managed'], 'indigo.500': ['Customer managed'], 'coral.600': ['Customer supplied']
    }),
    TextDyField.data_source('Source Image', 'data.source_image_display'),
    DateTimeDyField.data_source('Last Attach Time', 'data.last_attach_timestamp'),
    DateTimeDyField.data_source('Last Detach Time', 'data.last_detach_timestamp'),
    DateTimeDyField.data_source('Creation Time', 'data.creation_timestamp'),
])

# TAB - Instance Group
disk_performance_meta = ItemDynamicLayout.set_fields('Estimated Performance', fields=[
    TextDyField.data_source('Read IOPS', 'data.read_iops'),
    TextDyField.data_source('Write IOPS', 'data.write_iops'),
    TextDyField.data_source('Read Throughput(MB/s)', 'data.read_throughput'),
    TextDyField.data_source('Write Throughput(MB/s)', 'data.write_throughput'),
])

schedule_meta = TableDynamicLayout.set_fields('Snapshot Schedule',  root_path='data.snapshot_schedule', fields=[
    TextDyField.data_source('ID', 'id'),
    TextDyField.data_source('Name', 'name'),
    TextDyField.data_source('Region', 'region'),
    ListDyField.data_source('Schedule Frequency (UTC)', 'snapshot_schedule_policy.schedule_display',
                            default_badge={'type': 'outline', 'delimiter': '<br>'}),
    TextDyField.data_source('Auto-delete Snapshots After', 'snapshot_schedule_policy.retention_policy.max_retention_days_display'),
    ListDyField.data_source('Storage Locations', 'storage_locations',
                            default_badge={'type': 'outline', 'delimiter': '<br>'}),
    DateTimeDyField.data_source('Creation Time', 'creation_timestamp')

])

meta_disk_template = ListDynamicLayout.set_layouts('Disks', layouts=[disk_properties_meta, disk_performance_meta])

it_meta_labels = TableDynamicLayout.set_fields('Labels', root_path='data.labels', fields=[
    TextDyField.data_source('Key', 'key'),
    TextDyField.data_source('Value', 'value'),
])

disk_meta = CloudServiceMeta.set_layouts([meta_disk_template, it_meta_labels, schedule_meta])


class ComputeEngineResource(CloudServiceResource):
    cloud_service_group = StringType(default='ComputeEngine')


class DiskResource(ComputeEngineResource):
    cloud_service_type = StringType(default='Disk')
    data = ModelType(Disk)
    _metadata = ModelType(CloudServiceMeta, default=disk_meta, serialized_name='metadata')


class DiskResponse(CloudServiceResponse):
    resource = PolyModelType(DiskResource)