from schematics import Model
from schematics.types import (
    ModelType,
    ListType,
    StringType,
    IntType,
    DateTimeType,
    BooleanType,
    FloatType,
)
from spaceone.inventory.libs.schema.cloud_service import BaseResource


class Labels(Model):
    key = StringType()
    value = StringType()


class TargetTCPProxy(Model):
    id = StringType()
    name = StringType()
    description = StringType(default="")
    self_link = StringType(deserialize_from="selfLink", serialize_when_none=False)
    service = StringType()
    proxy_header = StringType(
        choices=["NONE", "PROXY_V1"],
        deserialize_from="proxyHeader",
        serialize_when_none=False,
    )
    proxy_bind = BooleanType(deserialize_from="proxyBind", serialize_when_none=False)
    creation_timestamp = DateTimeType(
        deserialize_from="creationTimestamp", serialize_when_none=False
    )


class TargetSSLProxy(Model):
    id = StringType()
    name = StringType()
    description = StringType(default="")
    self_link = StringType(deserialize_from="selfLink", serialize_when_none=False)
    service = StringType()
    ssl_certificates = StringType(
        deserialize_from="sslCertificates", serialize_when_none=False
    )
    proxy_header = StringType(
        choices=["NONE", "PROXY_V1"],
        deserialize_from="proxyHeader",
        serialize_when_none=False,
    )
    ssl_policy = StringType(deserialize_from="sslPolicy", serialize_when_none=False)
    creation_timestamp = DateTimeType(
        deserialize_from="creationTimestamp", serialize_when_none=False
    )


class TargetGRPCProxy(Model):
    id = StringType()
    name = StringType()
    description = StringType(default="")
    self_link = StringType(deserialize_from="selfLink", serialize_when_none=False)
    self_link_with_id = StringType(
        deserialize_from="selfLinkWithId", serialize_when_none=False
    )
    url_map = StringType(deserialize_from="urlMap", serialize_when_none=False)
    validate_for_proxyless = BooleanType(
        deserialize_from="validateForProxyless", serialize_when_none=False
    )
    creation_timestamp = DateTimeType(
        deserialize_from="creationTimestamp", serialize_when_none=False
    )


class TargetHttpProxy(Model):
    id = StringType(serialize_when_none=False)
    name = StringType(serialize_when_none=False)
    description = StringType(default="", serialize_when_none=False)
    self_link = StringType(deserialize_from="selfLink", serialize_when_none=False)
    url_map = StringType(deserialize_from="urlMap", serialize_when_none=False)
    region = StringType(default="global", serialize_when_none=False)
    proxy_bind = BooleanType(deserialize_from="proxyBind", serialize_when_none=False)
    creation_timestamp = DateTimeType(
        deserialize_from="creationTimestamp", serialize_when_none=False
    )


class TargetHttpsProxy(Model):
    id = StringType()
    name = StringType()
    description = StringType(default="")
    self_link = StringType(deserialize_from="selfLink", serialize_when_none=False)
    url_map = StringType(deserialize_from="urlMap", serialize_when_none=False)
    ssl_certificates = ListType(
        StringType,
        default=[],
        deserialize_from="sslCertificates",
        serialize_when_none=False,
    )
    quic_override = StringType(
        deserialize_from="quicOverride",
        choices=["NONE", "ENABLE", "DISABLE"],
        serialize_when_none=False,
    )
    ssl_policy = StringType(deserialize_from="sslPolicy", serialize_when_none=False)
    region = StringType(serialize_when_none=False)
    proxy_bind = BooleanType(deserialize_from="proxyBind", serialize_when_none=False)
    server_tls_policy = StringType(
        deserialize_from="serverTlsPolicy", serialize_when_none=False
    )
    authorization_policy = StringType(
        deserialize_from="authorizationPolicy", serialize_when_none=False
    )
    creation_timestamp = DateTimeType(
        deserialize_from="creationTimestamp", serialize_when_none=False
    )


class TargetProxy(Model):
    name = StringType(serialize_when_none=False)
    type = StringType(
        choices=["GRPC", "HTTP", "HTTPS", "SSL", "TCP"],
        default="TCP",
        serialize_when_none=False,
    )
    description = StringType(serialize_when_none=False)
    grpc_proxy = ModelType(TargetGRPCProxy, serialize_when_none=False)
    http_proxy = ModelType(TargetHttpProxy, serialize_when_none=False)
    https_proxy = ModelType(TargetHttpsProxy, serialize_when_none=False)
    tcp_proxy = ModelType(TargetTCPProxy, serialize_when_none=False)
    ssl_proxy = ModelType(TargetSSLProxy, serialize_when_none=False)


class ForwardingRule(Model):
    id = StringType()
    name = StringType()
    description = StringType()
    type = StringType(choices=["Global", "Regional"])
    region = StringType()
    ip_address = StringType(deserialize_from="IPAddress", serialize_when_none=False)
    ip_protocol = StringType(
        deserialize_from="IPProtocol",
        choices=["TCP", "UDP", "ESP", "AH", "SCTP", "ICMP", "L3_DEFAULT"],
        serialize_when_none=False,
    )
    port_range = StringType(deserialize_from="portRange", serialize_when_none=False)
    ports = ListType(StringType(), default=[])
    target = StringType(serialize_when_none=False)
    self_link = StringType(deserialize_from="selfLink", serialize_when_none=False)
    load_balancing_scheme = StringType(
        choices=[
            "EXTERNAL",
            "EXTERNAL_MANAGED",
            "INTERNAL",
            "INTERNAL_MANAGED",
            "INTERNAL_SELF_MANAGED",
        ],
        serialize_when_none=False,
    )
    subnetwork = StringType(serialize_when_none=False)
    network = StringType(serialize_when_none=False)
    backend_service = StringType(
        deserialize_from="backendService", serialize_when_none=False
    )
    service_label = StringType(
        deserialize_from="serviceLabel", serialize_when_none=False
    )
    service_name = StringType(deserialize_from="serviceName", serialize_when_none=False)
    network_tier = StringType(
        deserialize_from="networkTier", choices=["Premium", "Standard"]
    )
    labels = ModelType(Labels, serialize_when_none=False)
    ip_version = StringType(deserialize_from="ipVersion", serialize_when_none=False)
    all_ports = BooleanType(deserialize_from="allPorts", serialize_when_none=False)
    all_global_access = BooleanType(
        deserialize_from="allowGlobalAccess", serialize_when_none=False
    )
    creation_timestamp = DateTimeType(
        deserialize_from="creationTimestamp", serialize_when_none=False
    )


class LogConfig(Model):
    enable = BooleanType(serialize_when_none=False)
    sample_rate = IntType(deserialize_from="sampleRate", serialize_when_none=False)


class BackendServiceBackend(Model):
    description = StringType(serialize_when_none=False)
    group = StringType()
    balancing_mode = StringType(
        deserialize_from="balancingMode", choices=["RATE", "UTILIZATION", "CONNECTION"]
    )
    max_utilization = FloatType(
        deserialize_from="maxUtilization", serialize_when_none=False
    )
    max_rate = IntType(deserialize_from="maxRate", serialize_when_none=False)
    max_rate_per_instance = FloatType(
        deserialize_from="maxRatePerInstance", serialize_when_none=False
    )
    max_rate_per_endpoint = FloatType(
        deserialize_from="maxRatePerEndpoint", serialize_when_none=False
    )
    max_connections = IntType(
        deserialize_from="maxConnections", serialize_when_none=False
    )
    max_connections_per_instance = IntType(
        deserialize_from="maxConnectionsPerInstance", serialize_when_none=False
    )
    max_connections_per_endpoint = IntType(
        deserialize_from="maxConnectionsPerEndpoint", serialize_when_none=False
    )
    capacity_scaler = FloatType(
        deserialize_from="capacityScaler", serialize_when_none=False
    )
    failover = BooleanType(serialize_when_none=False)


class FailOverPolicy(Model):
    disable_connection_drain_on_failover = BooleanType(
        deserialize_from="disableConnectionDrainOnFailover", serialize_when_none=False
    )
    drop_traffic_if_unhealthy = BooleanType(
        deserialize_from="dropTrafficIfUnhealthy", serialize_when_none=False
    )
    failover_ratio = FloatType(
        deserialize_from="failoverRatio", serialize_when_none=False
    )


class ConnectionDraining(Model):
    draining_timeout_sec = IntType(
        deserialize_from="drainingTimeoutSec", serialize_when_none=False
    )


class BackendService(Model):
    id = StringType()
    name = StringType()
    description = StringType()
    self_link = StringType(deserialize_from="selfLink")
    backends = ListType(
        ModelType(BackendServiceBackend), default=[], serialize_when_none=False
    )
    health_checks = ListType(
        StringType(),
        default=[],
        deserialize_from="healthChecks",
        serialize_when_none=False,
    )
    timeout_sec = IntType(deserialize_from="timeoutSec", serialize_when_none=False)
    port = IntType(serialize_when_none=False)
    protocol = StringType(
        choices=["HTTP", "HTTPS", "HTTP2", "TCP", "SSL", "UDP" "GRPC"]
    )
    port_name = StringType(deserialize_from="portName", serialize_when_none=False)
    enable_cdn = BooleanType(deserialize_from="enableCDN", serialize_when_none=False)
    session_affinity = StringType(
        deserialize_from="sessionAffinity",
        choices=[
            "NONE",
            "CLIENT_IP",
            "CLIENT_IP_PROTO",
            "CLIENT_IP_PORT_PROTO",
            "INTERNAL_MANAGED",
            "INTERNAL_SELF_MANAGED",
            "GENERATED_COOKIE",
            "HEADER_FIELD",
            "HTTP_COOKIE",
        ],
        serialize_when_none=False,
    )
    affinity_cookie_ttl_sec = IntType(
        deserialize_from="affinityCookieTtlSec", serialize_when_none=False
    )
    failover_policy = ModelType(
        FailOverPolicy, deserialize_from="failoverPolicy", serialize_when_none=False
    )
    load_balancing_scheme = StringType(
        deserialize_from="loadBalancingScheme",
        choices=["EXTERNAL", "INTERNAL", "INTERNAL_MANAGED", "INTERNAL_SELF_MANAGED"],
        serialize_when_none=False,
    )
    log_config = ModelType(LogConfig, serialize_when_none=False)
    connection_draining = ModelType(
        ConnectionDraining,
        deserialize_from="connectionDraining",
        serialize_when_none=False,
    )
    creation_timestamp = DateTimeType(deserialize_from="creationTimestamp")


class CDNPolicy(Model):
    signed_url_key_names = ListType(
        StringType(),
        default=[],
        deserialize_from="signedUrlKeyNames",
        serialize_when_none=False,
    )
    signed_url_cache_max_age_sec = StringType(
        deserialize_from="signedUrlCacheMaxAgeSec"
    )
    cache_mode = StringType(
        deserialize_from="cache_mode",
        choices=["USE_ORIGIN_HEADERS", "FORCE_CACHE_ALL", "CACHE_ALL_STATIC"],
    )
    default_ttl = IntType(deserialize_from="defaultTtl")
    max_ttl = IntType(deserialize_from="maxTtl")
    client_ttl = IntType(deserialize_from="clientTtl")


class BackEndBucket(Model):
    id = StringType(serialize_when_none=False)
    name = StringType(serialize_when_none=False)
    description = StringType(serialize_when_none=False)
    self_link = StringType(deserialize_from="selfLink")
    bucket_name = StringType(deserialize_from="bucketName", serialize_when_none=False)
    enable_cdn = BooleanType(deserialize_from="enableCdn", serialize_when_none=False)
    cdn_policy = ModelType(CDNPolicy, serialize_when_none=False)
    custom_response_headers = ListType(
        StringType(),
        default=[],
        deserialize_from="customResponseHeaders",
        serialize_when_none=False,
    )
    creation_timestamp = DateTimeType(deserialize_from="creationTimestamp")


class TargetPools(Model):
    id = StringType()
    name = StringType()
    description = StringType()
    health_checks = ListType(StringType(), deserialize_from="healthChecks", default=[])
    instances = ListType(StringType(), default=[])
    session_affinity = StringType(
        deserialize_from="sessionAffinity",
        choices=["NONE", "CLIENT_IP", "CLIENT_IP_PROTO"],
        serialize_when_none=False,
    )
    failover_ratio = FloatType(
        deserialize_from="failoverRatio", serialize_when_none=False
    )
    backup_pool = StringType(deserialize_from="backupPool", serialize_when_none=False)
    self_link = StringType(deserialize_from="selfLink")


class Managed(Model):
    domain = ListType(StringType(), default=[], serialize_when_none=False)
    status = StringType(serialize_when_none=False)
    domain_status = ModelType(
        Labels, deserialize_from="domainStatus", serialize_when_none=False
    )


class SelfManaged(Model):
    certificate = StringType()
    private_key = StringType(deserialize_from="privateKey", serialize_when_none=False)


class Certificates(Model):
    id = StringType()
    name = StringType()
    domains = ListType(StringType())
    description = StringType(serialize_when_none=False)
    self_link = StringType(deserialize_from="selfLink", serialize_when_none=False)
    certificate = StringType(serialize_when_none=False)
    private_key = StringType(deserialize_from="privateKey", serialize_when_none=False)
    managed = ModelType(Managed, serialize_when_none=False)
    self_managed = ModelType(
        SelfManaged, deserialize_from="selfManaged", serialize_when_none=False
    )
    type = StringType(choices=["SELF_MANAGED", "MANAGED"], serialize_when_none=False)
    subject_alternative_names = ListType(
        StringType(),
        default=[],
        deserialize_from="subjectAlternativeNames",
        serialize_when_none=False,
    )
    expire_time = StringType(deserialize_from="expireTime", serialize_when_none=False)
    region = StringType(serialize_when_none=False)
    creation_timestamp = DateTimeType(deserialize_from="creationTimestamp")


class HostRule(Model):
    description = StringType(serialize_when_none=False)
    host = ListType(StringType(), deserialize_from="hosts", serialize_when_none=False)
    path_matcher = StringType(deserialize_from="pathMatcher", serialize_when_none=False)


class UrlMap(Model):
    id = StringType(serialize_when_none=False)
    name = StringType
    description = StringType(serialize_when_none=False)
    self_link = StringType(deserialize_from="selfLink", serialize_when_none=False)
    host_rule = ListType(
        ModelType(HostRule), deserialize_from="hostRules", serialize_when_none=False
    )
    creation_timestamp = DateTimeType(deserialize_from="creationTimestamp")


class LogConfigHealthCheck(Model):
    enable = BooleanType(serialize_when_none=False)


class HealthCheckSingle(Model):
    host = StringType(serialize_when_none=False)
    port = StringType(serialize_when_none=False)
    port_name = StringType(deserialize_from="portName", serialize_when_none=False)
    port_specification = StringType(
        deserialize_from="portSpecification", serialize_when_none=False
    )
    proxy_header = StringType(
        deserialize_from="proxyHeader",
        choices=["NONE", "PROXY_V1"],
        serialize_when_none=False,
    )
    response = StringType(deserialize_from="response", serialize_when_none=False)
    grpc_service_name = StringType(
        deserialize_from="grpcServiceName", serialize_when_none=False
    )


class LegacyHealthCheck(Model):
    id = StringType()
    name = StringType(serialize_when_none=False)
    description = StringType(serialize_when_none=False)
    host = StringType(serialize_when_none=False)
    request_path = StringType(deserialize_from="requestPath", serialize_when_none=False)
    port = IntType(serialize_when_none=False)
    check_interval_sec = IntType(
        deserialize_from="checkIntervalSec", serialize_when_none=False
    )
    timeout_sec = IntType(deserialize_from="timeoutSec", serialize_when_none=False)
    unhealthy_threshold = IntType(
        deserialize_from="unhealthyThreshold", serialize_when_none=False
    )
    healthy_threshold = IntType(
        deserialize_from="healthyThreshold", serialize_when_none=False
    )
    self_link = StringType(deserialize_from="selfLink", serialize_when_none=False)
    creation_timestamp = DateTimeType(deserialize_from="creationTimestamp")


class HealthCheck(Model):
    id = StringType()
    name = StringType()
    description = StringType(default="")
    self_link = StringType(deserialize_from="selfLink")
    check_interval_sec = IntType(
        deserialize_from="checkIntervalSec", serialize_when_none=False
    )
    timeout_sec = IntType(deserialize_from="timeoutSec", serialize_when_none=False)
    unhealthy_threshold = IntType(
        deserialize_from="unhealthyThreshold", serialize_when_none=False
    )
    healthy_threshold = IntType(
        deserialize_from="healthyThreshold", serialize_when_none=False
    )
    type = StringType(
        choices=["TCP", "SSL", "HTTP", "HTTPS", "HTTP2"], serialize_when_none=False
    )
    tcp_health_check = ModelType(
        HealthCheckSingle, deserialize_from="tcpHealthCheck", serialize_when_none=False
    )
    ssl_health_check = ModelType(
        HealthCheckSingle, deserialize_from="sslHealthCheck", serialize_when_none=False
    )
    http_health_check = ModelType(
        HealthCheckSingle, deserialize_from="httpHealthCheck", serialize_when_none=False
    )
    https_health_check = ModelType(
        HealthCheckSingle,
        deserialize_from="httpsHealthCheck",
        serialize_when_none=False,
    )
    http2_health_check = ModelType(
        HealthCheckSingle,
        deserialize_from="http2HealthCheck",
        serialize_when_none=False,
    )
    grpc_health_check = ModelType(
        HealthCheckSingle, deserialize_from="grpcHealthCheck", serialize_when_none=False
    )
    region = StringType(serialize_when_none=False)
    log_config = ModelType(
        LogConfigHealthCheck, deserialize_from="logConfig", serialize_when_none=False
    )
    creation_timestamp = DateTimeType(deserialize_from="creationTimestamp")


class LoadBalancing(BaseResource):
    description = StringType(default="")
    internal_or_external = StringType(
        choices=["Internal", "External", "UnKnown"], serialize_when_none=False
    )
    type = StringType(
        choices=[
            "HTTP(S) LoadBalancer",
            "HTTP(S) LoadBalancer(classic)",
            "SSL Proxy LoadBalancer",
            "TCP Proxy LoadBalancer",
            "TCP/UDP Network LoadBalancer",
            "UnKnown",
        ],
        serialize_when_none=False,
    )
    protocol = StringType(
        choices=[
            "HTTP",
            "HTTPS",
            "TCP",
            "UDP",
            "ESP",
            "AH",
            "SCTP",
            "ICMP",
            "L3_DEFAULT",
            "UnKnown",
        ],
        serialize_when_none=False,
    )
    self_link = StringType(default="")
    forwarding_rules = ListType(ModelType(ForwardingRule), serialize_when_none=False)
    target_proxy = (ModelType(TargetProxy, serialize_when_none=False),)
    urlmap = ModelType(UrlMap, serialize_when_none=False)
    certificates = ListType(ModelType(Certificates), serialize_when_none=False)
    backend_services = ListType(ModelType(BackendService), serialize_when_none=False)
    backend_buckets = ListType(ModelType(BackEndBucket), serialize_when_none=False)
    heath_checks = ListType(ModelType(HealthCheck), serialize_when_none=False)
    legacy_health_checks = ListType(
        ModelType(LegacyHealthCheck), serialize_when_none=False
    )
    target_pools = ListType(ModelType(TargetPools), serialize_when_none=False)
    tags = ListType(ModelType(Labels), serialize_when_none=False)
    creation_timestamp = DateTimeType(deserialize_from="creationTimestamp")
    affected_instance_count = IntType(serialize_when_none=False, default=0)

    def reference(self, refer_link):
        return {"resource_id": self.self_link, "external_link": refer_link}
