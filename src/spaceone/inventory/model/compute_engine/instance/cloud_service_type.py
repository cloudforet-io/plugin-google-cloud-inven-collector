import os

from spaceone.inventory.libs.common_parser import *
from spaceone.inventory.libs.schema.metadata.dynamic_widget import CardWidget, ChartWidget
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, SearchField, DateTimeDyField, ListDyField, \
    EnumDyField, SizeField
from spaceone.inventory.libs.schema.cloud_service_type import CloudServiceTypeResource, CloudServiceTypeResponse, \
    CloudServiceTypeMeta

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
    'spaceone:icon': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/Compute_Engine.svg',
}


cst_vm_instance._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source('Server ID', 'server_id', options={'is_optional': True}),
        TextDyField.data_source('Name', 'name'),
        TextDyField.data_source('Resource ID', 'reference.resource_id', options={'is_optional': True}),
        EnumDyField.data_source('Management State', 'state', default_badge={
            'green.500': ['Active'], 'gray.500': ['Deleted']
        }),
        TextDyField.data_source('Instance Type', 'data.compute.instance_type'),
        TextDyField.data_source('Core', 'data.hardware.core'),
        TextDyField.data_source('Memory', 'data.hardware.memory'),
        TextDyField.data_source('Provider', 'provider'),
        TextDyField.data_source('Cloud Service Group', 'cloud_service_group', options={'is_optional': True}),
        TextDyField.data_source('Cloud Service Type', 'cloud_service_type', options={'is_optional': True}),
        TextDyField.data_source('Instance ID', 'data.compute.instance_id', options={'is_optional': True}),
        TextDyField.data_source('Key Pair', 'data.compute.keypair', options={'is_optional': True}),
        TextDyField.data_source('Image', 'data.compute.image', options={'is_optional': True}),
        EnumDyField.data_source('Instance State', 'data.compute.instance_state', default_badge={
            'yellow.500': ['Pending', 'Rebooting', 'Shutting-Down', 'Stopping', 'Starting', 'Staging', 'Provisioning',
                           'Suspending', 'Deallocating', 'Repairing'],
            'green.500': ['Running'],
            'red.500': ['Stopped', 'Deallocated', 'Suspended'],
            'gray.500': ['Terminated']
        }),
        TextDyField.data_source('Availability Zone', 'data.compute.az'),
        TextDyField.data_source('OS Type', 'os_type', options={'is_optional': True}),
        TextDyField.data_source('OS', 'data.os.os_distro'),
        TextDyField.data_source('OS Architecture', 'data.os.os_arch', options={'is_optional': True}),
        TextDyField.data_source('Primary IP', 'primary_ip_address', options={'is_optional': True}),
        TextDyField.data_source('Public IP', 'nics.public_ip_address', options={'is_optional': True}),
        TextDyField.data_source('Public DNS', 'nics.tags.public_dns', options={'is_optional': True}),
        TextDyField.data_source('All IP', 'ip_addresses', options={'is_optional': True}),
        TextDyField.data_source('MAC Address', 'nics.mac_address', options={'is_optional': True}),
        TextDyField.data_source('CIDR', 'nics.cidr', options={'is_optional': True}),
        TextDyField.data_source('VPC ID', 'data.vpc.vpc_id', options={'is_optional': True}),
        TextDyField.data_source('VPC Name', 'data.vpc.vpc_name', options={'is_optional': True}),
        TextDyField.data_source('Subnet ID', 'data.subnet.subnet_id', options={'is_optional': True}),
        TextDyField.data_source('Subnet Name', 'data.subnet.subnet_name', options={'is_optional': True}),
        TextDyField.data_source('ELB Name', 'data.load_balancers.name', options={'is_optional': True}),
        TextDyField.data_source('ELB DNS', 'data.load_balancers.dns', options={'is_optional': True}),
        TextDyField.data_source('IAM Role ARN', 'data.aws.iam_instance_profile.arn', options={'is_optional': True}),
        TextDyField.data_source('EC2 Lifecycle', 'data.aws.lifecycle', options={'is_optional': True}),
        TextDyField.data_source('ELB DNS', 'data.load_balancers.dns', options={'is_optional': True}),
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
        SizeField.data_source('Network Received Throughput', 'data.monitoring.network.received_throughput.avg', options={
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
        SizeField.data_source('Network Received Throughput', 'data.monitoring.network.received_throughput.max', options={
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
        TextDyField.data_source('Region', 'region_code', options={'is_optional': True}, reference={
            "resource_type": "inventory.Region",
            "reference_key": "region_code"
        }),
        TextDyField.data_source('Project', 'project_id', options={"sortable": False}, reference={
            "resource_type": "identity.Project",
            "reference_key": "project_id"
        }),
        TextDyField.data_source('Service Accounts', 'collection_info.service_accounts', options={'is_optional': True},
                                reference={
                                    "resource_type": "identity.ServiceAccount",
                                    "reference_key": "service_account_id"
                                }),
        TextDyField.data_source('Secrets', 'collection_info.secrets', options={'is_optional': True}, reference={
            "resource_type": "secret.Secret",
            "reference_key": "secret_id"
        }),
        TextDyField.data_source('Collectors', 'collection_info.collectors', options={'is_optional': True}, reference={
            "resource_type": "inventory.Collector",
            "reference_key": "collector_id"
        }),
        TextDyField.data_source('Launched', 'launched_at', options={'is_optional': True}),
        DateTimeDyField.data_source('Last Collected', 'updated_at', options={"source_type": "iso8601"}),
        DateTimeDyField.data_source('Created', 'created_at', options={
            "source_type": "iso8601",
            "is_optional": True
        }),
        DateTimeDyField.data_source('Deleted', 'deleted_at', options={
            "source_type": "iso8601",
            "is_optional": True
        }),
    ],

    search=[
        SearchField.set(name='Server ID', key='server_id'),
        SearchField.set(name='Name', key='name'),
        SearchField.set(name='Resource ID', key='reference.resource_id'),
        SearchField.set(name='IP Address', key='ip_addresses'),
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
        SearchField.set(name='Key Pair', key='data.compute.keypair'),
        SearchField.set(name='Image', key='data.compute.image'),
        SearchField.set(name='Availability Zone', key='data.compute.az'),
        SearchField.set(name='OS Type', key='os_type',
                        enums={
                            'LINUX': {'label': 'Linux'},
                            'WINDOWS': {'label': 'Windows'}
                        }),
        SearchField.set(name='OS Distro', key='data.os.os_distro'),
        SearchField.set(name='OS Architecture', key='data.os.os_arch'),
        SearchField.set(name='MAC Address', key='nics.mac_address'),
        SearchField.set(name='Public IP Address', key='nics.public_ip_address'),
        SearchField.set(name='Public DNS', key='nics.tags.public_dns'),
        SearchField.set(name='VPC ID', key='data.vpc.vpc_id'),
        SearchField.set(name='VPC Name', key='data.vpc.vpc_name'),
        SearchField.set(name='Subnet ID', key='data.subnet.subnet_id'),
        SearchField.set(name='Subnet Name', key='data.subnet.subnet_name'),
        SearchField.set(name='ELB Name', key='data.load_balancers.name'),
        SearchField.set(name='ELB DNS', key='data.load_balancers.dns'),
        SearchField.set(name='Auto Scaling Group', key='data.auto_scaling_group.name'),
        SearchField.set(name='Core', key='data.hardware.core', data_type='integer'),
        SearchField.set(name='Memory', key='data.hardware.memory', data_type='float'),
        SearchField.set(name='Management State', key='state',
                        enums={
                            'ACTIVE': {'label': 'Active'},
                            'DELETED': {'label': 'Deleted'}
                        }),
        SearchField.set(name='Provider', key='provider', reference='identity.Provider'),
        SearchField.set(name='Account ID', key='account'),
        SearchField.set(name='Cloud Service Group', key='cloud_service_group'),
        SearchField.set(name='Cloud Service Type', key='cloud_service_type'),
        SearchField.set(name='Region', key='region_code', reference='inventory.Region'),
        SearchField.set(name='Project', key='project_id', reference='identity.Project'),
        SearchField.set(name='Project Group', key='project_group_id', reference='identity.ProjectGroup'),
        SearchField.set(name='Service Account', key='collection_info.service_accounts', reference='identity.ServiceAccount'),
        SearchField.set(name='Secret', key='collection_info.secrets', reference='secret.Secret'),
        SearchField.set(name='Launched', key='launched_at'),
        SearchField.set(name='Last Collected', key='updated_at', data_type='datetime'),
        SearchField.set(name='Created', key='created_at', data_type='datetime'),
        SearchField.set(name='Deleted', key='deleted_at', data_type='datetime')
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

