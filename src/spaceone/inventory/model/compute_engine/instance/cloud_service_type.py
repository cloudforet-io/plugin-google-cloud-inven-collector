import os

from spaceone.inventory.libs.common_parser import *
from spaceone.inventory.libs.schema.metadata.dynamic_widget import CardWidget, ChartWidget
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, SearchField, EnumDyField, SizeField
from spaceone.inventory.libs.schema.cloud_service_type import CloudServiceTypeResource, CloudServiceTypeResponse, \
    CloudServiceTypeMeta
from spaceone.inventory.conf.cloud_service_conf import *

current_dir = os.path.abspath(os.path.dirname(__file__))

total_count_conf = os.path.join(current_dir, 'widget/total_count.yml')
total_disk_size_conf = os.path.join(current_dir, 'widget/total_disk_size.yml')
total_memory_size_conf = os.path.join(current_dir, 'widget/total_memory_size.yml')
total_vcpu_count_conf = os.path.join(current_dir, 'widget/total_vcpu_count.yml')
count_by_account_conf = os.path.join(current_dir, 'widget/count_by_account.yml')
count_by_instance_type_conf = os.path.join(current_dir, 'widget/count_by_instance_type.yml')
count_by_region_conf = os.path.join(current_dir, 'widget/count_by_region.yml')

cst_vm_instance = CloudServiceTypeResource()
cst_vm_instance.name = 'Instance'
cst_vm_instance.provider = 'google_cloud'
cst_vm_instance.group = 'ComputeEngine'
cst_vm_instance.service_code = 'Compute Engine'
cst_vm_instance.labels = ['Compute', 'Server']
cst_vm_instance.is_primary = True
cst_vm_instance.is_major = True
cst_vm_instance.tags = {
    'spaceone:icon': f'{ASSET_URL}/Compute_Engine.svg',
}

cst_vm_instance._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        EnumDyField.data_source('Instance State', 'data.compute.instance_state', default_state={
            'safe': ['RUNNING'],
            'warning': ['STAGING', 'PROVISIONING', 'REPAIRING', 'STOPPING', 'SUSPENDING'],
            'disable': [],
            'alert': ['SUSPENDED', 'TERMINATED']
        }),
        TextDyField.data_source('Server ID', 'server_id', options={'is_optional': True}),
        TextDyField.data_source('Instance Type', 'data.compute.instance_type'),
        TextDyField.data_source('Core', 'data.hardware.core'),
        TextDyField.data_source('Memory', 'data.hardware.memory'),
        TextDyField.data_source('Preemptible', 'data.compute.scheduling.preemptible', options={'is_optional': True}),
        EnumDyField.data_source('Has GPU', 'data.display.has_gpu', default_badge={
            'indigo.500': ['True'], 'coral.600': ['False']}),
        TextDyField.data_source('Total GPU Count', 'data.total_gpu_count', options={'is_optional': True}),
        TextDyField.data_source('GPUs', 'data.display.gpus',
                                default_badge={'type': 'outline', 'delimiter': '<br>'}, options={'is_optional': True}),
        TextDyField.data_source('Instance ID', 'data.compute.instance_id', options={'is_optional': True}),
        TextDyField.data_source('Key Pair', 'data.compute.keypair', options={'is_optional': True}),
        TextDyField.data_source('Image', 'data.compute.image', options={'is_optional': True}),

        TextDyField.data_source('Availability Zone', 'data.compute.az'),
        TextDyField.data_source('OS Type', 'data.os.os_type', options={'is_optional': True}),
        TextDyField.data_source('OS', 'data.os.os_distro'),
        TextDyField.data_source('OS Architecture', 'data.os.os_arch', options={'is_optional': True}),
        TextDyField.data_source('Primary IP', 'data.primary_ip_address', options={'is_optional': True}),
        TextDyField.data_source('Public IP', 'data.compute.public_ip_address', options={'is_optional': True}),
        TextDyField.data_source('Public DNS', 'data.nics.tags.public_dns', options={'is_optional': True}),
        TextDyField.data_source('All IP', 'ip_addresses', options={'is_optional': True}),
        TextDyField.data_source('MAC Address', 'data.nics.mac_address', options={'is_optional': True}),
        TextDyField.data_source('CIDR', 'data.nics.cidr', options={'is_optional': True}),
        TextDyField.data_source('VPC ID', 'data.vpc.vpc_id', options={'is_optional': True}),
        TextDyField.data_source('VPC Name', 'data.vpc.vpc_name', options={'is_optional': True}),
        TextDyField.data_source('Subnet ID', 'data.subnet.subnet_id', options={'is_optional': True}),
        TextDyField.data_source('Subnet Name', 'data.subnet.subnet_name', options={'is_optional': True}),
        TextDyField.data_source('LB Name', 'data.load_balancers.name', options={'is_optional': True}),
        TextDyField.data_source('LB DNS', 'data.load_balancers.dns', options={'is_optional': True}),
        TextDyField.data_source('Managed Instance', 'data.google_cloud.is_managed_instance',
                                options={'is_optional': True}),
        TextDyField.data_source('LB DNS', 'data.load_balancers.dns', options={'is_optional': True}),
        TextDyField.data_source('Auto Scaling Group', 'data.auto_scaling_group.name', options={'is_optional': True}),
        TextDyField.data_source('CPU Utilization', 'data.monitoring.cpu.utilization.avg', options={
            'default': 0,
            'is_optional': True,
            'field_description': '(Daily Average)'
        }),
        TextDyField.data_source('Memory Usage', 'data.monitoring.memory.usage.avg', options={
            'default': 0,
            'is_optional': True,
            'field_description': '(Daily Average)'
        }),
        TextDyField.data_source('Disk Read IOPS', 'data.monitoring.disk.read_iops.avg', options={
            'default': 0,
            'is_optional': True,
            'field_description': '(Daily Average)'
        }),
        TextDyField.data_source('Disk Write IOPS', 'data.monitoring.disk.write_iops.avg', options={
            'default': 0,
            'is_optional': True,
            'field_description': '(Daily Average)'
        }),
        SizeField.data_source('Disk Read Throughput', 'data.monitoring.disk.read_throughput.avg', options={
            'default': 0,
            'is_optional': True,
            'field_description': '(Daily Average)'
        }),
        SizeField.data_source('Disk Write Throughput', 'data.monitoring.disk.write_throughput.avg', options={
            'default': 0,
            'is_optional': True,
            'field_description': '(Daily Average)'
        }),
        TextDyField.data_source('Network Received PPS', 'data.monitoring.network.received_pps.avg', options={
            'default': 0,
            'is_optional': True,
            'field_description': '(Daily Average)'
        }),
        TextDyField.data_source('Network Sent PPS', 'data.monitoring.network.sent_pps.avg', options={
            'default': 0,
            'is_optional': True,
            'field_description': '(Daily Average)'
        }),
        SizeField.data_source('Network Received Throughput', 'data.monitoring.network.received_throughput.avg',
                              options={
                                  'default': 0,
                                  'is_optional': True,
                                  'field_description': '(Daily Average)'
                              }),
        SizeField.data_source('Network Sent Throughput', 'data.monitoring.network.sent_throughput.avg', options={
            'default': 0,
            'is_optional': True,
            'field_description': '(Daily Average)'
        }),
        TextDyField.data_source('CPU Utilization', 'data.monitoring.cpu.utilization.max', options={
            'default': 0,
            'is_optional': True,
            'field_description': '(Daily Max)'
        }),
        TextDyField.data_source('Memory Usage', 'data.monitoring.memory.usage.max', options={
            'default': 0,
            'is_optional': True,
            'field_description': '(Daily Max)'
        }),
        TextDyField.data_source('Disk Read IOPS', 'data.monitoring.disk.read_iops.max', options={
            'default': 0,
            'is_optional': True,
            'field_description': '(Daily Max)'
        }),
        TextDyField.data_source('Disk Write IOPS', 'data.monitoring.disk.write_iops.max', options={
            'default': 0,
            'is_optional': True,
            'field_description': '(Daily Max)'
        }),
        SizeField.data_source('Disk Read Throughput', 'data.monitoring.disk.read_throughput.max', options={
            'default': 0,
            'is_optional': True,
            'field_description': '(Daily Max)'
        }),
        SizeField.data_source('Disk Write Throughput', 'data.monitoring.disk.write_throughput.max', options={
            'default': 0,
            'is_optional': True,
            'field_description': '(Daily Max)'
        }),
        TextDyField.data_source('Network Received PPS', 'data.monitoring.network.received_pps.ma', options={
            'default': 0,
            'is_optional': True,
            'field_description': '(Daily Max)'
        }),
        TextDyField.data_source('Network Sent PPS', 'data.monitoring.network.sent_pps.max', options={
            'default': 0,
            'is_optional': True,
            'field_description': '(Daily Max)'
        }),
        SizeField.data_source('Network Received Throughput', 'data.monitoring.network.received_throughput.max',
                              options={
                                  'default': 0,
                                  'is_optional': True,
                                  'field_description': '(Daily Max)'
                              }),
        SizeField.data_source('Network Sent Throughput', 'data.monitoring.network.sent_throughput.max', options={
            'default': 0,
            'is_optional': True,
            'field_description': '(Daily Max)'
        }),
        TextDyField.data_source('Account ID', 'account', options={'is_optional': True}),
        TextDyField.data_source('Launched', 'launched_at', options={'is_optional': True}),
    ],

    search=[
        SearchField.set(name='Server ID', key='server_id'),
        SearchField.set(name='IP Address', key='data.ip_addresses'),
        SearchField.set(name='Instance ID', key='data.compute.instance_id'),
        SearchField.set(name='Instance State', key='data.compute.instance_state',
                        enums={
                            'RUNNING': {'label': 'Running'},
                            'STOPPED': {'label': 'Stopped'},
                            'DEALLOCATED': {'label': 'Deallocated'},
                            'SUSPENDED': {'label': 'Suspended'},
                            'TERMINATED': {'label': 'Terminated'}
                        }),
        SearchField.set(name='Instance Type', key='data.compute.instance_type'),
        SearchField.set(name='Has GPU', key='data.display.has_gpu', data_type='boolean'),
        SearchField.set(name='Total GPU Count', key='data.total_gpu_count', data_type='integer'),
        SearchField.set(name='GPUs', key='data.display.gpus'),
        SearchField.set(name='Key Pair', key='data.compute.keypair'),
        SearchField.set(name='Image', key='data.compute.image'),
        SearchField.set(name='Availability Zone', key='data.compute.az'),
        SearchField.set(name='OS Type', key='data.os.os_type',
                        enums={
                            'LINUX': {'label': 'Linux'},
                            'WINDOWS': {'label': 'Windows'}
                        }),
        SearchField.set(name='OS Distro', key='data.os.os_distro'),
        SearchField.set(name='OS Architecture', key='data.os.os_arch'),
        SearchField.set(name='MAC Address', key='data.nics.mac_address'),
        SearchField.set(name='Public IP Address', key='data.nics.public_ip_address'),
        SearchField.set(name='Public DNS', key='data.nics.tags.public_dns'),
        SearchField.set(name='VPC ID', key='data.vpc.vpc_id'),
        SearchField.set(name='VPC Name', key='data.vpc.vpc_name'),
        SearchField.set(name='Subnet ID', key='data.subnet.subnet_id'),
        SearchField.set(name='Subnet Name', key='data.subnet.subnet_name'),
        SearchField.set(name='ELB Name', key='data.load_balancers.name'),
        SearchField.set(name='ELB DNS', key='data.load_balancers.dns'),
        SearchField.set(name='Auto Scaling Group', key='data.auto_scaling_group.name'),
        SearchField.set(name='Core', key='data.hardware.core', data_type='integer'),
        SearchField.set(name='Memory', key='data.hardware.memory', data_type='float'),
        SearchField.set(name='Account ID', key='account'),
        SearchField.set(name='Project Group', key='project_group_id', reference='identity.ProjectGroup'),
        SearchField.set(name='Launched', key='launched_at'),
    ],

    widget=[
        CardWidget.set(**get_data_from_yaml(total_count_conf)),
        CardWidget.set(**get_data_from_yaml(total_vcpu_count_conf)),
        CardWidget.set(**get_data_from_yaml(total_memory_size_conf)),
        CardWidget.set(**get_data_from_yaml(total_disk_size_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_region_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_instance_type_conf)),
        ChartWidget.set(**get_data_from_yaml(count_by_account_conf))
    ]
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({'resource': cst_vm_instance}),
]
