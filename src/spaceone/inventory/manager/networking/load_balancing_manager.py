import time
import logging

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.connector.networking.load_balancing import (
    LoadBalancingConnector,
)
from spaceone.inventory.model.networking.load_balancing.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.networking.load_balancing.cloud_service import (
    LoadBalancingResource,
    LoadBalancingResponse,
)
from spaceone.inventory.model.networking.load_balancing.data import LoadBalancing

_LOGGER = logging.getLogger(__name__)


class LoadBalancingManager(GoogleCloudManager):
    connector_name = "LoadBalancingConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug(f"** Load Balancing START **")
        start_time = time.time()
        """
        Args:
            params:
                - options
                - schema
                - secret_data
                - filter
                - zones
        Response:
            CloudServiceResponse/ErrorResourceResponse
        """
        collected_cloud_services = []
        error_responses = []
        lb_id = ""

        secret_data = params["secret_data"]
        loadbalancing_conn: LoadBalancingConnector = self.locator.get_connector(
            self.connector_name, **params
        )

        project_id = secret_data.get("project_id")

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################

        # Getting all components for loadbalancing
        forwarding_rules = loadbalancing_conn.list_forwarding_rules()

        # Extend all types of proxies
        load_balancers = []
        all_proxies = []
        grpc_proxies = loadbalancing_conn.list_grpc_proxies()
        load_balancers.extend(grpc_proxies)
        all_proxies.extend(grpc_proxies)

        http_proxies = loadbalancing_conn.list_target_http_proxies()
        load_balancers.extend(http_proxies)
        all_proxies.extend(http_proxies)

        https_proxies = loadbalancing_conn.list_target_https_proxies()
        load_balancers.extend(https_proxies)
        all_proxies.extend(https_proxies)

        ssl_proxies = loadbalancing_conn.list_ssl_proxies()
        load_balancers.extend(ssl_proxies)
        all_proxies.extend(ssl_proxies)

        tcp_proxies = loadbalancing_conn.list_tcp_proxies()
        load_balancers.extend(tcp_proxies)
        all_proxies.extend(tcp_proxies)

        # SSL Cert for proxy
        ssl_certificates = loadbalancing_conn.list_ssl_certificates()

        url_maps = loadbalancing_conn.list_url_maps()
        backend_services = loadbalancing_conn.list_backend_services()
        backend_buckets = loadbalancing_conn.list_backend_buckets()

        # Health Checks
        legacy_health_checks = []
        health_checks = loadbalancing_conn.list_health_checks()

        http_health_checks = loadbalancing_conn.list_http_health_checks()
        legacy_health_checks.extend(http_health_checks)

        https_health_checks = loadbalancing_conn.list_https_health_checks()
        legacy_health_checks.extend(https_health_checks)

        target_pools = loadbalancing_conn.list_target_pools()

        # Extract loadbalancer information from related resources(Target Proxy, Forwarding Rule)
        # Google Cloud Service Does not provider single object of loadbalancer
        target_pool_based_load_balancers = self._get_loadbalancer_from_forwarding_rule(
            forwarding_rules
        )
        load_balancers.extend(target_pool_based_load_balancers)

        for load_balancer in load_balancers:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                lb_forwarding_rules = self._get_forwarding_rules(
                    load_balancer, forwarding_rules
                )
                lb_target_proxy = self._get_target_proxy(load_balancer)
                lb_certificates = self._get_certificates(
                    lb_target_proxy, ssl_certificates
                )
                lb_urlmap = self._get_urlmap(load_balancer, url_maps)
                lb_backend_services = self._get_backend_services(
                    lb_urlmap, backend_services
                )
                lb_health_checks = self._get_health_checks(
                    lb_backend_services, health_checks
                )
                lb_legacy_health_checks = self._get_legacy_health_checks(
                    lb_backend_services, legacy_health_checks
                )
                lb_bucket_services = self._get_bucket_services(
                    lb_urlmap, backend_buckets
                )
                lb_target_pools = self._get_target_pools(
                    lb_forwarding_rules, target_pools
                )

                ##################################
                # 2. Make Base Data
                ##################################

                loadbalancer_data = LoadBalancing(
                    {
                        "id": load_balancer.get("id", ""),
                        "name": self._get_name(load_balancer),
                        "description": load_balancer.get("description", ""),
                        "project": self._get_project_name(load_balancer),
                        "region": self.get_region(load_balancer),
                        "internal_or_external": self._get_external_internal(
                            lb_forwarding_rules
                        ),
                        "type": self._get_loadbalancer_type(load_balancer),
                        "protocol": self._get_loadbalancer_protocol(load_balancer),
                        "self_link": load_balancer.get("selfLink", ""),
                        "forwarding_rules": lb_forwarding_rules,
                        "target_proxy": lb_target_proxy,
                        "urlmap": lb_urlmap,
                        "certificates": lb_certificates,
                        "backend_services": lb_backend_services,
                        "backend_buckets": lb_bucket_services,
                        "heath_checks": lb_health_checks,
                        "legacy_health_checks": lb_legacy_health_checks,
                        "target_pools": lb_target_pools,
                        "tags": [],
                        "creation_timestamp": self._get_creation_timestamp(
                            load_balancer, lb_forwarding_rules, lb_backend_services, lb_urlmap
                        ),
                    },
                    strict=False,
                )

                ##################################
                # 3. Make Return Resource
                ##################################
                loadbalancer_resource = LoadBalancingResource(
                    {
                        "name": loadbalancer_data.get("name", ""),
                        "account": project_id,
                        "region_code": loadbalancer_data.get("region", ""),
                        "data": loadbalancer_data,
                        "reference": ReferenceModel(
                            loadbalancer_data.reference()
                        ),
                    }
                )

                ##################################
                # 4. Make Collected Region Code
                ##################################
                self.set_region_code(loadbalancer_data.get("region", ""))

                ##################################
                # 5. Make Resource Response Object
                # List of LoadBalancingResponse Object
                ##################################
                collected_cloud_services.append(
                    LoadBalancingResponse({"resource": loadbalancer_resource})
                )
            except Exception as e:
                _LOGGER.error(f"[collect_cloud_service] => {e}", exc_info=True)
                error_response = self.generate_resource_error_response(
                    e, "NetworkService", "LoadBalancing", lb_id
                )
                error_responses.append(error_response)

        _LOGGER.debug(
            f"** Load Balancing Finished {time.time() - start_time} Seconds **"
        )
        return collected_cloud_services, error_responses

    def _get_loadbalancer_from_forwarding_rule(self, forwarding_rules) -> list:
        loadbalancers = []
        for fr in forwarding_rules:
            if self._check_forwarding_rule_is_loadbalancer(fr):
                loadbalancers.append(fr)

        return loadbalancers

    def _check_forwarding_rule_is_loadbalancer(self, forwarding_rule) -> bool:
        target = forwarding_rule.get("target", "")
        if self.get_param_in_url(target, "targetPools") != "":
            return True
        else:
            return False

    # Get loadbalancer name from related services
    def _get_name(self, loadbalancer) -> str:
        # Loadbalancer name can be extracted by resource type
        # Google cloud does not support one single loadbalancer
        if loadbalancer.get("kind") == "compute#targetHttpProxy":
            return self.get_param_in_url(loadbalancer.get("urlMap", ""), "urlMaps")
        elif loadbalancer.get("kind") == "compute#targetHttpsProxy":
            return self.get_param_in_url(loadbalancer.get("urlMap", ""), "urlMaps")
        elif loadbalancer.get("kind") == "compute#targetSslProxy":
            return self.get_param_in_url(
                loadbalancer.get("service", ""), "backendServices"
            )
        elif loadbalancer.get("kind") == "compute#targetTcpProxy":
            return self.get_param_in_url(
                loadbalancer.get("service", ""), "backendServices"
            )
        elif loadbalancer.get("kind") == "compute#forwardingRule":
            return self.get_param_in_url(loadbalancer.get("target", ""), "targetPools")
        else:
            return ""

    def _get_project_name(self, loadbalancer) -> str:
        url_self_link = loadbalancer.get("selfLink", "")
        project_name = self.get_param_in_url(url_self_link, "projects")
        return project_name

    def _get_target_proxy(self, load_balancer) -> dict:
        """
        Loadbalancer type is two case
        1. proxy type(grpc, http, https, tcp, udp)
        2. forwarding rule(target pool based)
        Remove forwarding rule case
        """
        if load_balancer.get("kind", "") == "compute#forwardingRule":
            target_proxy = {}
        else:
            target_proxy = {
                "name": load_balancer.get("name", ""),
                "description": load_balancer.get("description", ""),
            }
            target_proxy.update(
                self._get_target_proxy_type(
                    load_balancer.get("kind", ""), load_balancer
                )
            )

        return target_proxy

    @staticmethod
    def _get_target_proxy_type(kind, target_proxy) -> dict:
        # Proxy service is managed by type(protocol)
        if kind == "compute#targetGRPCProxy":
            proxy_type = {"type": "GRPC", "grpc_proxy": target_proxy}
        elif kind == "compute#targetHttpProxy":
            proxy_type = {"type": "HTTP", "http_proxy": target_proxy}
        elif kind == "compute#targetHttpsProxy":
            proxy_type = {"type": "HTTPS", "https_proxy": target_proxy}
        elif kind == "compute#targetSslProxy":
            proxy_type = {"type": "SSL", "ssl_proxy": target_proxy}
        elif kind == "compute#targetTcpProxy":
            proxy_type = {"type": "TCP", "tcp_proxy": target_proxy}
        else:
            proxy_type = {}
        return proxy_type

    @staticmethod
    def _get_certificates(lb_target_proxy, ssl_certificates) -> list:
        """
        Get related certificated to target proxy(LoadBalancer)
        """
        matched_certificates = []
        for cert in ssl_certificates:
            if cert.get("selfLink", "") in lb_target_proxy.get("sslCertificates", []):
                matched_certificates.append(cert)
        return matched_certificates

    @staticmethod
    def _get_urlmap(load_balancer, url_maps):
        """
        Get relatred urlmaps to loadbalancer
        """
        matched_urlmap = {}
        for map in url_maps:
            if map.get("selfLink") == load_balancer.get("urlMap", ""):
                matched_urlmap = map

        return matched_urlmap

    @staticmethod
    def _get_backend_services(lb_urlmap, backend_services):
        """
        Get related backend services from urlmap
        """
        matched_backend_services = []
        for svc in backend_services:
            if lb_urlmap.get("defaultService", "") == svc.get("selfLink"):
                matched_backend_services.append(svc)

        return matched_backend_services

    @staticmethod
    def _get_health_checks(lb_backend_services, health_checks):
        """
        Get related health checks from backend_services
        """
        matched_health_checks = []
        for svc in lb_backend_services:
            for check in health_checks:
                if check.get("selfLink") in svc.get("healthChecks", []):
                    matched_health_checks.append(check)

        return matched_health_checks

    @staticmethod
    def _get_legacy_health_checks(lb_backend_services, legacy_health_checks):
        """
        Get related legacy health checks from backend_services
        """
        matched_legacy_health_checks = []
        for svc in lb_backend_services:
            for check in legacy_health_checks:
                if check.get("selfLink") in svc.get("healthChecks", []):
                    matched_legacy_health_checks.append(check)

        return matched_legacy_health_checks

    @staticmethod
    def _get_bucket_services(lb_urlmap, backend_buckets):
        """
        Get related bucket backend from urlmaps
        """
        matched_bucket_service = []
        for backend in backend_buckets:
            if backend.get("selfLink") in lb_urlmap.get("defaultService", ""):
                matched_bucket_service.append(backend)

        return matched_bucket_service

    @staticmethod
    def _get_target_pools(lb_forwarding_rules, target_pools):
        """
        Get related target pool from forwarding rules
        """
        matched_target_pools = []
        for rule in lb_forwarding_rules:
            for pool in target_pools:
                if rule.get("target", "") == pool.get("selfLink"):
                    matched_target_pools.append(pool)

        return matched_target_pools

    @staticmethod
    def _get_forwarding_rules(loadbalancer, forwarding_rules):
        matched_forwarding_rules = []
        """
        1. LoadBalancer is target of forwarding rule
        2. LoadBalancer is same as forwarding rules(Target Pool Based)
        """
        for rule in forwarding_rules:
            if loadbalancer.get("selfLink") == rule.get("target", ""):
                matched_forwarding_rules.append(rule)
            if loadbalancer.get("selfLink") == rule.get("selfLink", ""):
                matched_forwarding_rules.append(rule)

        return matched_forwarding_rules

    @staticmethod
    def _get_external_internal(forwarding_rules) -> str:
        external_or_internal = "UnKnown"
        if len(forwarding_rules) > 0:
            external_or_internal = forwarding_rules[0].get("loadBalancingScheme")

        return external_or_internal

    @staticmethod
    def _get_loadbalancer_type(load_balancer):
        """
        - load_balancer kind is six type
            compute#forwardingRule
            compute#targetHttpProxy
            compute#targetHttpsProxy
            compute#targetSslProxy
            compute#targetTcpProxy
            compute#targetGrpcProxy
        """
        lb_type = "UnKnown"
        if load_balancer.get("kind") == "compute#forwardingRule":
            # kind: compute#forwardingRule loadbalancer pass traffic to backend service directly.
            lb_type = "TCP/UDP Network LoadBalancer"
        elif load_balancer.get("kind") in [
            "compute#targetHttpsProxy",
            "compute#targetHttpProxy",
            "compute#targetGrpcProxy",
        ]:
            lb_type = "HTTP(S) LoadBalancer"
        elif load_balancer.get("kind") in ["compute#targetTcpProxy"]:
            lb_type = "TCP Proxy LoadBalancer"
        elif load_balancer.get("kind") in ["compute#targetSslProxy"]:
            lb_type = "SSL Proxy LoadBalancer"

        return lb_type

    @staticmethod
    def _get_loadbalancer_protocol(load_balancer):
        lb_protocol = "UnKnown"

        if load_balancer.get("kind") == "compute#forwardingRule":
            # IPProtocol can be TCP, UDP, ESP, AH, SCTP, ICMP and L3_DEFAULT
            lb_protocol = load_balancer.get("IPProtocol", "")
        elif load_balancer.get("kind") in [
            "compute#targetHttpProxy",
            "compute#targetGrpcProxy",
        ]:
            lb_protocol = "HTTP"
        elif load_balancer.get("kind") in ["compute#targetHttpsProxy"]:
            lb_protocol = "HTTPS"
        elif load_balancer.get("kind") in ["compute#targetTcpProxy"]:
            lb_protocol = "TCP"
        elif load_balancer.get("kind") in ["compute#targetSslProxy"]:
            lb_protocol = "SSL"

        return lb_protocol

    @staticmethod
    def _get_creation_timestamp(load_balancer, forwarding_rules, backend_services, urlmap):
        """
        LoadBalancer의 creation_timestamp를 결정합니다.
        우선순위: 1) load_balancer 자체 2) urlmap 3) forwarding_rules 4) backend_services
        """
        # 1. Load Balancer 자체에 creation_timestamp가 있으면 사용
        lb_timestamp = load_balancer.get("creationTimestamp") or load_balancer.get("creation_timestamp")
        if lb_timestamp:
            return lb_timestamp
        
        # 2. UrlMap의 creation_timestamp 사용
        if urlmap and urlmap.get("creation_timestamp"):
            return urlmap.get("creation_timestamp")
        
        # 3. Forwarding Rules 중 가장 이른 timestamp 사용
        if forwarding_rules:
            timestamps = []
            for rule in forwarding_rules:
                timestamp = rule.get("creation_timestamp")
                if timestamp:
                    timestamps.append(timestamp)
            if timestamps:
                return min(timestamps)  # 가장 이른 시간 반환
        
        # 4. Backend Services 중 가장 이른 timestamp 사용
        if backend_services:
            timestamps = []
            for service in backend_services:
                timestamp = service.get("creation_timestamp")
                if timestamp:
                    timestamps.append(timestamp)
            if timestamps:
                return min(timestamps)  # 가장 이른 시간 반환
        
        # 모든 구성 요소에 timestamp가 없으면 None 반환
        return None
