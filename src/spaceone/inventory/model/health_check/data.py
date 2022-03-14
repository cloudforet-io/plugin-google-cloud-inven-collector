from schematics import Model
from schematics.types import ModelType, ListType, StringType, IntType, DateTimeType, BooleanType, FloatType, DictType, \
    UnionType, MultiType


class TcpHealthCheck(Model):
    port = IntType()
    port_name = StringType(deserialize_from='portName')
    port_specification = StringType(choices=('USE_FIXED_PORT', 'USE_NAMED_PORT', 'USE_SERVING_PORT'),
                                    deserialize_from='portSpecification')
    request = StringType()
    response = StringType()
    proxy_header = StringType(choices=('NONE', 'PROXY_V1'),
                              deserialize_from='proxyHeader')


class SslHealthCheck(Model):
    port = IntType()
    port_name = StringType(deserialize_from='portName')
    port_specification = StringType(choices=('USE_FIXED_PORT', 'USE_NAMED_PORT', 'USE_SERVING_PORT'),
                                    deserialize_from='portSpecification')
    request = StringType()
    response = StringType()
    proxy_header = StringType(deserialize_from='proxyHeader',
                              choices=('NONE', 'PROXY_V1'))


class HttpHealthCheck(Model):
    port = IntType()
    port_Name = StringType(deserialize_from='portName')
    port_specification = StringType(choices=('USE_FIXED_PORT', 'USE_NAMED_PORT', 'USE_SERVING_PORT'),
                                    deserialize_from='portSpecification')
    host = StringType()
    request_path = StringType(deserialize_from='requestPath')
    proxy_header = StringType(deserialize_from='proxyHeader',
                              choices=('NONE', 'PROXY_V1'))
    response = StringType()


class HttpsHealthCheck(Model):
    port = IntType()
    port_Name = StringType(deserialize_from='portName')
    port_specification = StringType(choices=('USE_FIXED_PORT', 'USE_NAMED_PORT', 'USE_SERVING_PORT'),
                                    deserialize_from='portSpecification')
    host = StringType()
    request_path = StringType(deserialize_from='requestPath')
    proxy_header = StringType(deserialize_from='proxyHeader',
                              choices=('NONE', 'PROXY_V1'))
    response = StringType()


class Http2HealthCheck(Model):
    port = IntType()
    port_Name = StringType(deserialize_from='portName')
    port_specification = StringType(choices=('USE_FIXED_PORT', 'USE_NAMED_PORT', 'USE_SERVING_PORT'),
                                    deserialize_from='portSpecification')
    host = StringType()
    request_path = StringType(deserialize_from='requestPath')
    proxy_header = StringType(deserialize_from='proxyHeader',
                              choices=('NONE', 'PROXY_V1'))
    response = StringType()


class GrpcHealthCheckSpec(Model):
    port = IntType()
    port_name = StringType()
    port_specification = StringType(choices=('USE_FIXED_PORT', 'USE_NAMED_PORT', 'USE_SERVING_PORT'),
                                    deserialize_from='portSpecification')
    grpc_service_name = StringType()


class LogConfig(Model):
    enable = BooleanType()


class HealthCheck(Model):
    id = StringType()
    name = StringType()
    description = StringType()
    check_interval_sec = IntType(deserialize_from='checkIntervalSec')
    timeout_sec = IntType(deserialize_from='timeoutSec')
    unhealthy_threshold = IntType(deserialize_from='unhealthyThreshold')
    healthy_threshold = IntType(deserialize_from='healthyThreshold')
    type = StringType(choices=('TCP', 'SSL', 'HTTP', 'HTTPS', 'HTTP2'))
    tcp_health_check = ModelType(TcpHealthCheck, deserialize_from='tcpHealthCheck')
    ssl_health_check = ModelType(SslHealthCheck, deserialize_from='sslHealthCheck')
    http_health_check = ModelType(HttpHealthCheck, deserialize_from='httpHealthCheck')
    https_health_check = ModelType(HttpsHealthCheck, deserialize_from='httpsHealthCheck')
    http2_health_check = ModelType(Http2HealthCheck, deserialize_from='http2HealthCheck')
    grpc_health_check = ModelType(GrpcHealthCheckSpec, deserialize_from='grpcHealthCheck')
    project = StringType()
    region = StringType()
    log_config = ModelType(LogConfig, deserialize_from='logConfig')
    kind = StringType()

    self_link = StringType(deserialize_from='selfLink')
    creation_time = DateTimeType(deserialize_from='creationTimestamp')

    def reference(self):
        return {
            "resource_id": self.self_link,
            "external_link": f"https://console.cloud.google.com/compute/healthChecks/details/{self.name}?project={self.project}"
        }
