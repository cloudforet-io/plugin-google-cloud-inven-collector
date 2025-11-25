import logging
import os

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["VMInstanceConnector"]
_LOGGER = logging.getLogger(__name__)
INSTANCE_TYPE_FILE = "%s/conf/%s" % (
    os.path.dirname(os.path.abspath(__file__)),
    "instances.json",
)


class VMInstanceConnector(GoogleCloudConnector):
    google_client_service = "compute"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def verify(self, options, secret_data):
        self.get_connect(secret_data)
        return "ACTIVE"

    def get_connect(self, secret_data):
        """
        cred(dict)
            - type: ..
            - project_id: ...
            - token_uri: ...
            - ...
        """
        self.project_id = secret_data.get("project_id")

    def list_regions(self):
        result = self.client.regions().list(project=self.project_id).execute()
        return result.get("items", [])

    def list_zones(self):
        result = self.client.zones().list(project=self.project_id).execute()
        return result.get("items", [])

    def list_instances(self, **query):
        status_filter = {
            "key": "status",
            "values": [
                "PROVISIONING",
                "STAGING",
                "RUNNING",
                "STOPPING",
                "REPAIRING",
                "SUSPENDING",
                "SUSPENDED",
                "TERMINATED",
            ],
        }
        if "filter" in query:
            query.get("filter").append(status_filter)
        else:
            query.update({"filter": [status_filter]})

        query = self.generate_key_query(
            "filter", self._get_filter_to_params(**query), "", is_default=True, **query
        )

        instance_list = []
        query.update({"project": self.project_id})
        request = self.client.instances().aggregatedList(**query)

        while request is not None:
            response = request.execute()
            for key, _instance_list in response["items"].items():
                if "instances" in _instance_list:
                    instance_list.extend(_instance_list.get("instances"))
            request = self.client.instances().aggregatedList_next(
                previous_request=request, previous_response=response
            )
        return instance_list

    def list_machine_types(self, **query):
        machine_type_list = []
        query.update({"project": self.project_id})
        request = self.client.machineTypes().aggregatedList(**query)
        while request is not None:
            response = request.execute()
            for key, machine_type in response["items"].items():
                if "machineTypes" in machine_type:
                    machine_type_list.extend(machine_type.get("machineTypes"))
            request = self.client.machineTypes().aggregatedList_next(
                previous_request=request, previous_response=response
            )

        return machine_type_list

    def list_url_maps(self, **query):
        url_map_list = []
        query.update({"project": self.project_id})
        request = self.client.urlMaps().aggregatedList(**query)

        while request is not None:
            response = request.execute()
            for key, url_scoped_list in response["items"].items():
                if "urlMaps" in url_scoped_list:
                    url_map_list.extend(url_scoped_list.get("urlMaps"))
            request = self.client.urlMaps().aggregatedList_next(
                previous_request=request, previous_response=response
            )

        return url_map_list

    def list_back_end_services(self, **query):
        backend_svc_list = []
        query.update({"project": self.project_id})
        request = self.client.backendServices().aggregatedList(**query)
        while request is not None:
            response = request.execute()
            for key, url_scoped_list in response["items"].items():
                if "backendServices" in url_scoped_list:
                    backend_svc_list.extend(url_scoped_list.get("backendServices"))
            request = self.client.backendServices().aggregatedList_next(
                previous_request=request, previous_response=response
            )

        return backend_svc_list

    def list_disks(self, **query):
        disk_list = []
        query.update({"project": self.project_id})
        request = self.client.disks().aggregatedList(**query)
        while request is not None:
            response = request.execute()
            for key, _disk in response["items"].items():
                if "disks" in _disk:
                    disk_list.extend(_disk.get("disks"))
            request = self.client.disks().aggregatedList_next(
                previous_request=request, previous_response=response
            )

        return disk_list

    def list_autoscalers(self, **query):
        autoscaler_list = []
        query.update({"project": self.project_id})
        request = self.client.autoscalers().aggregatedList(**query)
        while request is not None:
            response = request.execute()
            for key, _autoscaler_list in response["items"].items():
                if "autoscalers" in _autoscaler_list:
                    autoscaler_list.extend(_autoscaler_list.get("autoscalers"))
            request = self.client.autoscalers().aggregatedList_next(
                previous_request=request, previous_response=response
            )

        return autoscaler_list

    def list_firewall(self, **query):
        firewalls_list = []
        query.update({"project": self.project_id})
        request = self.client.firewalls().list(**query)

        while request is not None:
            response = request.execute()
            for backend_bucket in response.get("items", []):
                firewalls_list.append(backend_bucket)
            request = self.client.firewalls().list_next(
                previous_request=request, previous_response=response
            )

        return firewalls_list

    def list_images(self, public_id, **query) -> dict:
        public_images = {}
        public_image_list = [
            {"key": "centos", "value": "centos-cloud"},
            {"key": "coreos", "value": "coreos-cloud"},
            {"key": "debian", "value": "debian-cloud"},
            {"key": "google", "value": "google-containers"},
            {"key": "opensuse", "value": "opensuse-cloud"},
            {"key": "rhel", "value": "rhel-cloud"},
            {"key": "suse", "value": "suse-cloud"},
            {"key": "ubuntu", "value": "ubuntu-os-cloud"},
            {"key": "windows", "value": "windows-cloud"},
            {"key": "custom", "value": public_id},
        ]

        for public_image in public_image_list:
            query.update(
                {
                    "project": public_image.get("value"),
                    "orderBy": "creationTimestamp desc",
                }
            )
            response = self.client.images().list(**query).execute()
            public_images[public_image.get("key")] = response.get("items", [])

        return public_images

    def list_instance_groups(self, **query):
        instance_group_list = []
        query.update({"project": self.project_id})
        request = self.client.instanceGroups().aggregatedList(**query)
        while request is not None:
            response = request.execute()
            for key, _instance_group_list in response["items"].items():
                if "instanceGroups" in _instance_group_list:
                    instance_group_list.extend(
                        _instance_group_list.get("instanceGroups")
                    )
            request = self.client.instanceGroups().aggregatedList_next(
                previous_request=request, previous_response=response
            )

        return instance_group_list

    def get_machine_type(self, zone, machine_type, **query):
        response = {}
        query.update(
            {"project": self.project_id, "zone": zone, "machineType": machine_type}
        )
        response = self.client.machineTypes().get(**query).execute()

        return response

    """
    Query all instance list from managed instance group
    """

    def list_instance_from_instance_groups(
        self, instance_group_name, key, loc, **query
    ):
        query = self.generate_query(**query)
        query.update({key: loc, "instanceGroup": instance_group_name})
        response = []

        request = (
            self.client.instanceGroups().listInstances(**query).execute()
            if key == "zone"
            else self.client.regionInstanceGroups().listInstances(**query).execute()
        )
        response = request.get("items", [])

        return response

    # Queries managed instance groups
    def list_instance_group_managers(self, **query):
        instance_group_manager_list = []
        query.update({"project": self.project_id})
        request = self.client.instanceGroupManagers().aggregatedList(**query)

        while request is not None:
            response = request.execute()
            for key, _instance_group_manager_list in response["items"].items():
                if "instanceGroupManagers" in _instance_group_manager_list:
                    instance_group_manager_list.extend(
                        _instance_group_manager_list.get("instanceGroupManagers")
                    )
            request = self.client.instanceGroupManagers().aggregatedList_next(
                previous_request=request, previous_response=response
            )
        return instance_group_manager_list

    def list_vpcs(self, **query):
        network_list = []
        query.update({"project": self.project_id})
        request = self.client.networks().list(**query)
        while request is not None:
            response = request.execute()
            for network in response.get("items", []):
                network_list.append(network)
            request = self.client.networks().list_next(
                previous_request=request, previous_response=response
            )

        return network_list

    def list_subnetworks(self, **query):
        subnetworks_list = []
        query = self.generate_query(**query)
        request = self.client.subnetworks().aggregatedList(**query)
        while request is not None:
            response = request.execute()
            for name, _sbworks_list in response["items"].items():
                if "subnetworks" in _sbworks_list:
                    subnetworks_list.extend(_sbworks_list.get("subnetworks"))
            request = self.client.addresses().aggregatedList_next(
                previous_request=request, previous_response=response
            )

        return subnetworks_list

    def list_target_pools(self, **query):
        target_pool_list = []
        query.update({"project": self.project_id})
        request = self.client.targetPools().aggregatedList(**query)

        while request is not None:
            response = request.execute()
            for key, pool_scoped_list in response["items"].items():
                if "targetPools" in pool_scoped_list:
                    target_pool_list.extend(pool_scoped_list.get("targetPools"))
            request = self.client.targetPools().aggregatedList_next(
                previous_request=request, previous_response=response
            )

        return target_pool_list

    def list_forwarding_rules(self, **query):
        forwarding_rule_list = []
        query.update({"project": self.project_id})
        request = self.client.forwardingRules().aggregatedList(**query)
        while request is not None:
            response = request.execute()
            for key, forwarding_scoped_list in response["items"].items():
                if "forwardingRules" in forwarding_scoped_list:
                    forwarding_rule_list.extend(
                        forwarding_scoped_list.get("forwardingRules")
                    )
            request = self.client.forwardingRules().aggregatedList_next(
                previous_request=request, previous_response=response
            )
        return forwarding_rule_list

    def get_instance_in_group(self, key, value, instance_group, **query):
        query.update(
            {"project": self.project_id, key: value, "instanceGroup": instance_group}
        )
        response = (
            self.client.instanceGroups().listInstances(**query).execute()
            if key == "zone"
            else self.client.regionInstanceGroups().listInstances(**query).execute()
        )
        # NoneType error occurs sometimes. To prevent them insert default value.
        if response is None:
            _LOGGER.debug("[get_instance_in_group] response is None")
            response = {"items": []}
        else:
            _LOGGER.debug(f"[get_instance_in_group] response => {response}")
        return response

    def _get_filter_to_params(self, **query):
        filtering_list = []
        filters = query.get("filter", None)
        if filters and isinstance(filters, list):
            for single_filter in filters:
                filter_key = single_filter.get("key", "")
                filter_values = single_filter.get("values", [])
                filter_str = self._get_full_filter_string(filter_key, filter_values)
                if filter_str != "":
                    filtering_list.append(filter_str)

            return " AND ".join(filtering_list)

    def generate_query(self, **query):
        query.update(
            {
                "project": self.project_id,
            }
        )
        return query

    def generate_key_query(self, key, value, delete, is_default=False, **query):
        if is_default:
            if delete != "":
                query.pop(delete, None)

            query.update({key: value, "project": self.project_id})

        return query

    @staticmethod
    def get_region(zone):
        index = zone.find("-")
        region = zone[0:index] if index > -1 else ""
        return region

    @staticmethod
    def _get_full_filter_string(filter_key, filter_values):
        filter_string = ""
        if filter_key != "" and filter_values != [] and isinstance(filter_values, list):
            single_filter_list = [f"{filter_key}={x}" for x in filter_values]
            join_string = " OR ".join(single_filter_list)
            filter_string = f"({join_string})"
        elif (
            filter_key != ""
            and filter_values != []
            and not isinstance(filter_values, dict)
        ):
            filter_string = f"({filter_key}={filter_values})"
        return filter_string
