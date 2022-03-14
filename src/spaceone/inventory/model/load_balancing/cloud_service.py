from schematics.types import ModelType, StringType, PolyModelType

from spaceone.inventory.model.load_balancing.data import *
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, EnumDyField, ListDyField, DateTimeDyField
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, TableDynamicLayout, \
    SimpleTableDynamicLayout, ListDynamicLayout
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta

'''
INSTANCE
'''
lb_frontend_in_detaail = SimpleTableDynamicLayout.set_fields('Frontend',
                                                             root_path='data.frontends',
                                                             fields=[
                                                                 TextDyField.data_source('Name', 'name'),
                                                                 EnumDyField.data_source('Protocol', 'protocols',
                                                                                         default_badge={
                                                                                             'primary': ['HTTP',
                                                                                                         'HTTPS'],
                                                                                             'indigo.500': ['TCP'],
                                                                                             'coral.600': ['UDP']
                                                                                         }),
                                                                 ListDyField.data_source('Port', 'port'),
                                                                 TextDyField.data_source('Scope', 'scope'),
                                                                 ListDyField.data_source('Certificate', 'certificate'),
                                                                 EnumDyField.data_source('Network Tier',
                                                                                         'network_tier',
                                                                                         default_badge={
                                                                                             'indigo.500': ['Premium'],
                                                                                             'coral.600': ['Standard']
                                                                                         }),
                                                             ])

lb_host_path_in_detail = SimpleTableDynamicLayout.set_fields('Host & Path Rules',
                                                             root_path='data.host_and_paths',
                                                             fields=[
                                                                 ListDyField.data_source('Hosts', 'host'),
                                                                 ListDyField.data_source('Paths', 'path'),
                                                                 TextDyField.data_source('Name', 'backend'),
                                                             ])

lb_backend_url_map_in_detail = SimpleTableDynamicLayout.set_fields('Backend(URL Map)',
                                                                   root_path='data.backends.url_map_backend',
                                                                   fields=[
                                                                       TextDyField.data_source('Name', 'name'),
                                                                       TextDyField.data_source('Type', 'type'),
                                                                       TextDyField.data_source('Instance Name',
                                                                                               'instance_name'),
                                                                       EnumDyField.data_source('Cloud CDN', 'cloud_cdn',
                                                                                               default_badge={
                                                                                                   'indigo.500': [
                                                                                                       'enabled'],
                                                                                                   'coral.600': [
                                                                                                       'disabled']
                                                                                               }),
                                                                       ListDyField.data_source('Health Check',
                                                                                               'health_check'),
                                                                       EnumDyField.data_source('Scheme', 'scheme',
                                                                                               default_badge={
                                                                                                   'indigo.500': [
                                                                                                       'EXTERNAL'],
                                                                                                   'coral.600': [
                                                                                                       'INTERNAL']
                                                                                               }),
                                                                       TextDyField.data_source('Endpoint Protocol',
                                                                                               'end_point_protocol'),
                                                                       TextDyField.data_source('Named port',
                                                                                               'named_port'),
                                                                       TextDyField.data_source('Timeout', 'timeout'),
                                                                       TextDyField.data_source('Autoscaling',
                                                                                               'autoscaling_display'),
                                                                       TextDyField.data_source('Balancing Mode',
                                                                                               'balancing_mode_display'),
                                                                       TextDyField.data_source('Capacity',
                                                                                               'capacity_display'),

                                                                       ListDyField.data_source('Selected Port',
                                                                                               'selected_port',
                                                                                               options={
                                                                                                   'delimiter': '<br>'}),
                                                                   ])

lb_backend_target_pool_item_in_detail = ItemDynamicLayout.set_fields('Backend(Target Pool)',
                                                                     root_path='data.backends.target_pool_backend',
                                                                     fields=[
                                                                         TextDyField.data_source('Name', 'name'),
                                                                         TextDyField.data_source('Region', 'region'),
                                                                         TextDyField.data_source('Session Affinity',
                                                                                                 'session_affinity'),
                                                                         ListDyField.data_source('Health Check',
                                                                                                 'health_check'),
                                                                         TextDyField.data_source('Backup Pool',
                                                                                                 'backup_pool'),
                                                                         TextDyField.data_source('Failover Ratio',
                                                                                                 'fail_over_display'),
                                                                     ])

lb_backend_target_pool_table_in_detail = SimpleTableDynamicLayout.set_fields('Backend Instances (Target Pool) ',
                                                                             root_path='data.backends.target_pool_backend.backend_instances',
                                                                             fields=[
                                                                                 TextDyField.data_source('Name',
                                                                                                         'name'),
                                                                                 TextDyField.data_source('Type',
                                                                                                         'type'),
                                                                                 TextDyField.data_source('Region',
                                                                                                         'region'),
                                                                                 TextDyField.data_source('Zone',
                                                                                                         'zone'),
                                                                                 ListDyField.data_source('Address',
                                                                                                         'address'),
                                                                             ])

lb_details_tab_in_backend_proxy = SimpleTableDynamicLayout.set_fields('Backend (Proxy)',
                                                                      root_path='data.backends.proxy_backend',
                                                                      fields=[
                                                                          TextDyField.data_source('Name', 'name'),
                                                                          TextDyField.data_source('Type', 'type'),
                                                                          TextDyField.data_source('Instance Name',
                                                                                                  'instance_name'),
                                                                          EnumDyField.data_source('Cloud CDN',
                                                                                                  'cloud_cdn',
                                                                                                  default_badge={
                                                                                                      'indigo.500': [
                                                                                                          'enabled'],
                                                                                                      'coral.600': [
                                                                                                          'disabled']
                                                                                                  }),
                                                                          ListDyField.data_source('Health Check',
                                                                                                  'health_check'),
                                                                          EnumDyField.data_source('Scheme', 'scheme',
                                                                                                  default_badge={
                                                                                                      'indigo.500': [
                                                                                                          'EXTERNAL'],
                                                                                                      'coral.600': [
                                                                                                          'INTERNAL']
                                                                                                  }),
                                                                          TextDyField.data_source('Endpoint Protocol',
                                                                                                  'end_point_protocol'),
                                                                          TextDyField.data_source('Named port',
                                                                                                  'named_port'),
                                                                          TextDyField.data_source('Timeout', 'timeout'),
                                                                          TextDyField.data_source('Autoscaling',
                                                                                                  'autoscaling_display'),
                                                                          TextDyField.data_source('Balancing Mode',
                                                                                                  'balancing_mode_display'),
                                                                          TextDyField.data_source('Capacity',
                                                                                                  'capacity_display'),

                                                                          ListDyField.data_source('Selected Port',
                                                                                                  'selected_port',
                                                                                                  options={
                                                                                                      'delimiter': '<br>'}),
                                                                      ])

load_balancing_details = ListDynamicLayout.set_layouts('Details', layouts=[lb_frontend_in_detaail,
                                                                           lb_host_path_in_detail,
                                                                           lb_backend_url_map_in_detail,
                                                                           lb_details_tab_in_backend_proxy,
                                                                           lb_backend_target_pool_item_in_detail,
                                                                           lb_backend_target_pool_table_in_detail,
                                                                           ])

lb_backend_meta = TableDynamicLayout.set_fields('Backends', root_path='data.backend_tabs', fields=[
    TextDyField.data_source('Name', 'name'),
    TextDyField.data_source('Type', 'type'),
    TextDyField.data_source('Scope', 'scope'),
    EnumDyField.data_source('Protocol', 'protocol', default_badge={
        'primary': ['HTTP', 'HTTPS'], 'indigo.500': ['TCP'], 'coral.600': ['UDP']
    }),
])

lb_frontend_meta = TableDynamicLayout.set_fields('Frontends', root_path='data.frontends', fields=[
    TextDyField.data_source('Name', 'name'),
    TextDyField.data_source('Scope', 'scope'),
    TextDyField.data_source('Address', 'ip_address'),
    ListDyField.data_source('Port', 'port'),
    EnumDyField.data_source('Protocol', 'protocols', default_badge={
        'primary': ['HTTP', 'HTTPS'], 'indigo.500': ['TCP'], 'coral.600': ['UDP']
    }),
    EnumDyField.data_source('Network Tier',
                            'network_tier',
                            default_badge={
                                'indigo.500': ['Premium'],
                                'coral.600': ['Standard']
                            }),
])

lb_forwarding_rule_meta = TableDynamicLayout.set_fields('Forwarding Rules', root_path='data.forwarding_rules', fields=[
    TextDyField.data_source('Name', 'name'),
    EnumDyField.data_source('Type', 'type', default_badge={'indigo.500': ['Global'], 'indigo.600': ['Regional']}),
    TextDyField.data_source('Region', 'region'),
    TextDyField.data_source('Address', 'ip_address'),
    TextDyField.data_source('Port', 'port_range'),
    EnumDyField.data_source('Protocol', 'ip_protocol', default_badge={
        'primary': ['HTTP', 'HTTPS'], 'indigo.500': ['TCP'], 'coral.600': ['UDP']
    }),
    TextDyField.data_source('Description', 'description'),
    DateTimeDyField.data_source('Creation Time', 'creation_timestamp')
])

lb_target_proxies_meta = TableDynamicLayout.set_fields('Target Proxies', root_path='data.target_proxies', fields=[
    TextDyField.data_source('Name', 'target_proxy_display.name'),
    EnumDyField.data_source('Type', 'target_proxy_display.type',
                            default_badge={
                                'primary': ['HTTP Proxy'],
                                'indigo.500': ['HTTPS Proxy'],
                                'coral.600': ['SSL Proxy'],
                                'peacock.500': ['TCP Proxy'],
                                'green.500': ['GRPC Proxy']
                            }),
    TextDyField.data_source('Target Resource', 'target_proxy_display.target_resource'),
    TextDyField.data_source('Description', 'target_proxy_display.description'),
    DateTimeDyField.data_source('Creation Time', 'target_proxy_display.creation_timestamp')
])

lb_health_checks_meta = TableDynamicLayout.set_fields('Health Checks', root_path='data.heath_check_vos.health_checks',
                                                      fields=[
                                                          TextDyField.data_source('Name', 'name'),
                                                          TextDyField.data_source('Healthy Threshold',
                                                                                  'healthy_threshold'),
                                                          TextDyField.data_source('Unhealthy Threshold',
                                                                                  'unhealthy_threshold'),
                                                          TextDyField.data_source('Timeout in sec', 'timeout_sec'),
                                                          TextDyField.data_source('Check Interval',
                                                                                  'check_interval_sec'),
                                                          DateTimeDyField.data_source('Creation Time',
                                                                                      'creation_timestamp')
                                                      ])

lb_backend_service_meta = TableDynamicLayout.set_fields('Backend Services', root_path='data.backend_services', fields=[
    TextDyField.data_source('Name', 'name'),
    EnumDyField.data_source('Type', 'type', default_badge={'indigo.500': ['Global'], 'indigo.600': ['Regional']}),
    ListDyField.data_source('Region', 'region'),
    TextDyField.data_source('Description', 'description'),
    DateTimeDyField.data_source('Creation Time', 'creation_timestamp')
])

lb_certificates_meta = TableDynamicLayout.set_fields('Certificates', root_path='data.certificates', fields=[
    TextDyField.data_source('Name', 'name'),
    ListDyField.data_source('Domain', 'domains'),
    TextDyField.data_source('Expires', 'expire_time'),
    TextDyField.data_source('Type', 'type'),
    TextDyField.data_source('Status', 'managed.status'),
    TextDyField.data_source('Description', 'description'),
    DateTimeDyField.data_source('Creation Time', 'creation_timestamp')
])

lb_target_pools_meta = TableDynamicLayout.set_fields('Target Pools', root_path='data.target_pools', fields=[
    TextDyField.data_source('Name', 'name'),
    TextDyField.data_source('Region', '_region'),
    TextDyField.data_source('Instances', 'num_of_instance'),
    ListDyField.data_source('Health Check', '_health_checks'),
])

load_balancing_meta = CloudServiceMeta.set_layouts([load_balancing_details,
                                                    lb_backend_meta,
                                                    lb_frontend_meta,
                                                    lb_forwarding_rule_meta,
                                                    lb_target_proxies_meta,
                                                    lb_health_checks_meta,
                                                    lb_backend_service_meta,
                                                    lb_certificates_meta,
                                                    lb_target_pools_meta])


class LoadBalancingResource(CloudServiceResource):
    cloud_service_group = StringType(default='Networking')


class LoadBalancingResource(LoadBalancingResource):
    cloud_service_type = StringType(default='LoadBalancing')
    data = ModelType(LoadBalancing)
    _metadata = ModelType(CloudServiceMeta, default=load_balancing_meta, serialized_name='metadata')


class LoadBalancingResponse(CloudServiceResponse):
    resource = PolyModelType(LoadBalancingResource)
