import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ['ExternalIPAddressConnector']
_LOGGER = logging.getLogger(__name__)


class ExternalIPAddressConnector(GoogleCloudConnector):
    google_client_service = 'compute'
    version = 'v1'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_instance_for_networks(self, **query):
        instance_list = []
        query.update({'project': self.project_id, 'includeAllScopes': False, 'maxResults': 500})
        request = self.client.instances().aggregatedList(**query)

        while request is not None:
            response = request.execute()
            for name, instances_scoped_list in response['items'].items():
                if 'instances' in instances_scoped_list:
                    instance_list.extend(instances_scoped_list.get('instances'))
            request = self.client.instances().aggregatedList_next(previous_request=request, previous_response=response)

        return instance_list

    def list_forwarding_rule(self, **query):
        forwarding_rule_list = []
        query.update({'project': self.project_id, 'includeAllScopes': False, 'maxResults': 500})

        request = self.client.forwardingRules().aggregatedList(**query)

        while request is not None:
            response = request.execute()
            for name, forwarding_rules_scoped_list in response['items'].items():
                if 'forwardingRules' in forwarding_rules_scoped_list:
                    forwarding_rule_list.extend(forwarding_rules_scoped_list.get('forwardingRules'))
            request = self.client.forwardingRules().aggregatedList_next(previous_request=request,
                                                                        previous_response=response)

        return forwarding_rule_list

    def list_addresses(self, **query):
        address_list = []
        query = self.generate_query(**query)
        request = self.client.addresses().aggregatedList(**query)
        while request is not None:
            response = request.execute()
            for name, _address_list in response['items'].items():
                if 'addresses' in _address_list:
                    address_list.extend(_address_list.get('addresses'))
            request = self.client.addresses().aggregatedList_next(previous_request=request, previous_response=response)

        return address_list

