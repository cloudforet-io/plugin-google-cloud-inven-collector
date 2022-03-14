from schematics import Model
from schematics.types import ModelType, ListType, StringType, IntType, DateTimeType, BooleanType, FloatType, \
    DictType, PolyModelType


class Labels(Model):
    key = StringType()
    value = StringType()


class InstanceGroupManagerVersionTargetSize(Model):
    fixed = IntType(serialize_when_none=False)
    percent = IntType(serialize_when_none=False)
    calculated = IntType(serialize_when_none=False)


class AutoScalingPolicyScaleInControl(Model):
    max_scaled_in_replicas = ModelType(InstanceGroupManagerVersionTargetSize,
                                       deserialize_from='maxScaledInReplicas')
    time_window_sec = IntType(deserialize_from='timeWindowSec')


class AutoScalerPolicyCPUUtilization(Model):
    utilization_target = FloatType(deserialize_from='utilizationTarget')


class LoadBalancingUtilization(Model):
    utilization_target = FloatType(deserialize_from='utilizationTarget')


class AutoScalerPolicyCustomMetricUtilization(Model):
    metric = StringType(serialize_when_none=False)
    filter = StringType(serialize_when_none=False)
    utilization_target_type = StringType(choices=('GAUGE', 'DELTA_PER_SECOND', 'DELTA_PER_MINUTE'),
                                         deserialize_from='utilizationTargetType', serialize_when_none=False)
    utilization_target = FloatType(deserialize_from='utilizationTarget')
    single_instance_assignment = FloatType(deserialize_from='singleInstanceAssignment', serialize_when_none=False)


class AutoScalerPolicy(Model):
    min_num_replicas = IntType(deserialize_from='minNumReplicas')
    max_num_replicas = IntType(deserialize_from='maxNumReplicas')
    scaler_in_control = ModelType(AutoScalingPolicyScaleInControl,
                                  deserialize_from='scaleInControl', serialize_when_none=False)
    cool_down_period_sec = IntType(deserialize_from='coolDownPeriodSec')
    cpu_utilization = ModelType(AutoScalerPolicyCPUUtilization, deserialize_from='cpuUtilization')
    custom_metric_utilizations = ListType(ModelType(AutoScalerPolicyCustomMetricUtilization),
                                          deserialize_from='customMetricUtilizations',
                                          serialize_when_none=False)
    loadbalancing_utilization = ModelType(LoadBalancingUtilization,
                                          deserialize_from='loadBalancingUtilization',
                                          serialize_when_none=False)
    mode = StringType(deserialize_from='mode')


class TargetTCPProxy(Model):
    id = StringType()
    name = StringType()
    description = StringType(default='')
    self_link = StringType(deserialize_from='selfLink', serialize_when_none=False)
    region = StringType(default='global')
    service = StringType()
    proxy_header = StringType(choices=['NONE', 'PROXY_V1'], deserialize_from='proxyHeader', serialize_when_none=False)
    creation_timestamp = DateTimeType(deserialize_from='creationTimestamp', serialize_when_none=False)
    kind = StringType()


class TargetSSLProxy(Model):
    id = StringType()
    name = StringType()
    description = StringType(default='')
    self_link = StringType(deserialize_from='selfLink', serialize_when_none=False)
    region = StringType(default='global')
    service = StringType()
    ssl_certificates = StringType(deserialize_from='sslCertificates', serialize_when_none=False)
    proxy_header = StringType(choices=['NONE', 'PROXY_V1'], deserialize_from='proxyHeader', serialize_when_none=False)
    ssl_policy = StringType(deserialize_from='sslPolicy', serialize_when_none=False)
    creation_timestamp = DateTimeType(deserialize_from='creationTimestamp', serialize_when_none=False)
    kind = StringType()


class TargetGRPCProxy(Model):
    id = StringType()
    name = StringType()
    description = StringType(default='')
    self_link = StringType(deserialize_from='selfLink', serialize_when_none=False)
    kind = StringType()
    region = StringType(default='global')
    self_link_with_id = StringType(deserialize_from='selfLinkWithId', serialize_when_none=False)
    url_map = StringType(deserialize_from='urlMap', serialize_when_none=False)
    validate_for_proxyless = BooleanType(deserialize_from='validateForProxyless', serialize_when_none=False)
    finger_print = StringType(deserialize_from='fingerprint', serialize_when_none=False)
    creation_timestamp = DateTimeType(deserialize_from='creationTimestamp', serialize_when_none=False)


class TargetHttpProxy(Model):
    id = StringType()
    name = StringType()
    description = StringType(default='')
    self_link = StringType(deserialize_from='selfLink', serialize_when_none=False)
    url_map = StringType(deserialize_from='urlMap', serialize_when_none=False)
    region = StringType(default='global')
    kind = StringType()
    proxy_bind = BooleanType(deserialize_from='proxyBind', serialize_when_none=False)
    finger_print = StringType(deserialize_from='fingerprint', serialize_when_none=False)
    creation_timestamp = DateTimeType(deserialize_from='creationTimestamp', serialize_when_none=False)


class TargetHttpsProxy(Model):
    id = StringType()
    name = StringType()
    description = StringType(default='')
    self_link = StringType(deserialize_from='selfLink', serialize_when_none=False)
    url_map = StringType(deserialize_from='urlMap', serialize_when_none=False)
    ssl_certificates = ListType(StringType, default=[], deserialize_from='sslCertificates', serialize_when_none=False)
    quic_override = StringType(deserialize_from='quicOverride', choices=['NONE', 'ENABLE', 'DISABLE'],
                               serialize_when_none=False)
    ssl_policy = StringType(deserialize_from='sslPolicy', serialize_when_none=False)
    region = StringType(default='global')
    proxy_bind = BooleanType(deserialize_from='proxyBind', serialize_when_none=False)
    http_filters = ListType(StringType, default=[], serialize_when_none=False)
    server_tls_policy = StringType(deserialize_from='serverTlsPolicy', serialize_when_none=False)
    authentication = StringType(serialize_when_none=False)
    authorization_policy = StringType(deserialize_from='authorizationPolicy', serialize_when_none=False)
    authorization = StringType(serialize_when_none=False)
    kind = StringType()
    creation_timestamp = DateTimeType(deserialize_from='creationTimestamp', serialize_when_none=False)


class TargetProxyDisplay(Model):
    name = StringType()
    description = StringType()
    type = StringType()
    target_resource = StringType()
    in_used_by_display = ListType(StringType(), default=[])
    creation_timestamp = DateTimeType(serialize_when_none=False)

class InUsedBy(Model):
    id = StringType()
    name = StringType()
    self_link = StringType()


class TargetProxy(Model):
    name = StringType()
    type = StringType()
    description = StringType()
    proxy_key = StringType()
    grpc_proxy = ModelType(TargetGRPCProxy, serialize_when_none=False)
    http_proxy = ModelType(TargetHttpProxy, serialize_when_none=False)
    https_proxy = ModelType(TargetHttpsProxy, serialize_when_none=False)
    tcp_proxy = ModelType(TargetTCPProxy, serialize_when_none=False)
    ssl_proxy = ModelType(TargetSSLProxy, serialize_when_none=False)
    target_proxy_display = ModelType(TargetProxyDisplay, serialize_when_none=False)
    in_used_by = ListType(ModelType(InUsedBy), default=[])


class ForwardingRule(Model):
    id = StringType()
    name = StringType()
    description = StringType()
    type = StringType(choices=['Global', 'Regional'])
    ip_address = StringType(deserialize_from='IPAddress', serialize_when_none=False)
    ip_protocol = StringType(deserialize_from='IPProtocol', serialize_when_none=False)
    port_range = StringType(deserialize_from='portRange', serialize_when_none=False)
    ports = ListType(StringType(), default=[])
    region = StringType(default='global')
    ip_version = StringType(deserialize_from='ipVersion', serialize_when_none=False)
    fingerprint = StringType(serialize_when_none=False)
    kind = StringType(serialize_when_none=False)
    target = StringType(serialize_when_none=False)
    self_link = StringType(deserialize_from='selfLink', serialize_when_none=False)
    load_balancing_scheme = StringType(choices=['EXTERNAL', 'INTERNAL', 'INTERNAL_MANAGED', 'INTERNAL_SELF_MANAGED'],
                                       serialize_when_none=False)
    subnetwork = StringType(serialize_when_none=False)
    network = StringType(serialize_when_none=False)
    back_service = StringType(serialize_when_none=False)
    service_label = StringType(serialize_when_none=False)
    service_name = StringType(serialize_when_none=False)
    network_tier = StringType(deserialize_from='networkTier', choices=('Premium', 'Standard'))
    creation_timestamp = DateTimeType(deserialize_from='creationTimestamp', serialize_when_none=False)


class LogConfig(Model):
    enable = BooleanType(serialize_when_none=False)
    sample_rate = IntType(deserialize_from='sampleRate', serialize_when_none=False)


class BackendServiceBackend(Model):
    description = StringType(serialize_when_none=False)
    group = StringType()
    balancing_mode = StringType(deserialize_from='balancingMode', choices=['RATE', 'UTILIZATION', 'CONNECTION'])
    max_utilization = FloatType(deserialize_from='maxUtilization', serialize_when_none=False)
    max_rate = IntType(deserialize_from='maxRate', serialize_when_none=False)
    max_rate_per_instance = FloatType(deserialize_from='maxRatePerInstance', serialize_when_none=False)
    max_rate_per_endpoint = FloatType(deserialize_from='maxRatePerEndpoint', serialize_when_none=False)
    max_connections = IntType(deserialize_from='maxConnections', serialize_when_none=False)
    max_connections_per_instance = IntType(deserialize_from='maxConnectionsPerInstance', serialize_when_none=False)
    max_connections_per_endpoint = IntType(deserialize_from='maxConnectionsPerEndpoint', serialize_when_none=False)
    capacity_scaler = FloatType(deserialize_from='capacityScaler', serialize_when_none=False)
    failover = BooleanType(serialize_when_none=False)


class FailOverPolicy(Model):
    disable_connection_drain_on_failover = BooleanType(deserialize_from='disableConnectionDrainOnFailover',
                                                       serialize_when_none=False)
    drop_traffic_if_unhealthy = BooleanType(deserialize_from='dropTrafficIfUnhealthy', serialize_when_none=False)
    failover_ratio = FloatType(deserialize_from='failoverRatio', serialize_when_none=False)


class ConnectionDraining(Model):
    draining_timeout_sec = IntType(deserialize_from='drainingTimeoutSec', serialize_when_none=False)


class BackendService(Model):
    id = StringType()
    name = StringType()
    description = StringType()
    region = StringType('global')
    type = StringType(choices=['Global', 'Regional'])
    backends = ListType(ModelType(BackendServiceBackend), default=[], serialize_when_none=False)
    health_checks = ListType(StringType(), default=[], deserialize_from='healthChecks', serialize_when_none=False)
    timeout_sec = IntType(deserialize_from='timeoutSec', serialize_when_none=False)
    port = IntType(serialize_when_none=False)
    protocol = StringType(choices=['HTTP', 'HTTPS', 'HTTP2', 'TCP', 'SSL', 'UDP' 'GRPC'])
    fingerprint = StringType()
    port_name = StringType(deserialize_from='portName', serialize_when_none=False)
    enable_cdn = BooleanType(deserialize_from='enableCDN', serialize_when_none=False)
    session_affinity = StringType(deserialize_from='sessionAffinity',
                                  choices=['NONE', 'CLIENT_IP', 'CLIENT_IP_PROTO', 'CLIENT_IP_PORT_PROTO',
                                           'INTERNAL_MANAGED', 'INTERNAL_SELF_MANAGED', 'GENERATED_COOKIE',
                                           'HEADER_FIELD', 'HTTP_COOKIE'],
                                  serialize_when_none=False)
    affinity_cookie_ttl_sec = IntType(deserialize_from='affinityCookieTtlSec', serialize_when_none=False)
    failover_policy = ModelType(FailOverPolicy, serialize_when_none=False)
    load_balancing_scheme = StringType(deserialize_from='loadBalancingScheme',
                                       choices=['EXTERNAL', 'INTERNAL', 'INTERNAL_MANAGED', 'INTERNAL_SELF_MANAGED'],
                                       serialize_when_none=False)
    log_config = ModelType(LogConfig, serialize_when_none=False)
    connection_draining = ModelType(ConnectionDraining, serialize_when_none=False)
    self_link = StringType(deserialize_from='selfLink')
    creation_timestamp = DateTimeType(deserialize_from='creationTimestamp')


class CDNPolicy(Model):
    signed_url_key_names = ListType(StringType(), default=[],
                                    deserialize_from='signedUrlKeyNames',
                                    serialize_when_none=False)
    signed_url_cache_max_age_sec = StringType(deserialize_from='signedUrlCacheMaxAgeSec')
    cache_mode = StringType(deserialize_from='cache_mode',
                            choices=['USE_ORIGIN_HEADERS', 'FORCE_CACHE_ALL', 'CACHE_ALL_STATIC'])
    default_ttl = IntType(deserialize_from='defaultTtl')
    max_ttl = IntType(deserialize_from='maxTtl')
    client_ttl = IntType(deserialize_from='clientTtl')


class BackEndBucket(Model):
    id = StringType()
    name = StringType()
    bucket_name = StringType(deserialize_from='bucketName')
    description = StringType()
    self_link = StringType(deserialize_from='selfLink')
    cdn_policy = ModelType(CDNPolicy, serialize_when_none=False)
    enable_cdn = BooleanType(deserialize_from='enableCdn', serialize_when_none=False)
    custom_response_headers = ListType(StringType(), default=[],
                                       deserialize_from='customResponseHeaders',
                                       serialize_when_none=False)
    creation_timestamp = DateTimeType(deserialize_from='creationTimestamp')
    kind = StringType()


class TargetPools(Model):
    id = StringType()
    name = StringType()
    description = StringType()
    region = StringType(serialize_when_none=False)
    _region = StringType()
    num_of_instance = IntType(default=0)
    health_checks = ListType(StringType(), deserialize_from='healthChecks', default=[])
    _health_checks = ListType(StringType(), default=[])
    instances = ListType(StringType(), default=[])
    session_affinity = StringType(deserialize_from='sessionAffinity', serialize_when_none=False)
    failover_ratio = FloatType(deserialize_from='failoverRatio', serialize_when_none=False)
    backup_pool = StringType(deserialize_from='backupPool', serialize_when_none=False)
    self_link = StringType(deserialize_from='selfLink')
    kind = StringType(serialize_when_none=False)


class BackendTab(Model):
    name = StringType()
    type = StringType()
    scope = StringType()
    protocol = StringType(default='')


class InstancesObject(Model):
    type = StringType()
    name = StringType()
    region = StringType()
    zone = StringType()
    address = ListType(StringType(), default=[])


class TargetPoolBackend(Model):
    name = StringType(serialize_when_none=False)
    region = StringType(serialize_when_none=False)
    session_affinity = StringType(serialize_when_none=False)
    health_check = ListType(StringType(), default=[], serialize_when_none=False)
    backup_pool = StringType(serialize_when_none=False)
    fail_over = FloatType()
    fail_over_display = StringType()
    backend_instances = ListType(ModelType(InstancesObject), default=[], serialize_when_none=False)


class UrlMapBackend(Model):
    name = StringType()
    type = StringType()
    region = StringType()
    instance_name = StringType()
    end_point_protocol = StringType(serialize_when_none=False)
    named_port = StringType(serialize_when_none=False)
    timeout = StringType(serialize_when_none=False)
    health_check = ListType(StringType(), default=[], serialize_when_none=False)
    cloud_cdn = StringType(serialize_when_none=False)
    autoscaling_policy = ModelType(AutoScalerPolicy, serialize_when_none=False)
    autoscaling_display = StringType(serialize_when_none=False)
    balancing_mode = StringType(serialize_when_none=False)
    balancing_mode_display = StringType(serialize_when_none=False)
    capacity = FloatType(serialize_when_none=False)
    capacity_display = StringType(serialize_when_none=False)
    scheme = StringType(serialize_when_none=False)
    selected_port = ListType(StringType(), serialize_when_none=False)
    custom_response_header = StringType(serialize_when_none=False)


class Backend(Model):
    type = StringType(choices=['proxy', 'target_pool', 'url_map'])
    proxy_backend = ListType(ModelType(UrlMapBackend), serialize_when_none=False)
    target_pool_backend = ModelType(TargetPoolBackend, serialize_when_none=False)
    url_map_backend = ListType(ModelType(UrlMapBackend), serialize_when_none=False)


class Frontend(Model):
    name = StringType()
    scope = StringType()
    region = StringType()
    protocols = StringType(choices=('HTTP', 'TCP', 'UDP', 'HTTPS'))
    ip_address = StringType()
    port = ListType(StringType(), default=[])
    certificate = ListType(StringType(), default=[])
    network_tier = StringType(choices=('Premium', 'Standard'))


class Managed(Model):
    domain = ListType(StringType(), default=[], serialize_when_none=False)
    status = StringType(serialize_when_none=False)
    domain_status = ListType(ModelType(Labels), default=[])


class SelfManaged(Model):
    certificate = StringType()
    private_key = StringType(deserialize_from='privateKey', serialize_when_none=False)


class Certificates(Model):
    id = StringType()
    name = StringType()
    type = StringType()
    domains = ListType(StringType())
    description = StringType(default='')
    certificate = StringType(serialize_when_none=False)
    private_key = StringType(deserialize_from='privateKey', serialize_when_none=False)
    managed = ModelType(Managed, serialize_when_none=False)
    self_managed = ModelType(SelfManaged, deserialize_from='selfManaged', serialize_when_none=False)
    subject_alternative_names = ListType(StringType(),
                                         default=[],
                                         deserialize_from='subjectAlternativeNames',
                                         serialize_when_none=False)
    region = StringType(serialize_when_none=False)
    expire_time = StringType(deserialize_from='expireTime', serialize_when_none=False)
    self_link = StringType(deserialize_from='selfLink')
    creation_timestamp = DateTimeType(deserialize_from='creationTimestamp')


class HostAndPathRule(Model):
    host = ListType(StringType())
    path = ListType(StringType())
    backend = StringType()


class LogConfigHealthCheck(Model):
    enable = BooleanType(serialize_when_none=False)


class HealthCheckSingle(Model):
    host = StringType(serialize_when_none=False)
    port = StringType(serialize_when_none=False)
    port_name = StringType(deserialize_from='portName', serialize_when_none=False)
    port_specification = StringType(deserialize_from='portSpecification', serialize_when_none=False)
    proxy_header = StringType(deserialize_from='proxyHeader', choices=['NONE', 'PROXY_V1'], serialize_when_none=False)
    response = StringType(deserialize_from='response', serialize_when_none=False)
    grpc_service_name = StringType(deserialize_from='grpcServiceName', serialize_when_none=False)


class LegacyHealthCheck(Model):
    id = StringType()
    name = StringType(serialize_when_none=False)
    description = StringType(serialize_when_none=False)
    host = StringType(serialize_when_none=False)
    request_path = StringType(deserialize_from='requestPath', serialize_when_none=False)
    port = IntType(serialize_when_none=False)
    check_interval_sec = IntType(deserialize_from='checkIntervalSec', serialize_when_none=False)
    timeout_sec = IntType(deserialize_from='timeoutSec', serialize_when_none=False)
    unhealthy_threshold = IntType(deserialize_from='unhealthyThreshold', serialize_when_none=False)
    healthy_threshold = IntType(deserialize_from='healthyThreshold', serialize_when_none=False)
    self_link = StringType(deserialize_from='selfLink', serialize_when_none=False)
    creation_timestamp = DateTimeType(deserialize_from='creationTimestamp')


class HealthCheck(Model):
    id = StringType()
    name = StringType()
    description = StringType(default='')
    check_interval_sec = IntType(deserialize_from='checkIntervalSec', serialize_when_none=False)
    timeout_sec = IntType(deserialize_from='timeoutSec', serialize_when_none=False)
    unhealthy_threshold = IntType(deserialize_from='unhealthyThreshold', serialize_when_none=False)
    healthy_threshold = IntType(deserialize_from='healthyThreshold', serialize_when_none=False)
    check_interval_sec = IntType(deserialize_from='checkIntervalSec', serialize_when_none=False)
    type = StringType(choices=['TCP', 'SSL', 'HTTP', 'HTTPS', 'HTTP2'], serialize_when_none=False)
    tcp_health_check = ModelType(HealthCheckSingle, deserialize_from='tcpHealthCheck', serialize_when_none=False)
    ssl_health_check = ModelType(HealthCheckSingle, deserialize_from='sslHealthCheck', serialize_when_none=False)
    http_health_check = ModelType(HealthCheckSingle, deserialize_from='httpHealthCheck', serialize_when_none=False)
    https_health_check = ModelType(HealthCheckSingle, deserialize_from='httpsHealthCheck', serialize_when_none=False)
    http2_health_check = ModelType(HealthCheckSingle, deserialize_from='http2HealthCheck', serialize_when_none=False)
    grpc_health_check = ModelType(HealthCheckSingle, deserialize_from='grpcHealthCheck', serialize_when_none=False)
    region = StringType(serialize_when_none=False)
    self_link = StringType(deserialize_from='selfLink')
    log_config = ModelType(LogConfigHealthCheck, deserialize_from='logConfig', serialize_when_none=False)
    creation_timestamp = DateTimeType(deserialize_from='creationTimestamp')


class HealthCheckVO(Model):
    health_check_list = ListType(StringType, default=[], serialize_when_none=False)
    health_check_self_link_list = ListType(StringType, default=[], serialize_when_none=False)
    health_checks = ListType(PolyModelType([HealthCheck, LegacyHealthCheck]), default=[], serialize_when_none=False)


class LoadBalancing(Model):
    id = StringType()
    name = StringType()
    description = StringType(default='')
    project = StringType()
    region = StringType()
    lb_type = StringType()
    lead_protocol = StringType(choices=('HTTP', 'TCP', 'UDP', 'HTTP(S)', 'TCP (Proxy)', 'UDP (Proxy)'))
    source_link = StringType(deserialize_from='identifier', serialize_when_none=False)
    self_link = StringType(default="")
    frontends = ListType(ModelType(Frontend), default=[], serialize_when_none=False)
    frontend_display = StringType(default="")
    host_and_paths = ListType(ModelType(HostAndPathRule), default=[], serialize_when_none=False)
    backend_tabs = ListType(ModelType(BackendTab, serialize_when_none=False))
    backends = ModelType(Backend, serialize_when_none=False)
    backends_display = StringType(default='')
    heath_check_vos = ModelType(HealthCheckVO, serialize_when_none=False)
    forwarding_rules = ListType(ModelType(ForwardingRule), default=[], serialize_when_none=False)
    target_proxies = ListType(ModelType(TargetProxy), default=[], serialize_when_none=False)
    backend_services = ListType(ModelType(BackendService), serialize_when_none=False)
    backend_buckets = ListType(ModelType(BackEndBucket), default=[], serialize_when_none=False)
    certificates = ListType(ModelType(Certificates), default=[], serialize_when_none=False)
    target_pools = ListType(ModelType(TargetPools), default=[])
    tags = ListType(ModelType(Labels), default=[])
    creation_timestamp = DateTimeType(deserialize_from='creationTimestamp')

    def reference(self, refer_link):
        return {
            "resource_id": self.self_link,
            "external_link": refer_link
        }
