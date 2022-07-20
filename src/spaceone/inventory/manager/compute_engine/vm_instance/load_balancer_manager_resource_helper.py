from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.model.compute_engine.instance.data import LoadBalancer


class LoadBalancerManagerResourceHelper(GoogleCloudManager):
    connector_name = 'VMInstanceConnector'

    def get_loadbalancer_info(self, instance, instance_groups, backend_svc, url_maps, target_pools, forwarding_rules):
        """
        load_balancer_data_list = [{
                "type": 'HTTP'| 'TCP'| 'UDP'
                "name": "",
                "dns": "",
                "scheme": 'EXTERNAL'|'INTERNAL,
                "port": [
                    50051
                ],
                "protocol": [
                    "TCP"
                ],
                 "tags": {},
            },
            ...
        ]
        """
        load_balancer_data_list = []
        matched_groups = self.get_matched_instance_group(instance, instance_groups)
        for matched_group in matched_groups:
            matched_http_backend_svcs = self.get_matched_backend_svc_for_http(matched_group, backend_svc, url_maps)
            matched_lb_infos = matched_http_backend_svcs
            for matched_lb_info in matched_lb_infos:
                lb_info = matched_lb_info.get('lb_info', {})
                protocol = matched_lb_info.get('protocol', '')
                lb_data = {
                    'type': protocol,
                    'name': lb_info.get('name', ''),
                    'dns': '',
                    'scheme': matched_lb_info.get('loadBalancingScheme', ''),
                    'port': [matched_lb_info.get('port', '')] if matched_lb_info.get('port', '') != '' else [],
                    'protocol': [protocol] if protocol != '' else [],
                    'tags': {}
                }

                load_balancer_data_list.append(LoadBalancer(lb_data, strict=False))

        matched_target_pools = self._get_matched_target_pool(instance, target_pools)

        if len(matched_target_pools) > 0:
            lbs_by_fd_rules = self._get_matched_forwarding_rules(matched_target_pools, forwarding_rules)
            for lbs_by_fd_rule in lbs_by_fd_rules:
                lb_info = lbs_by_fd_rule.get('lb_info', {})
                protocol = lbs_by_fd_rule.get('IPProtocol', '')
                lb_data = {
                    'type': protocol,
                    'name': lb_info.get('name', ''),
                    'dns': '',
                    'scheme': lbs_by_fd_rule.get('loadBalancingScheme', ''),
                    'port': self._get_port_ranges_into_array(lbs_by_fd_rule),
                    'protocol': [protocol] if protocol != '' else [],
                    'tags': {}
                }

                load_balancer_data_list.append(LoadBalancer(lb_data, strict=False))

        return load_balancer_data_list

    def get_matched_backend_svc_for_http(self, matched_group, backend_svcs, url_maps):
        matched_backend_svc = []
        instance_group_key = self._get_matching_str('instanceGroup', matched_group)
        for backend_svc in backend_svcs:
            backends = backend_svc.get('backends', [])
            selected_url_map = self._get_lb_name_from_backend_svc(backend_svc.get('selfLink', ''), url_maps)
            if backend_svc.get('protocol', '') in ['HTTP', 'HTTPS'] and selected_url_map is not None:
                for backend in backends:
                    group_name = backend.get('group', '')
                    if instance_group_key in group_name:
                        backend_svc.update({
                            'lb_info': selected_url_map
                        })
                        matched_backend_svc.append(backend_svc)
                        break

        return matched_backend_svc

    @staticmethod
    def get_matched_instance_group(instance, instance_groups):
        matched_instance_group = []
        for instance_group in instance_groups:
            instance_list = instance_group.get('instance_list', [])
            for single_inst in instance_list:
                if instance.get('selfLink', '') == single_inst.get('instance'):
                    matched_instance_group.append(instance_group)
                    break

        return matched_instance_group

    @staticmethod
    def _get_matching_str(key, matching_item):
        matching_string = matching_item.get(key, '')
        return matching_string[matching_string.find('/projects/'):len(matching_string)] \
            if matching_string != '' else None

    @staticmethod
    def _get_lb_name_from_backend_svc(self_link, url_maps):
        selected_url_map = None
        for url_map in url_maps:
            if self_link == url_map.get('defaultService', ''):
                selected_url_map = url_map
                break
        return selected_url_map

    @staticmethod
    def _get_matched_target_pool(instance, target_pools):
        instance_contained_pools = []
        for target_pool in target_pools:
            inst_self_link = instance.get('selfLink', '')
            if any(inst_self_link in s for s in target_pool.get('instances', [])):
                instance_contained_pools.append(target_pool)
        return instance_contained_pools

    @staticmethod
    def _get_matched_forwarding_rules(target_pools, forwarding_ruls):
        matched_forwarding_rule = []
        for target_pool in target_pools:
            self_link = target_pool.get('selfLink', '')
            for forwarding_rule in forwarding_ruls:
                target = forwarding_rule.get('target', '')
                if self_link == target:
                    forwarding_rule.update({
                        'lb_info': target_pool
                    })
                    matched_forwarding_rule.append(forwarding_rule)
        return matched_forwarding_rule

    @staticmethod
    def _get_port_ranges_into_array(lbs_by_fd_rule):
        port_range = lbs_by_fd_rule.get('portRange')
        ports = port_range.split('-') if port_range.find('-') > 0 else int(port_range)
        return list(range(int(ports[0]), int(ports[1])+1)) if isinstance(ports, list) and len(ports) == 2 else [ports]

