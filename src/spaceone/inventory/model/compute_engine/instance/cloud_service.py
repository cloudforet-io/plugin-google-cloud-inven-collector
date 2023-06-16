from schematics.types import ModelType, StringType, PolyModelType

from spaceone.inventory.model.compute_engine.instance.data import VMInstance
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, EnumDyField, ListDyField, \
    DateTimeDyField, SizeField, MoreField
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, TableDynamicLayout, \
    ListDynamicLayout, SimpleTableDynamicLayout
from spaceone.inventory.libs.schema.cloud_service import CloudServiceMeta, CloudServiceResource, \
    CloudServiceResponse

'''
VM Instance
'''
vm_instance = ItemDynamicLayout.set_fields('VM Instance', fields=[
    TextDyField.data_source('Account', 'data.compute.account'),
    TextDyField.data_source('Instance ID', 'data.compute.instance_id'),
    TextDyField.data_source('Instance Name', 'data.compute.instance_name'),
    EnumDyField.data_source('Instance State', 'data.compute.instance_state', default_state={
        'safe': ['RUNNING'],
        'warning': ['STAGING', 'PROVISIONING', 'REPAIRING', 'STOPPING', 'SUSPENDING'],
        'disable': [],
        'alert': ['SUSPENDED', 'TERMINATED']
    }),
    EnumDyField.data_source('Preemptible', 'data.google_cloud.scheduling.preemptible', default_badge={
        'indigo.500': ['true'], 'coral.600': ['false']
    }),
    EnumDyField.data_source('Is Managed Instance in Instance Group', 'data.google_cloud.is_managed_instance',
                            default_badge={
                                'indigo.500': ['true'], 'coral.600': ['false']
                            }),
    TextDyField.data_source('Instance Type', 'data.compute.instance_type'),
    EnumDyField.data_source('Has GPU', 'data.display.has_gpu', default_badge={
        'indigo.500': ['True'], 'coral.600': ['False']}),
    TextDyField.data_source('Total GPU Count', 'data.total_gpu_count'),
    ListDyField.data_source('GPUs', 'data.display.gpus',
                            default_badge={'type': 'outline', 'delimiter': '<br>'}),
    TextDyField.data_source('Image', 'data.compute.image'),
    TextDyField.data_source('Region', 'region_code'),
    TextDyField.data_source('Availability Zone', 'data.compute.az'),
    TextDyField.data_source('Reservation Affinity', 'data.google_cloud.reservation_affinity'),
    TextDyField.data_source('Self link', 'data.google_cloud.self_link'),
    EnumDyField.data_source('Deletion Protection', 'data.google_cloud.deletion_protection', default_badge={
        'indigo.500': ['true'], 'coral.600': ['false']
    }),
    TextDyField.data_source('Public IP', 'data.compute.public_ip_address'),
    ListDyField.data_source('IP Addresses', 'ip_addresses',
                            default_badge={'type': 'outline', 'delimiter': '<br>'}),
    ListDyField.data_source('Affected Rules', 'data.compute.security_groups',
                            default_badge={'type': 'outline', 'delimiter': '<br>'}),

    DateTimeDyField.data_source('Launched At', 'data.compute.launched_at'),
])

google_cloud_vpc = ItemDynamicLayout.set_fields('VPC', fields=[
    TextDyField.data_source('VPC ID', 'data.vpc.vpc_id'),
    TextDyField.data_source('VPC Name', 'data.vpc.vpc_name'),
    TextDyField.data_source('Subnet ID', 'data.subnet.subnet_id'),
    TextDyField.data_source('Subnet Name', 'data.subnet.subnet_name'),
])

instance_group_manager = ItemDynamicLayout.set_fields('InstanceGroupManager', fields=[
    TextDyField.data_source('Auto Scaler', 'data.autoscaler.name'),
    TextDyField.data_source('Auto Scaler ID', 'data.autoscaler.id'),
    TextDyField.data_source('Instance Group Name', 'data.autoscaler.instance_group.name'),
    TextDyField.data_source('Instance Template Name', 'data.autoscaler.instance_group.instance_template_name'),
])

operating_system_manager = ItemDynamicLayout.set_fields('Operating System', fields=[
    TextDyField.data_source('OS Type', 'os_type'),
    TextDyField.data_source('OS Distribution', 'data.os.os_distro'),
    TextDyField.data_source('OS Architecture', 'data.os.os_arch'),
    TextDyField.data_source('OS Version Details', 'data.os.details'),
    TextDyField.data_source('OS License', 'data.os.os_license'),
])

hardware_manager = ItemDynamicLayout.set_fields('Hardware', root_path='data.hardware', fields=[
    TextDyField.data_source('Core', 'core'),
    TextDyField.data_source('Memory', 'memory'),
    TextDyField.data_source('CPU Model', 'cpu_model'),
])

ssh_keys = SimpleTableDynamicLayout.set_tags('SSH Keys', root_path='data.google_cloud.ssh_keys.ssh_keys',
                                             fields=[
                                                 TextDyField.data_source('User Name', 'user_name'),
                                                 MoreField.data_source('Overview', 'display_name',
                                                                       options={
                                                                           'sub_key': 'ssh_key',
                                                                           'layout': {
                                                                               'name': 'SSH Key',
                                                                               'type': 'popup',
                                                                               'options': {
                                                                                   'layout': {
                                                                                       'type': 'raw'
                                                                                   }
                                                                               }
                                                                           }
                                                                       })
                                             ])
ssh_options = ItemDynamicLayout.set_fields('SSH Key Options', root_path='data.google_cloud.ssh_keys', fields=[
    TextDyField.data_source('Block project-wide SSH keys', 'block_project_ssh_keys')
])

service_accounts = TableDynamicLayout.set_fields('API and Identity Management',
                                                 root_path='data.google_cloud.service_accounts',
                                                 fields=[
                                                     TextDyField.data_source('Service Account', 'service_account'),
                                                     MoreField.data_source('Cloud API access scopes', 'display_name',
                                                                           options={
                                                                               'layout': {
                                                                                   'name': 'Details',
                                                                                   'options': {
                                                                                       'type': 'popup',
                                                                                       'layout': {
                                                                                           'type': 'simple-table',
                                                                                           'options': {
                                                                                               'root_path': 'scopes',
                                                                                               'fields': [
                                                                                                   {
                                                                                                       "type": "text",
                                                                                                       "key": "description",
                                                                                                       "name": "Scope Description"
                                                                                                   }
                                                                                               ]
                                                                                           }
                                                                                       }
                                                                                   }
                                                                               }
                                                                           })
                                                 ])

compute_engine = ListDynamicLayout.set_layouts('Compute Engine',
                                               layouts=[vm_instance, google_cloud_vpc, ssh_keys, ssh_options,
                                                        service_accounts, instance_group_manager])

disk = TableDynamicLayout.set_fields('Disk', root_path='data.disks', fields=[
    TextDyField.data_source('Index', 'device_index'),
    TextDyField.data_source('Name', 'tags.disk_name'),
    SizeField.data_source('Size', 'size'),
    TextDyField.data_source('Disk ID', 'tags.disk_id'),
    EnumDyField.data_source('Disk Type', 'tags.disk_type',
                            default_outline_badge=['local-ssd', 'pd-balanced', 'pd-ssd', 'pd-standard']),
    TextDyField.data_source('Read IOPS', 'tags.read_iops'),
    TextDyField.data_source('Write IOPS', 'tags.write_iops'),
    TextDyField.data_source('Read Throughput(MB/s)', 'tags.read_throughput'),
    TextDyField.data_source('Write Throughput(MB/s)', 'tags.write_throughput'),
    EnumDyField.data_source('Encrypted', 'tags.encrypted', default_badge={
        'indigo.500': ['true'], 'coral.600': ['false']
    }),
])

nic = TableDynamicLayout.set_fields('NIC', root_path='data.nics', fields=[
    TextDyField.data_source('Index', 'device_index'),
    ListDyField.data_source('IP Addresses', 'ip_addresses', options={'delimiter': '<br>'}),
    TextDyField.data_source('CIDR', 'cidr'),
    TextDyField.data_source('Public IP', 'public_ip_address')
])

firewall = TableDynamicLayout.set_fields('Firewalls', root_path='data.security_group', fields=[
    TextDyField.data_source('Priority', 'priority'),
    EnumDyField.data_source('Direction', 'direction', default_badge={
        'indigo.500': ['ingress'], 'coral.600': ['egress']
    }),
    EnumDyField.data_source('Action', 'action', default_badge={
        'indigo.500': ['allow'], 'coral.600': ['deny']
    }),
    TextDyField.data_source('Name', 'security_group_name'),
    TextDyField.data_source('Firewall ID', 'security_group_id'),
    TextDyField.data_source('Protocol', 'protocol'),
    TextDyField.data_source('Port Min.', 'port_range_min'),
    TextDyField.data_source('Port MAx.', 'port_range_max'),
    TextDyField.data_source('Description', 'description'),
])

lb = TableDynamicLayout.set_fields('LB', root_path='data.load_balancers', fields=[
    TextDyField.data_source('Name', 'name'),
    EnumDyField.data_source('Type', 'type', default_badge={
        'primary': ['HTTP', 'HTTPS'], 'indigo.500': ['TCP'], 'coral.600': ['UDP']
    }),
    ListDyField.data_source('Protocol', 'protocol', options={'delimiter': '<br>'}),
    ListDyField.data_source('Port', 'port', options={'delimiter': '<br>'}),
    EnumDyField.data_source('Scheme', 'scheme', default_badge={
        'indigo.500': ['EXTERNAL'], 'coral.600': ['INTERNAL']
    }),
])

labels = TableDynamicLayout.set_fields('Labels', root_path='data.google_cloud.labels', fields=[
    TextDyField.data_source('Key', 'key'),
    TextDyField.data_source('Value', 'value'),
])

tags = TableDynamicLayout.set_fields('Tags', root_path='data.google_cloud.tags', fields=[
    TextDyField.data_source('Item', 'key')
])

vm_instance_meta = CloudServiceMeta.set_layouts([compute_engine, labels, tags, disk, nic, firewall, lb])


class ComputeEngineResource(CloudServiceResource):
    cloud_service_group = StringType(default='ComputeEngine')


class VMInstanceResource(ComputeEngineResource):
    cloud_service_type = StringType(default='Instance')
    data = ModelType(VMInstance)
    _metadata = ModelType(CloudServiceMeta, default=vm_instance_meta, serialized_name='metadata')


class VMInstanceResponse(CloudServiceResponse):
    resource = PolyModelType(VMInstanceResource)
