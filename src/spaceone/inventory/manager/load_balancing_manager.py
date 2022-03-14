import time
import logging

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.load_balancing.cloud_service import *
from spaceone.inventory.connector.load_balancing import LoadBalancingConnector
from spaceone.inventory.model.load_balancing.cloud_service_type import CLOUD_SERVICE_TYPES

_LOGGER = logging.getLogger(__name__)


class LoadBalancingManager(GoogleCloudManager):
    connector_name = 'LoadBalancingConnector'
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug(f'** Load Balancing START **')
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

        secret_data = params['secret_data']
        project_id = secret_data['project_id']
        load_bal_conn: LoadBalancingConnector = self.locator.get_connector(self.connector_name, **params)

        project_id = secret_data.get('project_id')
        load_balancers = []

        instance_groups = load_bal_conn.list_instance_groups()
        target_pools = load_bal_conn.list_target_pools()
        url_maps = load_bal_conn.list_url_maps()
        forwarding_rules = load_bal_conn.list_forwarding_rules()
        backend_services = load_bal_conn.list_back_end_services()

        backend_buckets = load_bal_conn.list_back_end_buckets()
        ssl_certificates = load_bal_conn.list_ssl_certificates()
        autoscalers = load_bal_conn.list_autoscalers()
        health_checks = load_bal_conn.list_health_checks()

        legacy_health_checks = []
        http_health_checks = load_bal_conn.list_http_health_checks()
        https_health_checks = load_bal_conn.list_https_health_checks()
        legacy_health_checks.extend(http_health_checks)
        legacy_health_checks.extend(https_health_checks)

        # proxies
        grpc_proxies = load_bal_conn.list_grpc_proxies()
        http_proxies = load_bal_conn.list_target_http_proxies()
        https_proxies = load_bal_conn.list_target_https_proxies()
        ssl_proxies = load_bal_conn.list_ssl_proxies()
        tcp_proxies = load_bal_conn.list_tcp_proxies()

        target_proxies, selective_proxies = self.get_all_proxy_list(grpc_proxies,
                                                                    http_proxies,
                                                                    https_proxies,
                                                                    ssl_proxies,
                                                                    tcp_proxies,
                                                                    forwarding_rules)

        lbs_from_proxy = self.get_load_balacer_from_target_proxy(backend_services,
                                                                 selective_proxies,
                                                                 project_id)

        lbs_from_url_map = self.get_load_balancer_from_url_maps(url_maps, backend_services, backend_buckets, project_id)
        lbs_from_target_pool = self.get_load_balancer_from_target_pools(target_pools, project_id)

        load_balancers.extend(lbs_from_proxy)
        load_balancers.extend(lbs_from_url_map)
        load_balancers.extend(lbs_from_target_pool)

        for load_balancer in load_balancers:
            try:
                lb_id = load_balancer.get('id')
                lb_type = load_balancer.get('lb_type')
                health_checks_vo = load_balancer.get('heath_check_vos', {})
                health_self_links = health_checks_vo.get('health_check_self_link_list', [])
                ##################################
                # Set Target Proxies
                ##################################
                if lb_type != 'target_proxy':
                    matched_target_proxies, matched_certificates = self.get_matched_target_proxies(load_balancer,
                                                                                                   target_proxies,
                                                                                                   ssl_certificates)
                    load_balancer.update({'target_proxies': matched_target_proxies,
                                          'certificates': matched_certificates})
                ##################################
                # Set forwarding Rules to Load Balancer
                ##################################
                matched_forwarding_rules = self.get_matched_forwarding_rules(load_balancer, forwarding_rules)
                load_balancer.update({'forwarding_rules': matched_forwarding_rules})

                ##################################
                # Set Health Check to Load Balancer
                ##################################
                if len(health_self_links) > 0:
                    filter_check_list = list(set(health_checks_vo.get('health_check_list', [])))
                    filter_check_self_link_list = list(set(health_checks_vo.get('health_check_self_link_list', [])))
                    matched_health_list = self._get_matched_health_checks(filter_check_self_link_list, health_checks)

                    if len(matched_health_list) == len(filter_check_list):
                        load_balancer['heath_check_vos'].update({
                            'health_check_list': filter_check_list,
                            'health_check_self_link_list': filter_check_self_link_list,
                            'health_checks': matched_health_list
                        })
                    else:
                        matched_health_legacy_list = self._get_matched_health_checks(filter_check_self_link_list,
                                                                                     legacy_health_checks)
                        matched_health_list.extend(matched_health_legacy_list)
                        load_balancer['heath_check_vos'].update({
                            'health_check_list': filter_check_list,
                            'health_check_self_link_list': filter_check_self_link_list,
                            'health_checks': matched_health_list
                        })
                ############################
                # Set Front to Load Balancer
                ############################

                frontends = self.get_front_from_loadbalancer(load_balancer)
                frontend_display = self._get_frontend_display(frontends)
                if len(frontends) > 0:
                    load_balancer.update({'frontends': frontends,
                                          'frontend_display': frontend_display})

                #############################
                # Set Backend to Load Balancer
                #############################
                backend_vo = {}
                if lb_type in ['target_pool']:
                    backend_vo.update({
                        'type': 'target_pool',
                        'target_pool_backend': self.get_backend_from_target_pools(load_balancer, instance_groups)
                    })

                elif lb_type in ['url_map', 'target_proxy']:
                    key = 'proxy_backend' if lb_type == 'target_proxy' else 'url_map_backend'
                    backends = self.get_backend_from_url_map_and_proxy(load_balancer, instance_groups, autoscalers)
                    backend_vo.update({
                        'type': 'proxy' if lb_type == 'target_proxy' else 'url_map',
                        key: backends
                    })

                load_balancer.update({'backends': backend_vo})

                ########################################
                # Set Backend Tab to LoadBalancer
                ########################################
                backends_tab = self._get_backend_tabs(load_balancer)
                load_balancer.update({
                    'backend_tabs': backends_tab
                })

                ########################################
                # Set Backend Display
                ########################################
                backend_display = self._get_backend_display(load_balancer)
                load_balancer.update({
                    'backends_display': backend_display
                })

                '''
                            Get Appropriate Region & Protocols
    
                            Protocols
                            -  1. Frontend's forwarding Maps
                               2. Backend's end protocol
    
                            Region 
                            - backend-svc's backend
    
                '''
                lead_protocol = self._get_lead_protocol(load_balancer)
                region = self._get_proper_region(load_balancer)
                load_balancer.update({
                    'lead_protocol': lead_protocol,
                    'region': region
                })
                refer_link = self._get_refer_link(load_balancer, project_id)
                _name = load_balancer.get('name', '')
                load_balance_data = LoadBalancing(load_balancer, strict=False)

                lb_resource = LoadBalancingResource({
                    'name': _name,
                    'account': project_id,
                    'region_code': region,
                    'data': load_balance_data,
                    'reference': ReferenceModel(load_balance_data.reference(refer_link))
                })

                self.set_region_code(region)
                collected_cloud_services.append(LoadBalancingResponse({'resource': lb_resource}))
            except Exception as e:
                _LOGGER.error(f'[collect_cloud_service] => {e}', exc_info=True)
                error_response = self.generate_resource_error_response(e, 'NetworkService', 'LoadBalancing', lb_id)
                error_responses.append(error_response)

        _LOGGER.debug(f'** Load Balancing Finished {time.time() - start_time} Seconds **')
        return collected_cloud_services, error_responses

    def get_backend_from_target_pools(self, loadbalcnacer, instance_group):
        for pool in loadbalcnacer.get('target_pools', []):
            ratio = pool.get('failover_ratio')

            target_backend = {
                'name': pool.get('name'),
                'region': self._get_matched_last_target('region', pool),
                'session_affinity': pool.get('session_affinity'),
                'health_check': self._get_matched_last_target_in_list(pool.get('health_checks', [])),
                'backup_pool': self._get_matched_last_target('backup_pool', pool) if pool.get('backup_pool') else '',
                'fail_over': 0.0 if ratio is None else float(ratio),
                'fail_over_display': '0.0 %' if ratio is None else f'{str(float(ratio) * 100)} %',
                'backend_instances': self.get_instance_for_back_ends(loadbalcnacer, pool, instance_group)
            }
            return target_backend

    def get_backend_from_url_map_and_proxy(self, loadbalcnacer, instance_group, autoscalers):
        target_backend_list = []
        backend_services = loadbalcnacer.get('backend_services', [])
        backend_buckets = loadbalcnacer.get('backend_buckets', [])

        for service in backend_services:
            selected_port = self.get_selected_port(service.get('healthChecks'), loadbalcnacer.get('heath_check_vos'))
            for backend_service_back in service.get('backends', []):
                balancing_mode = backend_service_back.get('balancingMode')
                balancing_mode_display = self._get_balancing_mode_display(backend_service_back)
                autoscaler_vo = self._get_selected_instance_group(backend_service_back, instance_group, autoscalers)
                target_backend_svc = {
                    'name': service.get('name'),
                    'type': 'Instance group',
                    'instance_name': self._get_matched_last_target('group', backend_service_back),
                    'region': self.get_region_from_group(backend_service_back.get('group', '')),
                    'cloud_cdn': 'enabled' if service.get('enableCdn') else 'disabled',
                    'end_point_protocol': service.get('protocol'),
                    'named_port': service.get('portName'),
                    'timeout': str(service.get('timeoutSec')) + ' seconds',
                    'health_check': self._get_matched_last_target_in_list(service.get('healthChecks', [])),
                    'capacity': float(backend_service_back.get('capacityScaler', 0.0)),
                    'capacity_display': str(float(backend_service_back.get('capacityScaler', 0.0)) * 100) + ' %',
                    'selected_port': selected_port,
                    'balancing_mode': balancing_mode,
                    'balancing_mode_display': balancing_mode_display,
                    'scheme': service.get('loadBalancingScheme')
                }

                if autoscaler_vo is not None:
                    auto_display = self._get_autoscaling_display(autoscaler_vo)
                    target_backend_svc.update({
                        'autoscaling_policy': autoscaler_vo,
                        'autoscaling_display': 'No configuration' if auto_display == '' else auto_display,
                    })
                else:
                    target_backend_svc.update({
                        'autoscaling_display': 'No configuration',
                    })

                target_backend_list.append(target_backend_svc)

        for bucket in backend_buckets:
            region = self._get_matched_last_target('region', bucket) if bucket.get('region') else 'global'

            target_backend_bucket = {
                'name': bucket.get('name'),
                'instance_name': bucket.get('bucketName'),
                'type': 'Backend Bucket',
                'region': region,
                'cloud_cdn': 'enabled' if bucket.get('enableCdn') else 'disabled',
                'custom_response_headers': bucket.get('customResponseHeaders', [])
            }
            target_backend_list.append(target_backend_bucket)

        return target_backend_list

    def get_selected_port(self, health_checks, health_checks_vos):
        selected_port = []
        for hk in health_checks:
            for single_hk in health_checks_vos.get('health_checks', []):
                if hk == single_hk.get('selfLink'):
                    key = self._get_key_name_for_health_check(single_hk)
                    hc_vo = single_hk.get(key, {}).get('port')
                    if key and hc_vo:
                        selected_port.append(hc_vo)
        return selected_port

    def get_region_from_group(self, group_link):
        if '/zones/' in group_link:
            parsed_group = group_link[group_link.find('/zones/') + 7:]
            zone = parsed_group[:parsed_group.find('/')]
            return zone[:-2]
        else:
            return self._extract_region_from_group(group_link)

    def get_instance_for_back_ends(self, lb, pool, instance_groups):
        instance_list = []
        instances = pool.get('instances', [])
        addresses = [d.get('IPAddress') for d in lb.get('forwarding_rules', []) if d.get('IPAddress', '') != '']

        source_link = lb.get('source_link')
        for instance_group in instance_groups:
            if source_link in instance_group.get('targetPools', []):
                instance_list.append({
                    'type': 'Instance Group',
                    'name': instance_group.get('name'),
                    'region': 'global' if instance_group.get('region') is None else self._get_matched_last_target(
                        'region', instance_group),
                    'zone': '',
                    'address': addresses
                })

        for instance in instances:
            zone = self._extract_zone(instance)
            instance_list.append({
                'type': 'Compute VM',
                'name': instance[instance.rfind('/') + 1:],
                'region': zone[:-2],
                'zone': zone,
                'address': addresses
            })

        return instance_list

    def get_all_proxy_list(self, grpc_proxies, http_proxies, https_proxies, ssl_proxies, tcp_proxies, forwarding_rules):
        proxy_list = []
        proxy_list_relate_to_load_balancer = []

        all_resources = [{'type': 'grpc',
                          'source': grpc_proxies},
                         {'type': 'http',
                          'source': http_proxies},
                         {'type': 'https',
                          'source': https_proxies},
                         {'type': 'ssl',
                          'source': ssl_proxies},
                         {'type': 'tcp',
                          'source': tcp_proxies}
                         ]

        for resource in all_resources:
            for proxy in resource.get('source', []):

                proxy_type = resource.get('type')
                proxy_key: str = self._get_proxy_key(resource.get('type'))
                in_used_by, in_used_by_display = self._get_in_used_by_forwarding_rule(proxy, forwarding_rules)

                proxy_vo = {
                    proxy_key: proxy,
                    'proxy_key': proxy_key,
                    'type': proxy_type,
                    'name': proxy.get('name', ''),
                    'description': proxy.get('description', ''),
                    'target_resource': {},
                    'in_used_by': in_used_by,
                    'target_proxy_display': {
                        'name': proxy.get('name', ''),
                        'description': proxy.get('description', ''),
                        'type': f'{proxy_type.upper()} Proxy',
                        'target_resource': self._get_matched_last_target('urlMap', proxy),
                        'in_used_by_display': in_used_by_display,
                        'creation_timestamp': proxy.get('creationTimestamp'),
                    },
                }
                if proxy_type in ['ssl', 'tcp']:
                    proxy_list_relate_to_load_balancer.append(proxy_vo)
                proxy_list.append(proxy_vo)

        return proxy_list, proxy_list_relate_to_load_balancer

    def get_load_balancer_from_url_maps(self, url_maps, backend_services, backend_buckets, project):
        load_balancer_list = []

        for url_map in url_maps:
            region = self._get_matched_last_target('region', url_map) if url_map.get('region') else 'global'
            url_map_single_vo = {}

            identifiers = self._get_matched_services(url_map)
            backend_svc_list = self.get_lb_info_from_selected_items(identifiers, 'selfLink', backend_services)
            health_check_list = self._get_health_checks_from_backend_svc(backend_svc_list)
            backend_bucktet_list = self.get_lb_info_from_selected_items(identifiers, 'selfLink', backend_buckets)
            host_and_path_rules = self.get_matched_host_and_path(url_map)

            url_map_single_vo.update({
                'lb_type': 'url_map',
                'project': project,
                'region': region,
                'id': url_map.get('id'),
                'description': url_map.get('description', ''),
                'name': url_map.get('name'),
                'self_link': self._get_self_link(project, region, url_map.get('name')),
                'identifier': url_map.get('selfLink'),
                'heath_check_vos': {
                    'health_check_list': self._get_matched_last_target_in_list(health_check_list),
                    'health_check_self_link_list': health_check_list,
                },
                'backend_services': backend_svc_list,
                'backend_buckets': backend_bucktet_list,
                'host_and_paths': host_and_path_rules,
                'creation_timestamp': url_map.get('creationTimestamp')
            })

            load_balancer_list.append(url_map_single_vo)

        return load_balancer_list

    def get_load_balancer_from_target_pools(self, target_pools, project):
        load_balancer_list = []

        for target_pool in target_pools:
            region = self._get_matched_last_target('region', target_pool) if target_pool.get('region') else 'global'
            health_checks = target_pool.get('healthChecks', [])
            target_pool.update({
                '_region': region,
                'num_of_instance': len(target_pool.get('instances', [])),
                '_health_checks': self._get_matched_last_target_in_list(health_checks)
            })
            target_pool_vo = {
                'lb_type': 'target_pool',
                'project': project,
                'region': region,
                'description': target_pool.get('description'),
                'id': target_pool.get('id'),
                'name': target_pool.get('name'),
                'heath_check_vos': {
                    'health_check_list': self._get_matched_last_target_in_list(health_checks),
                    'health_check_self_link_list': health_checks,
                },
                'identifier': target_pool.get('selfLink'),
                'self_link': self._get_self_link(project, region, target_pool.get('name')),
                'creation_timestamp': target_pool.get('creationTimestamp'),
                'target_pools': [TargetPools(target_pool, strict=False)]
            }

            load_balancer_list.append(target_pool_vo)

        return load_balancer_list

    def get_load_balacer_from_target_proxy(self, backends, selective_proxies, project):
        backend_proxies = []

        for ssl_tcp_proxy in selective_proxies:
            key = 'tcp_proxy' if 'tcp_proxy' in ssl_tcp_proxy else 'ssl_proxy'
            proxy_info = ssl_tcp_proxy.get(key, {})
            for backend in backends:
                health_checks = backend.get('healthChecks', [])
                if backend.get('selfLink') == proxy_info.get('service', ''):
                    region = self._extract_region_from_proxy(backend.get('selfLink'), project)
                    backend.update({'region': region, 'type': 'Global' if region == 'global' else region})
                    backend_proxy_vo = {
                        'lb_type': 'target_proxy',
                        'project': project,
                        'id': proxy_info.get('id'),
                        'region': region,
                        'name': proxy_info.get('name'),
                        'self_link': self._get_self_link(project, region, proxy_info.get('name')),
                        'heath_check_vos': {
                            'health_check_list': self._get_matched_last_target_in_list(health_checks),
                            'health_check_self_link_list': health_checks,
                        },
                        'identifier': proxy_info.get('selfLink'),
                        'creation_timestamp': proxy_info.get('creationTimestamp'),
                        'target_proxies': [ssl_tcp_proxy],
                        'backend_services': [backend]
                    }



                    backend_proxies.append(backend_proxy_vo)
        return backend_proxies

    def get_matched_forwarding_rules(self, loadbalancer, forwarding_rules):
        matched_forwarding_rules = []
        lb_type = loadbalancer.get('lb_type')

        if lb_type == 'target_pool':
            for forwarding_rule in forwarding_rules:
                if loadbalancer.get('identifier') == forwarding_rule.get('target'):
                    region = forwarding_rule.get('region')
                    r_type = 'Global' if region == 'global' or region is None else 'Regional'
                    if r_type == 'Regional':
                        _region = region[region.rfind('/')+1:]
                        forwarding_rule.update({'region': _region})
                    forwarding_rule.update({'type': r_type})
                    if forwarding_rule.get('portRange', '').find('-') > 0:
                        forwarding_rule.update({'portRange': self._get_port_ranage_from_str(forwarding_rule.get('portRange', ''))})
                    matched_forwarding_rules.append(forwarding_rule)

        elif lb_type in ['url_map', 'target_proxy']:
            self_links = self._get_self_links_from_proxies(loadbalancer.get('target_proxies', []))
            for forwarding_rule in forwarding_rules:
                if forwarding_rule.get('target') in self_links:
                    region = forwarding_rule.get('region')
                    r_type = 'Global' if region == 'global' or region is None else 'Regional'
                    if r_type == 'Regional':
                        _region = region[region.rfind('/')+1:]
                        forwarding_rule.update({'region': _region})
                    forwarding_rule.update({'type': r_type})
                    if forwarding_rule.get('portRange', '').find('-') > 0:
                        forwarding_rule.update({'portRange': self._get_port_ranage_from_str(forwarding_rule.get('portRange', ''))})
                    matched_forwarding_rules.append(forwarding_rule)

        return matched_forwarding_rules

    def get_matched_target_proxies(self, lb, target_proxies, certs):
        matched_target_proxies = []
        matched_certificate = []
        for target_proxy in target_proxies:
            key = target_proxy.get('proxy_key')
            proxy_info = target_proxy.get(key, {})
            if 'urlMap' in proxy_info:
                if proxy_info.get('urlMap') == lb.get('identifier'):
                    if 'sslCertificates' in proxy_info:
                        matching_ones = self._get_matched_certificates(certs, proxy_info.get('sslCertificates', []))
                        for matching_one in matching_ones:
                            key = 'managed' if 'managed' in matching_one else 'selfManaged'
                            ssl_type = 'Customer supplied'
                            if key == 'managed':
                                ssl_type = 'Google managed'
                            elif key == 'selfManaged':
                                ssl_type = 'Customer managed'

                            managed = matching_one.get(key, {})
                            domain_info = managed.get('domainStatus', {})
                            domain_status = self.convert_labels_format(managed.get('domainStatus', {}))

                            domains = [dd for dd in domain_info]
                            matching_one.update({
                                'domains': domains,
                                'type': ssl_type
                            })
                            if domain_status:
                                matching_one['managed'].update({'domain_status': domain_status})
                            matched_certificate.append(matching_one)

                    matched_target_proxies.append(target_proxy)

        return matched_target_proxies, matched_certificate

    def get_matched_host_and_path(self, target_item):

        host_and_path_rules = []

        if 'defaultService' in target_item:
            host_and_path_rules.append({
                'host': ['All unmatched (default)'],
                'path': ['All unmatched (default)'],
                'backend': self._get_matched_last_target('defaultService', target_item)
            })

        if 'hostRules' in target_item:
            host_rule_map = {}
            for host_rule in target_item.get('hostRules', []):
                host_rule_map[host_rule.get('pathMatcher')] = {'host': host_rule.get('hosts', [])}

            for path_matcher in target_item.get('pathMatchers', []):
                _name = path_matcher.get('name', '')
                default_service = path_matcher.get('defaultService')
                if default_service:
                    host_and_path_rules.append({
                        'host': host_rule_map.get(_name, {}).get('host'),
                        'path': ['/*'],
                        'backend': self._get_matched_last_target('defaultService', target_item)
                    })

                for path_rule in path_matcher.get('pathRules', []):
                    host_and_path_rules.append({
                        'host': host_rule_map.get(_name, {}).get('host'),
                        'path': path_rule.get('paths', []),
                        'backend': self._get_matched_last_target('service', path_rule)
                    })

        return host_and_path_rules

    def get_front_from_loadbalancer(self, loadbalancer):
        frontends = []

        proxies = loadbalancer.get('target_proxies', [])
        pools = loadbalancer.get('target_pools', [])

        for forwarding_rule in loadbalancer.get('forwarding_rules', []):

            target = forwarding_rule.get('target', '')
            ports = forwarding_rule.get('ports', [])
            region = 'global' if forwarding_rule.get('region') is None else forwarding_rule.get('region')
            _region = region[region.rfind('/') + 1:]

            if not proxies:
                for pool in pools:
                    if target == pool.get('self_link'):
                        front_single = {
                            'name': forwarding_rule.get('name'),
                            'protocols': forwarding_rule.get('IPProtocol').upper(),
                            'scope': 'Global' if region == 'global' else f'Regional ({_region})',
                            'region': _region,
                            'ip_address': forwarding_rule.get('IPAddress'),
                            'port': self._get_list_from_str(
                                forwarding_rule.get('portRange')) if not ports else self._get_list_from_str(ports),
                            'network_tier': forwarding_rule.get('networkTier').capitalize()
                        }
                        frontends.append(front_single)
            else:
                for proxy in proxies:
                    key = proxy.get('proxy_key', '')
                    proxy_vo = proxy.get(key)
                    if target == proxy_vo.get('selfLink'):
                        front_single = {
                            'name': forwarding_rule.get('name'),
                            'protocols': proxy.get('type').upper(),
                            'scope': 'Global' if region == 'global' else f'Regional ({_region})',
                            'region': _region,
                            'ip_address': forwarding_rule.get('IPAddress'),
                            'port': self._get_list_from_str(
                                forwarding_rule.get('portRange')) if not ports else self._get_list_from_str(ports),
                            'network_tier': forwarding_rule.get('networkTier').capitalize()
                        }

                        if 'sslCertificates' in proxy_vo:
                            front_single.update(
                                {'certificate': self._get_matched_last_target_in_list(proxy_vo.get('sslCertificates'))})

                        frontends.append(front_single)
        return frontends

    @staticmethod
    def _get_frontend_display(frontend):
        frontend_display = ''
        rule_length = len(frontend)

        if rule_length > 0:
            regions = list(set([ft.get('region') for ft in frontend if 'region' in ft]))
            located_at = regions[0] if len(regions) == 1 else 'Multi regions' if len(regions) > 1 else ''
            _located_at = f'within {located_at}' if located_at != '' else ''
            plural = '' if rule_length == 1 else 's'
            frontend_display = f'{rule_length} Forwarding Rule{plural} {_located_at}'

        return frontend_display

    @staticmethod
    def _get_refer_link(lb, project):
        base = 'https://console.cloud.google.com/net-services/loadbalancing/details'
        lb_type = lb.get('lb_type')
        name = lb.get('name')
        region = lb.get('region')
        if lb_type == 'url_map':
            return base + f'/http/{name}?project={project}'
        elif lb_type == 'target_pool':
            return base + f'/network/{region}/{name}?project={project}'
        else:
            return base + f'/proxy/{name}?project={project}'

    @staticmethod
    def _get_proper_region(lb):
        lb_type = lb.get('lb_type')
        proper_region = ''
        if lb_type == 'url_map':
            backends = lb.get('backends', {})
            _type = backends.get('type')
            _backends = backends.get(f'{_type}_backend', [])
            prop = [backend.get('region') for backend in _backends if backend.get('region', '') != 'global']
            _prop = list(set(prop))
            proper_region = 'global' if not _prop else _prop[0]
        elif lb_type == 'target_pool':
            proper_region = lb.get('region')
        else:
            proper_region = lb.get('region')
        return proper_region

    @staticmethod
    def _get_lead_protocol(load_balancer):
        lead_protocol = ''
        all_protocols = [d.get('protocols') for d in load_balancer.get('frontends', []) if 'protocols' in d]

        if len(all_protocols) > 0:
            lead_protocol = 'HTTP(S)' if 'HTTPS' in all_protocols and 'HTTP' in all_protocols else all_protocols[0]
        else:
            all_protocols = [d.get('type').upper() for d in load_balancer.get('target_proxies', []) if 'type' in d]
            lead_protocol = f'{all_protocols[0]} (Proxy)' if len(all_protocols) > 0 else 'TCP/UDP'

        return lead_protocol

    @staticmethod
    def _get_backend_tabs(load_balancers):
        backends_tab_list = []
        backends = load_balancers.get('backends', {})
        backends_type = backends.get('type')
        object_key = f'{backends_type}_backend'

        if backends_type in ['proxy', 'url_map']:
            for back_end in backends.get(object_key, []):
                _region = back_end.get('region')
                backends_tab_list.append({
                    'name': back_end.get('name'),
                    'type': 'Backend Bucket' if back_end.get('type') == 'Backend Bucket' else 'Backend service',
                    'scope': 'Global' if _region == 'global' else f'Regional ({_region})',
                    'protocol': back_end.get('end_point_protocol', ''),
                })
        else:
            back_end = backends.get(object_key, {})
            _region = back_end.get('region')
            protocol = back_end.get('end_point_protocol', '')
            backends_tab_list.append({
                'name': back_end.get('name'),
                'type': 'Backend Bucket' if back_end.get('type') == 'Backend Bucket' else 'Backend service',
                'scope': 'Global' if _region == 'global' else f'Regional ({_region})',
                'protocol': '',
            })

        return backends_tab_list

    @staticmethod
    def _get_backend_display(load_balancer):
        lb_type = load_balancer.get('lb_type')
        display = ''

        if lb_type == 'target_pool':
            _pools = len(load_balancer.get('target_pools', []))
            pools = load_balancer.get('target_pools', [])
            num_of_instance = 0

            for pool in pools:
                num_of_instance = num_of_instance + len(pool.get('instances', []))

            pool_plural = '(s)' if _pools > 1 else ''
            num_plural = 's' if num_of_instance > 1 else ''

            display = f'{_pools} Target pool{pool_plural}' if num_of_instance == 0 else \
                f'{_pools} Target pool{pool_plural} ({num_of_instance} Instance{num_plural})'
        else:
            service = len(load_balancer.get('backend_services', []))
            bucket = len(load_balancer.get('backend_buckets', []))
            display = f'{service} Backend Services & {bucket} Backend Buckets' if service > 0 and bucket > 0 \
                else f'{bucket} Backend Buckets' if bucket > 0 else f'{service} Backend Service'

        return display

    @staticmethod
    def _extract_zone(self_link):
        p_len = len('/zones/')
        p_key = '/zones/'
        _zone = self_link[self_link.find(p_key) + p_len:]
        return _zone[:_zone.find('/')]

    @staticmethod
    def _get_matched_certificates(certs, ssl_certificates):
        certificates = []
        for cert in certs:
            if cert.get('selfLink', '') in ssl_certificates:
                certificates.append(cert)
        return certificates

    @staticmethod
    def _get_matched_services(target_item):
        matching_item_self_links = []
        if 'defaultService' in target_item:
            matching_item_self_links.append(target_item.get('defaultService'))

        if 'pathMatchers' in target_item and isinstance(target_item.get('pathMatchers'), list):
            for path_matcher in target_item.get('pathMatchers'):
                if path_matcher.get('defaultService', '') not in matching_item_self_links:
                    matching_item_self_links.append(path_matcher.get('defaultService', ''))

                if 'pathRules' in path_matcher and isinstance(path_matcher.get('pathRules'), list):
                    for rule in path_matcher.get('pathRules'):
                        if rule.get('service') not in matching_item_self_links:
                            matching_item_self_links.append(rule.get('service'))

        return matching_item_self_links

    @staticmethod
    def _get_self_links_from_proxies(target_proxies):
        self_link_list = []
        for proxy in target_proxies:
            key = proxy.get('proxy_key')
            self_link = proxy.get(key, {}).get('selfLink')
            if self_link:
                self_link_list.append(self_link)
        return self_link_list

    @staticmethod
    def _get_matched_last_target(key, source):
        a = source.get(key, '')
        return a[a.rfind('/') + 1:]

    @staticmethod
    def _get_matched_last_target_in_list(target_list):
        matched_links_vos = []
        for target_item in target_list:
            a = target_item
            matched_links_vos.append(a[a.rfind('/') + 1:])
        return matched_links_vos

    @staticmethod
    def _get_self_link(project, region, name):
        return f'https://www.googleapis.com/compute/v1/projects/{project}/regions/{region}/load_balancing/{name}'

    @staticmethod
    def _get_zone_from_target(key, source):
        a = source.get(key, '')
        return a[a.find('zones') + 6:a.find('/instances')]

    @staticmethod
    def _get_list_from_str(target_str):
        switching_target = None
        if isinstance(target_str, int):
            switching_target = target_str
        else:
            port_range = target_str.split('-')
            switching_target = port_range[0] if len(port_range) > 1 and port_range[0] == port_range[1] else target_str
        return switching_target if isinstance(switching_target, list) else [switching_target]

    @staticmethod
    def _get_port_ranage_from_str(target_str):
            port_range = target_str.split('-')
            switching_target = port_range[0] if len(port_range) > 1 and port_range[0] == port_range[1] else target_str
            return switching_target

    @staticmethod
    def _get_in_used_by_forwarding_rule(target_proxy, forwarding_rules):
        in_used_by = []
        in_used_by_display = []
        for forwarding_rule in forwarding_rules:
            if forwarding_rule.get('target') == target_proxy.get('selfLink'):
                in_used_by.append({
                    'id': forwarding_rule.get('id', ''),
                    'name': forwarding_rule.get('name', ''),
                    'self_link': forwarding_rule.get('selfLink', ''),
                })

                in_used_by_display.append(forwarding_rule.get('name', ''))

        return in_used_by, in_used_by_display

    @staticmethod
    def _get_matching_target_proxy(loadbalancer, all_proxies):
        target_proxies = []

        for proxy in all_proxies:
            proxy_key: str = 'grpc_proxy' if 'grpc_proxy' in proxy \
                else 'http_proxy' if 'http_proxy' in proxy else 'https_proxy'
            selected_px = proxy.get(proxy_key, {}).get('url_map', '')
            if selected_px == loadbalancer.get('identifier', ''):
                proxy['target_resource'].update({
                    'id': loadbalancer.get('id'),
                    'name': loadbalancer.get('name'),
                    'self_link': loadbalancer.get('identifier')
                })
                target_proxies.append(proxy)
        return target_proxies

    @staticmethod
    def _extract_region_from_proxy(self_link, project):
        p_len = len(project) + 1
        p_key = f'{project}/'
        _region = self_link[self_link.find(p_key) + p_len:]
        return _region[:_region.find('/')]

    @staticmethod
    def _extract_region_from_group(self_link):
        p_len = 9
        p_key = self_link.find('/regions/')
        if p_key == -1:
            return 'global'
        else:
            _region = self_link[p_key + p_len:]
            return _region[:_region.find('/')]

    @staticmethod
    def _get_proxy_key(proxy_type):
        proxy_key = 'tcp_proxy'
        if proxy_type == 'grpc':
            proxy_key = 'grpc_proxy'
        elif proxy_type == 'http':
            proxy_key = 'http_proxy'
        elif proxy_type == 'https':
            proxy_key = 'https_proxy'
        elif proxy_type == 'ssl':
            proxy_key = 'ssl_proxy'
        return proxy_key

    def get_lb_info_from_selected_items(self, identifier, key, selected_items):
        matched_lb_vo = []
        for selected_item in selected_items:
            if selected_item.get(key, '') in identifier:
                region = self._extract_region_from_group(selected_item.get(key, ''))
                _type = 'Global' if region == 'global' else 'Regional'
                selected_item.update({
                    'region': self._extract_region_from_group(selected_item.get(key, '')),
                    'type': _type
                })
                matched_lb_vo.append(selected_item)
        return matched_lb_vo

    @staticmethod
    def _get_matched_health_checks(self_link_list, health_checks):
        health_check_list = []
        for health_check in health_checks:
            if health_check.get('selfLink', '') in self_link_list:
                health_check_list.append(health_check)
        return health_check_list

    @staticmethod
    def _get_health_checks_from_backend_svc(backend_svcs):
        health_check_list = []
        for backend_svc in backend_svcs:
            if len(backend_svc.get('healthChecks', [])) > 0:
                health_check_list.extend(backend_svc.get('healthChecks'))
        return health_check_list

    @staticmethod
    def _get_autoscaling_display(autoscaling_policy):
        auto_scaling_display = ''

        if 'cpuUtilization' in autoscaling_policy:
            cpu_util = autoscaling_policy.get('cpuUtilization', {})
            target = float(cpu_util.get('utilizationTarget', 0.0)) * 100
            auto_scaling_display = f'On: Target CPU utilization {target} %'

        elif 'loadBalancingUtilization' in autoscaling_policy:
            cpu_util = autoscaling_policy.get('loadBalancingUtilization', {})
            target = float(cpu_util.get('utilizationTarget', 0.0)) * 100
            auto_scaling_display = f'On: Load balancing utilization {target} %'

        elif 'customMetricUtilizations' in autoscaling_policy:
            auto_scaling_display = f'On: custom metrics'

        return auto_scaling_display

    @staticmethod
    def _get_balancing_mode_display(backend):
        display_msg = 'No configuration'
        if 'maxUtilization' in backend:
            rate = float(backend.get('maxUtilization', 0.0)) * 100
            display_msg = f'Max Backend Utilization: {rate} %'

        elif 'maxRate' in backend:
            rate = int(backend.get('maxRate', 0))
            display_msg = f'Max Backend Rate: {rate}'

        elif 'maxRatePerInstance' in backend:
            rate = float(backend.get('maxRatePerInstance', 0.0))
            display_msg = f'Max Backend Rate Per Instance: {rate}'

        elif 'maxRatePerEndpoint' in backend:
            rate = float(backend.get('maxRatePerEndpoint', 0.0))
            display_msg = f'Max Backend Rate Per Endpoint: {rate}'

        elif 'maxConnections' in backend:
            rate = int(backend.get('maxConnections', 0))
            display_msg = f'Max Backend Connection: {rate}'

        elif 'maxConnectionsPerInstance' in backend:
            rate = int(backend.get('maxConnectionsPerInstance', 0))
            display_msg = f'Max Backend Connections Per Instance: {rate}'

        elif 'maxConnectionsPerEndpoint' in backend:
            rate = int(backend.get('maxConnectionsPerEndpoint', 0))
            display_msg = f'Max Backend Connections Per Endpoint: {rate}'

        return display_msg

    @staticmethod
    def _get_selected_instance_group(backend, instance_groups, autoscalers):
        for instance_group in instance_groups:
            if backend.get('group') == instance_group.get('instanceGroup'):
                for autoscaler in autoscalers:
                    if autoscaler.get('target') == instance_group.get('selfLink'):
                        auto_policy = autoscaler.get('autoscalingPolicy', {})
                        return auto_policy

    @staticmethod
    def _get_key_name_for_health_check(hk):
        if 'tcpHealthCheck' in hk:
            return 'tcpHealthCheck'

        elif 'sslHealthCheck' in hk:
            return 'tcpHealthCheck'

        elif 'httpHealthCheck' in hk:
            return 'tcpHealthCheck'

        elif 'httpsHealthCheck' in hk:
            return 'tcpHealthCheck'

        elif 'http2HealthCheck' in hk:
            return 'tcpHealthCheck'

        elif 'grpcHealthCheck' in hk:
            return 'grpcHealthCheck'

        else:
            return None