import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["VPCNetworkConnector"]
_LOGGER = logging.getLogger(__name__)


class VPCNetworkConnector(GoogleCloudConnector):
    google_client_service = "compute"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_instance_for_networks(self, **query):
        instance_list = []
        query.update(
            {"project": self.project_id, "includeAllScopes": False, "maxResults": 500}
        )

        request = self.client.instances().aggregatedList(**query)
        while request is not None:
            response = request.execute()
            for name, instances_scoped_list in response["items"].items():
                if "instances" in instances_scoped_list:
                    instance_list.extend(instances_scoped_list.get("instances"))
            request = self.client.instances().aggregatedList_next(
                previous_request=request, previous_response=response
            )

        return instance_list

    def list_forwarding_rule(self, **query):
        forwarding_rule_list = []
        query.update(
            {"project": self.project_id, "includeAllScopes": False, "maxResults": 500}
        )

        request = self.client.forwardingRules().aggregatedList(**query)
        while request is not None:
            response = request.execute()
            for name, forwarding_rules_scoped_list in response["items"].items():
                if "forwardingRules" in forwarding_rules_scoped_list:
                    forwarding_rule_list.extend(
                        forwarding_rules_scoped_list.get("forwardingRules")
                    )
            request = self.client.forwardingRules().aggregatedList_next(
                previous_request=request, previous_response=response
            )

        return forwarding_rule_list

    def list_networks(self, **query):
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

    def list_regional_addresses(self, **query):
        address_list = []
        query = self.generate_query(**query)
        request = self.client.addresses().aggregatedList(**query)
        while request is not None:
            response = request.execute()
            for name, _address_list in response["items"].items():
                if "addresses" in _address_list:
                    address_list.extend(_address_list.get("addresses"))
            request = self.client.addresses().aggregatedList_next(
                previous_request=request, previous_response=response
            )

        return address_list


    def list_routes(self, **query):
        route_list = []
        query.update({"project": self.project_id})
        request = self.client.routes().list(**query)

        while request is not None:
            response = request.execute()
            for route in response.get("items", []):
                route_list.append(route)
            request = self.client.routes().list_next(
                previous_request=request, previous_response=response
            )

        return route_list

    def list_firewall(self, **query):
        firewall_list = []
        query.update({"project": self.project_id})
        request = self.client.firewalls().list(**query)
        while request is not None:
            response = request.execute()
            for fire_wall in response.get("items", []):
                firewall_list.append(fire_wall)
            request = self.client.firewalls().list_next(
                previous_request=request, previous_response=response
            )

        return firewall_list
