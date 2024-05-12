import logging

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.model.compute_engine.instance.data import AutoScaler
from spaceone.inventory.connector.compute_engine.vm_instance import VMInstanceConnector

_LOGGER = logging.getLogger(__name__)


class InstanceGroupManagerResourceHelper(GoogleCloudManager):
    connector_name = "VMInstanceConnector"
    instance_conn = None

    def __init__(self, gcp_connector=None, **kwargs):
        super().__init__(**kwargs)
        self.instance_conn: VMInstanceConnector = gcp_connector

    def get_autoscaler_info(
        self, instance, instance_group_managers, autoscalers
    ) -> AutoScaler:
        """
        autoscaler_data = {
            name: '',
            id: '',
            self_link: '',
            'instance_group': {
                'id': '',
                'name': ''
                'self_link': ''
                'instance_template_name': ''
            }
        }
        """
        matched_inst_group = self.get_matched_instance_group(
            instance, instance_group_managers
        )
        autoscaler_data = self._get_autoscaler_data(matched_inst_group, autoscalers)

        if autoscaler_data is not None:
            return AutoScaler(autoscaler_data, strict=False)
        else:
            return None

    def get_matched_instance_group(self, instance, instance_groups):
        matched_instance_group = None
        for instance_group in instance_groups:
            find = False
            instance_list = instance_group.get("instance_list", [])
            for single_inst in instance_list:
                instance_name = self._get_key_name("instance", single_inst)
                if instance.get("name") == instance_name:
                    matched_instance_group = instance_group
                    find = True
                    break
            if find:
                break

        return matched_instance_group

    """
    - lists all instances groups
    - list instances for each instance groups
    """

    def list_managed_instances_in_instance_groups(self) -> list:
        instances = []
        instancegroup_managers = self.instance_conn.list_instance_group_managers()
        for instance_group in instancegroup_managers:
            if "region" in instance_group:
                region_name = self.get_region_from_instance_group(
                    instance_group.get("region", "")
                )
                tmp_instances = self.instance_conn.list_instance_from_instance_groups(
                    instance_group.get("name", ""), "region", region_name
                )
                instances.extend(i.get("instance") for i in tmp_instances)
            else:
                zone_name = self.get_zone_from_instance_group(
                    instance_group.get("zone", "")
                )
                tmp_instances = self.instance_conn.list_instance_from_instance_groups(
                    instance_group.get("name", ""), "zone", zone_name
                )
                instances.extend(i.get("instance") for i in tmp_instances)
        """
        Return value is below(zone)
        ['https://www.googleapis.com/compute/v1/projects/{project_id}}/zones/{zone_name{/instances/{instance_name}', 'https://xxx']
        """
        return instances

    """
    zone expression is => 'zone': 'https://www.googleapis.com/compute/v1/projects/xxxxxx/zones/us-west1-b',
    """

    @staticmethod
    def get_zone_from_instance_group(zone_link) -> str:
        # The last index of splitted information is zone name
        zone_name = zone_link.split("/")[-1]
        return zone_name

    """
    region expression is => 'region': 'https://www.googleapis.com/compute/v1/projects/xxxxxxxx/regions/asia-northeast1',
    """

    @staticmethod
    def get_region_from_instance_group(region_link) -> str:
        # The last index of splitted information is region name
        region_name = region_link.split("/")[-1]
        return region_name

    @staticmethod
    def _get_autoscaler_data(matched_inst_group, autoscalers):
        autoscaler_data = None
        if matched_inst_group is not None:
            for autoscaler in autoscalers:
                autoscaler_self_link = autoscaler.get("selfLink", "")
                matched_status = matched_inst_group.get("status", {})
                if autoscaler_self_link == matched_status.get("autoscaler", ""):
                    autoscaler_data = {
                        "name": autoscaler.get("name", ""),
                        "id": autoscaler.get("id", ""),
                        "self_link": autoscaler.get("selfLink", ""),
                        "instance_group": {
                            "id": matched_inst_group.get("id", ""),
                            "name": matched_inst_group.get("name", ""),
                            "self_link": matched_inst_group.get("selfLink", ""),
                            "instance_template_name": matched_inst_group.get(
                                "instanceTemplate", ""
                            ),
                        },
                    }
                    break
        return autoscaler_data

    @staticmethod
    def _get_key_name(key, self_link_source):
        instance_self_link = self_link_source.get(key, "")
        instance_self_link_split = instance_self_link.split("/")
        return instance_self_link_split[-1]
