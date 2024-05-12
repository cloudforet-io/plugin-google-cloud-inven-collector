import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["InstanceGroupConnector"]
_LOGGER = logging.getLogger(__name__)


class InstanceGroupConnector(GoogleCloudConnector):
    google_client_service = "compute"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_instances(self, instance_group, loc, loc_type, **query):
        query.update(
            {"project": self.project_id, "instanceGroup": instance_group, loc_type: loc}
        )

        request = (
            self.client.instanceGroups().listInstances(**query)
            if loc_type == "zone"
            else self.client.regionInstanceGroups().listInstances(**query)
        )
        response = request.execute()

        return response.get("items", [])

    def list_instance_templates(self, **query):
        instance_template_list = []
        query.update({"project": self.project_id})
        request = self.client.instanceTemplates().list(**query)
        while request is not None:
            response = request.execute()
            for template in response.get("items", []):
                instance_template_list.append(template)
            request = self.client.instanceTemplates().list_next(
                previous_request=request, previous_response=response
            )

        return instance_template_list

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
