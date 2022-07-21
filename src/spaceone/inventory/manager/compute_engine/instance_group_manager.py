import time
import logging

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.connector.compute_engine.instance_group import InstanceGroupConnector
from spaceone.inventory.model.compute_engine.instance_group.cloud_service_type import CLOUD_SERVICE_TYPES
from spaceone.inventory.model.compute_engine.instance_group.cloud_service import InstanceGroupResource, \
    InstanceGroupResponse
from spaceone.inventory.model.compute_engine.instance_group.data import InstanceGroupManagers, AutoScaler, \
    InstanceTemplate, InstanceGroup

_LOGGER = logging.getLogger(__name__)


class InstanceGroupManager(GoogleCloudManager):
    connector_name = 'InstanceGroupConnector'
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug(f'** Instance Group START **')
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
            CloudServiceResponse
        """
        collected_cloud_services = []
        error_responses = []
        instance_group_id = ""

        secret_data = params['secret_data']
        project_id = secret_data['project_id']
        instance_group_conn: InstanceGroupConnector = self.locator.get_connector(self.connector_name, **params)

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        instance_groups = instance_group_conn.list_instance_groups()
        instance_group_managers = instance_group_conn.list_instance_group_managers()
        autoscalers = instance_group_conn.list_autoscalers()
        instance_templates = instance_group_conn.list_instance_templates()

        for instance_group in instance_groups:
            try:

                ##################################
                # 1. Set Basic Information
                ##################################
                instance_group_id = instance_group.get('id')

                instance_group.update({
                    'project': secret_data['project_id']
                })

                scheduler = {'type': 'zone'} if 'zone' in instance_group else {'type': 'region'}

                if match_instance_group_manager := \
                        self.match_instance_group_manager(instance_group_managers, instance_group.get('selfLink')):

                    instance_group_type = self._get_instance_group_type(match_instance_group_manager)
                    scheduler.update({'instance_group_type': instance_group_type})

                    # Managed
                    match_instance_group_manager.update({
                        'statefulPolicy': {
                            'preservedState': {'disks': self._get_stateful_policy(match_instance_group_manager)}}
                    })

                    ##################################
                    # 2. Make Base Data
                    ##################################
                    instance_group.update({
                        'instance_group_type': instance_group_type,
                        'instance_group_manager': InstanceGroupManagers(match_instance_group_manager, strict=False)
                    })

                    if match_autoscaler := self.match_autoscaler(autoscalers, match_instance_group_manager):
                        scheduler.update(
                            self._get_auto_policy_for_scheduler(match_autoscaler)
                        )

                        instance_group.update({
                            'autoscaler': AutoScaler(match_autoscaler, strict=False),
                            'autoscaling_display': self._get_autoscaling_display(
                                match_autoscaler.get('autoscalingPolicy', {}))
                        })

                    match_instance_template = \
                        self.match_instance_template(instance_templates,
                                                     match_instance_group_manager.get('instanceTemplate'))

                    if match_instance_template:
                        instance_group.update({'template': InstanceTemplate(match_instance_template, strict=False)})

                else:
                    # Unmanaged
                    instance_group.update({'instance_group_type': 'UNMANAGED'})
                    scheduler.update({'instance_group_type': 'UNMANAGED'})

                location_type = self._check_instance_group_is_zonal(instance_group)
                location = self._get_location(instance_group)
                region = self.parse_region_from_zone(location) if location_type == 'zone' else location
                instances = instance_group_conn.list_instances(instance_group.get('name'), location, location_type)

                display_loc = {'region': location, 'zone': ''} if location_type == 'region' \
                    else {'region': self.parse_region_from_zone(location), 'zone': location}

                google_cloud_monitoring_filters = [{'key': 'resource.labels.instance_group_name',
                                                    'value': instance_group.get('name')}]

                instance_group.update({
                    'power_scheduler': scheduler,
                    'instances': self.get_instances(instances),
                    'instance_counts': len(instances),
                    'display_location': display_loc,
                    'google_cloud_monitoring': self.set_google_cloud_monitoring(project_id,
                                                                                "compute.googleapis.com/instance_group",
                                                                                instance_group.get('name'),
                                                                                google_cloud_monitoring_filters)
                })
                # No labels
                _name = instance_group.get('name', '')
                instance_group_data = InstanceGroup(instance_group, strict=False)

                ##################################
                # 3. Make Return Resource
                ##################################
                instance_group_resource = InstanceGroupResource({
                    'name': _name,
                    'account': project_id,
                    'region_code': region,
                    'data': instance_group_data,
                    'reference': ReferenceModel(instance_group_data.reference())
                })

                ##################################
                # 4. Make Collected Region Code
                ##################################
                self.set_region_code(region)

                ##################################
                # 5. Make Resource Response Object
                # List of LoadBalancingResponse Object
                ##################################
                collected_cloud_services.append(InstanceGroupResponse({'resource': instance_group_resource}))
            except Exception as e:
                _LOGGER.error(f'[collect_cloud_service] => {e}', exc_info=True)
                error_response = self.generate_resource_error_response(e, 'ComputeEngine', 'InstanceGroup', instance_group_id)
                error_responses.append(error_response)

        _LOGGER.debug(f'** Instance Group Finished {time.time() - start_time} Seconds **')
        return collected_cloud_services, error_responses

    def _get_location(self, instance_group):
        if 'zone' in instance_group:
            url_zone = instance_group.get('zone')
            location = self.get_param_in_url(url_zone, 'zones')
        else:
            # zone or region key must be existed
            url_region = instance_group.get('region')
            location = self.get_param_in_url(url_region, 'regions')

        return location

    def get_instances(self, instances):
        _instances = []
        for instance in instances:
            url_instance = instance.get('instance', '')
            instance.update({'name': self.get_param_in_url(url_instance, 'instances')})
            _instances.append(instance)

        return _instances

    @staticmethod
    def _check_instance_group_is_zonal(instance_group):
        instance_group_type = 'zone' if 'zone' in instance_group else 'region'
        return instance_group_type

    @staticmethod
    def match_instance_template(instance_templates, instance_template_self_link):
        for instance_template in instance_templates:
            if instance_template['selfLink'] == instance_template_self_link:
                return instance_template

        return None

    @staticmethod
    def match_instance_group_manager(instance_group_managers, instance_group_name):
        for instance_group_manager in instance_group_managers:
            if instance_group_manager['instanceGroup'] == instance_group_name:
                return instance_group_manager

        return None

    @staticmethod
    def match_autoscaler(autoscalers, instance_group_manager):
        match_autoscaler_name = instance_group_manager.get('status', {}).get('autoscaler')

        if match_autoscaler_name:
            for autoscaler in autoscalers:
                if match_autoscaler_name == autoscaler['selfLink']:
                    return autoscaler

        return None

    @staticmethod
    def _get_stateful_policy(match_instance_group_manager):
        disks_vos = []
        stateful_policy = match_instance_group_manager.get('statefulPolicy')
        if stateful_policy:
            preserved_state = stateful_policy.get('preservedState')
            if preserved_state:
                for key, val in preserved_state.get('disks', {}).items():
                    disks_vos.append({'key': key, 'value': val})

        return disks_vos

    @staticmethod
    def _get_instance_group_type(instance_group_manager):
        if instance_group_manager.get('status', {}).get('stateful', {}).get('hasStatefulConfig'):
            return 'STATEFUL'
        else:
            return 'STATELESS'

    def _get_autoscaling_display(self, autoscaling_policy):
        display_string = f'{autoscaling_policy.get("mode")}: Target '

        policy_display_list = []

        if 'cpuUtilization' in autoscaling_policy:
            policy_display_list.append(
                f'CPU utilization {(autoscaling_policy.get("cpuUtilization", {}).get("utilizationTarget")) * 100}%')

        if 'loadBalancingUtilization' in autoscaling_policy:
            policy_display_list.append(
                f'LB capacity fraction {(autoscaling_policy.get("loadBalancingUtilization", {}).get("utilizationTarget")) * 100}%')

        for custom_metric in autoscaling_policy.get('customMetricUtilizations', []):
            policy_display_list.append(
                f'{custom_metric.get("metric", "")} {custom_metric.get("utilizationTarget", "")}{self._get_custom_metric_target_type(custom_metric.get("utilizationTargetType"))}')

        if policy_display_list:
            policy_join_str = ', '.join(policy_display_list)
            return f'{display_string}{policy_join_str}'
        else:
            return ''

    @staticmethod
    def _get_custom_metric_target_type(util_target_type):
        if util_target_type == 'GAUGE':
            return ''
        elif util_target_type == 'DELTA_PER_SECOND':
            return '/s'
        elif util_target_type == 'DELTA_PER_MINUTE':
            return '/m'
        else:
            return ''

    @staticmethod
    def _get_auto_policy_for_scheduler(matched_scheduler) -> dict:
        auto_policy = matched_scheduler.get('autoscalingPolicy', {})

        if auto_policy != {}:
            return {
                'recommend_size': matched_scheduler.get('recommendedSize', 1),
                'origin_min_size': auto_policy.get('minNumReplicas'),
                'origin_max_size': auto_policy.get('maxNumReplicas'),
                'mode': auto_policy.get('mode')
            }
        else:
            return {}
