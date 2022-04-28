import os

from spaceone.inventory.libs.common_parser import *
from spaceone.inventory.libs.schema.metadata.dynamic_widget import CardWidget, ChartWidget
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, SearchField, DateTimeDyField, ListDyField, \
    EnumDyField, SizeField
from spaceone.inventory.libs.schema.cloud_service_type import CloudServiceTypeResource, CloudServiceTypeResponse, \
    CloudServiceTypeMeta

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, 'widget/total_count.yml')
count_by_region_conf = os.path.join(current_dir, 'widget/count_by_region.yml')
count_by_project_conf = os.path.join(current_dir, 'widget/count_by_project.yml')

cst_disk = CloudServiceTypeResource()
cst_disk.name = 'Disk'
cst_disk.provider = 'google_cloud'
cst_disk.group = 'ComputeEngine'
cst_disk.service_code = 'Compute Engine'
cst_disk.labels = ['Compute', 'Storage']
cst_disk.is_primary = True
cst_disk.tags = {
    'spaceone:icon': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/Compute_Engine.svg',
}

cst_disk._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source('Name', 'data.name'),
        TextDyField.data_source('ID', 'data.id'),
        TextDyField.data_source('Zone', 'data.zone'),
        TextDyField.data_source('Source Image', 'data.source_image_display'),
        EnumDyField.data_source('Disk Type', 'data.disk_type',
                                default_outline_badge=['local-ssd', 'pd-balanced', 'pd-ssd', 'pd-standard']),
        SizeField.data_source('Size', 'data.size'),
        ListDyField.data_source('In Used By', 'data.in_used_by',
                                default_badge={'type': 'outline', 'delimiter': '<br>'}),
        ListDyField.data_source('Snapshot Schedule', 'data.snapshot_schedule_display',
                                default_badge={'type': 'outline', 'delimiter': '<br>'}),
        TextDyField.data_source('Source Image', 'data.source_image_display', options={'is_optional': True}),


        TextDyField.data_source('Read IOPS', 'data.read_iops', options={'is_optional': True}),
        TextDyField.data_source('Write IOPS', 'data.write_iops', options={'is_optional': True}),
        TextDyField.data_source('Read Throughput(MB/s)', 'data.read_throughput', options={'is_optional': True}),
        TextDyField.data_source('Write Throughput(MB/s)', 'data.write_throughput', options={'is_optional': True}),

        DateTimeDyField.data_source('Creation Time', 'data.creation_timestamp'),
    ],
    search=[
        SearchField.set(name='ID', key='data.id'),
        SearchField.set(name='Name', key='data.name'),
        SearchField.set(name='Status', key='data.status'),
        SearchField.set(name='Disk Type', key='data.disk_type'),
        SearchField.set(name='Size (Bytes)', key='data.size', data_type='integer'),
        SearchField.set(name='Project', key='data.project'),
        SearchField.set(name='Zone', key='data.zone'),
        SearchField.set(name='Region', key='region_code'),
        SearchField.set(name='Creation Time', key='data.creation_timestamp', data_type='datetime'),
    ],

    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_project_conf))
    ]
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({'resource': cst_disk}),
]
