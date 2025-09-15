import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["VPCSubnetConnector"]
_LOGGER = logging.getLogger(__name__)


class VPCSubnetConnector(GoogleCloudConnector):
    google_client_service = "compute"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_subnetworks(self, **query):
        """VPC Subnet 목록을 조회합니다."""
        subnetworks_list = []
        query = self.generate_query(**query)
        request = self.client.subnetworks().aggregatedList(**query)
        while request is not None:
            response = request.execute()
            for name, _subnetworks_list in response["items"].items():
                if "subnetworks" in _subnetworks_list:
                    subnetworks_list.extend(_subnetworks_list.get("subnetworks"))
            request = self.client.subnetworks().aggregatedList_next(
                previous_request=request, previous_response=response
            )

        return subnetworks_list

    def list_regional_addresses(self, **query):
        """지역별 IP 주소 목록을 조회합니다."""
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

    def list_networks(self, **query):
        """VPC Network 목록을 조회합니다."""
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
