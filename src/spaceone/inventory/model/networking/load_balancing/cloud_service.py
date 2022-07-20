from spaceone.inventory.model.networking.load_balancing.data import *
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, EnumDyField, ListDyField, DateTimeDyField
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, TableDynamicLayout
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta
from schematics.types import ModelType, StringType, PolyModelType

'''
LOAD BALANCING
'''

lb_forwarding_rule = TableDynamicLayout.set_fields('Forwarding Rule', root_path='data.forwarding_rules', fields=[
    TextDyField.data_source('Id', 'id'),
    TextDyField.data_source('Name', 'name'),
    TextDyField.data_source('Description', 'description'),
    EnumDyField.data_source('Source', 'type', default_badge={
        'coral.600': ['Global'], 'peacock.500': ['Regional']
    }),
    TextDyField.data_source('Region', 'region'),
    TextDyField.data_source('IP Address', 'ip_address'),
    EnumDyField.data_source('Protocol', 'ip_protocol', default_outline_badge=['TCP', 'UDP', 'ESP', 'AH', 'SCTP', 'ICMP',
                                                                              'L3_DEFAULT']),
    TextDyField.data_source('Port Range', 'port_range'),
    TextDyField.data_source('Ports', 'ports'),
    TextDyField.data_source('Target', 'target'),
    EnumDyField.data_source('Load Balancing Scheme', 'load_balancing_scheme', default_outline_badge=['EXTERNAL', 'EXTERNAL_MANAGED', 'INTERNAL', 'INTERNAL_MANAGED',
                                                                            'INTERNAL_SELF_MANAGED']),
    TextDyField.data_source('Subnetwork', 'subnetwork'),
    TextDyField.data_source('Network', 'network'),
    TextDyField.data_source('Backend Service', 'backend_service'),
    TextDyField.data_source('Service Label', 'service_label'),
    TextDyField.data_source('Service Name', 'service_name'),
    TextDyField.data_source('Network Tier', 'network_tier'),
    TextDyField.data_source('IP Version', 'ip_version'),
    EnumDyField.data_source('All Port', 'data.all_ports', default_badge={
        'indigo.500': ['true'], 'coral.600': ['false']
    }),
    EnumDyField.data_source('All Global Access', 'data.all_global_access', default_badge={
        'indigo.500': ['true'], 'coral.600': ['false']
    }),
    DateTimeDyField.data_source('Created At', 'data.creation_timestamp')
])

lb_target_proxy = ItemDynamicLayout.set_fields('Target Proxy', root_path='data.target_proxy', fields=[
    TextDyField.data_source('Name', 'name'),
    EnumDyField.data_source('Proxy Type', 'type', default_outline_badge=['GRPC', 'HTTP', 'HTTPS', 'SSL', 'TCP']),
    TextDyField.data_source('Description', 'description')
])

lb_urlmap = ItemDynamicLayout.set_fields('UrlMap', root_path='data.urlmap', fields=[
    TextDyField.data_source('ID', 'id'),
    TextDyField.data_source('Name', 'name'),
    TextDyField.data_source('Description', 'description'),
    TextDyField.data_source('Host Rule', 'host_rule'),
    DateTimeDyField.data_source('Created At', 'creation_timestamp'),
])

lb_certificate = TableDynamicLayout.set_fields('Certificate', root_path='data.certificates', fields=[
    TextDyField.data_source('ID', 'id'),
    TextDyField.data_source('Name', 'name'),
    ListDyField.data_source('Domain', 'domains'),
    EnumDyField.data_source('Type', 'data.all_global_access', default_badge={
        'indigo.500': ['SELF_MANAGED'], 'coral.600': ['MANAGED']
    }),
    TextDyField.data_source('Description', 'description'),
    TextDyField.data_source('Certificate', 'certificate'),
    ListDyField.data_source('Subnect Alternative Name', 'subject_alternative_names'),
    TextDyField.data_source('Expire Time', 'expire_time'),
    TextDyField.data_source('Region', 'region'),
    DateTimeDyField.data_source('Created At', 'creation_timestamp')
])

lb_backend_service = TableDynamicLayout.set_fields('Backend Service', root_path='data.backend_services', fields=[
    TextDyField.data_source('ID', 'id'),
    TextDyField.data_source('Name', 'name'),
    TextDyField.data_source('Description', 'description'),
    EnumDyField.data_source('Protocol', 'data.protocol',
                            default_outline_badge=['HTTP', 'HTTPS', 'HTTP2', 'TCP', 'SSL', 'UDP' 'GRPC']),
    ListDyField.data_source('Backends', 'backends'),
    ListDyField.data_source('Health Checks', 'health_checks'),
    TextDyField.data_source('TimeOut Seconds', 'timeout_sec'),
    TextDyField.data_source('Port', 'port'),
    TextDyField.data_source('Port Name', 'port_name'),
    EnumDyField.data_source('Type', 'data.enable_cdn', default_badge={
        'indigo.500': ['true'], 'coral.600': ['false']
    }),
    EnumDyField.data_source('Session Affinity', 'data.session_affinity',
                            default_outline_badge=['NONE', 'CLIENT_IP', 'CLIENT_IP_PROTO', 'CLIENT_IP_PORT_PROTO',
                                                   'INTERNAL_MANAGED', 'INTERNAL_SELF_MANAGED', 'GENERATED_COOKIE',
                                                   'HEADER_FIELD', 'HTTP_COOKIE']),
    TextDyField.data_source('Affinity Cookie TTL Seconds', 'affinity_cookie_ttl_sec'),
    TextDyField.data_source('FailOver Policy', 'failover_policy'),
    EnumDyField.data_source('LoadBalancing Scheme', 'data.load_balancing_scheme',
                            default_outline_badge=['EXTERNAL', 'INTERNAL', 'INTERNAL_MANAGED', 'INTERNAL_SELF_MANAGED']),
    TextDyField.data_source('Log Config', 'log_config'),
    TextDyField.data_source('Connection Draining', 'connection_draining'),
    DateTimeDyField.data_source('Created At', 'creation_timestamp')
])

lb_backend_buckets = TableDynamicLayout.set_fields('Backend Bucket', root_path='data.backend_buckets', fields=[
    TextDyField.data_source('Id', 'id'),
    TextDyField.data_source('Name', 'name'),
    TextDyField.data_source('Description', 'description'),
    TextDyField.data_source('Bucket Name', 'bucket_name'),
    EnumDyField.data_source('CDN', 'data.enable_cdn', default_badge={
        'indigo.500': ['true'], 'coral.600': ['false']
    }),
    TextDyField.data_source('CDN Policy', 'cdn_policy'),
    ListDyField.data_source('Custom Response Headers', 'custom_response_headers'),
    DateTimeDyField.data_source('Created At', 'creation_timestamp')
])

lb_target_pools = TableDynamicLayout.set_fields('Target Pool', root_path='data.target_pools', fields=[
    TextDyField.data_source('Id', 'id'),
    TextDyField.data_source('Name', 'name'),
    TextDyField.data_source('Description', 'description'),
    ListDyField.data_source('Health Check', 'health_checks'),
    TextDyField.data_source('Instance', 'instances'),
    EnumDyField.data_source('LoadBalancing Scheme', 'data.session_affinity',
                            default_outline_badge=['NONE', 'CLIENT_IP', 'CLIENT_IP_PROTO']),
    TextDyField.data_source('FailOver Ratio', 'failover_ratio'),
    TextDyField.data_source('Backup Pool', 'backup_pool'),
])

lb_health_checks = TableDynamicLayout.set_fields('Health Check', root_path='data.heath_checks', fields=[
    TextDyField.data_source('Id', 'id'),
    TextDyField.data_source('Name', 'name'),
    TextDyField.data_source('Description', 'description'),
    EnumDyField.data_source('Type', 'data.type',
                            default_outline_badge=['TCP', 'SSL', 'HTTP', 'HTTPS', 'HTTP2']),
    TextDyField.data_source('Check Interval Seconds', 'check_interval_sec'),
    TextDyField.data_source('TimeOut Seconds', 'timeout_sec'),
    TextDyField.data_source('UnHealthy Threshold', 'unhealthy_threshold'),
    TextDyField.data_source('Healthy Threshold', 'healthy_threshold'),
    TextDyField.data_source('Region', 'region'),
    TextDyField.data_source('Log Config', 'log_config'),
    DateTimeDyField.data_source('Created At', 'creation_timestamp')
])

lb_legacy_health_checks = TableDynamicLayout.set_fields('Legacy Health Check', root_path='data.legacy_health_checks', fields=[
    TextDyField.data_source('Id', 'id'),
    TextDyField.data_source('Name', 'name'),
    TextDyField.data_source('Description', 'description'),
    TextDyField.data_source('Host', 'host'),
    TextDyField.data_source('Port', 'port'),
    TextDyField.data_source('Request Path', 'request_path'),
    TextDyField.data_source('Check Interval Seconds', 'check_interval_sec'),
    TextDyField.data_source('Timeout Seconds', 'timeout_sec'),
    TextDyField.data_source('UnHealthy Threshold', 'unhealthy_threshold'),
    TextDyField.data_source('Healthy Threshold', 'healthy_threshold'),
    DateTimeDyField.data_source('Created At', 'creation_timestamp')
])

load_balancing_meta = CloudServiceMeta.set_layouts([lb_forwarding_rule,
                                                    lb_target_proxy,
                                                    lb_urlmap,
                                                    lb_backend_service,
                                                    lb_backend_buckets,
                                                    lb_target_pools,
                                                    lb_health_checks,
                                                    lb_legacy_health_checks])


class LoadBalancingResource(CloudServiceResource):
    cloud_service_group = StringType(default='Networking')


class LoadBalancingResource(LoadBalancingResource):
    cloud_service_type = StringType(default='LoadBalancing')
    data = ModelType(LoadBalancing)
    _metadata = ModelType(CloudServiceMeta, default=load_balancing_meta, serialized_name='metadata')


class LoadBalancingResponse(CloudServiceResponse):
    resource = PolyModelType(LoadBalancingResource)
