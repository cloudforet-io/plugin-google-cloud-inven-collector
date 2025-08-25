import logging
import time

from spaceone.inventory.connector.cloud_build.cloud_build_v1 import (
    CloudBuildV1Connector,
)
from spaceone.inventory.connector.cloud_build.cloud_build_v2 import (
    CloudBuildV2Connector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.cloud_build.trigger.cloud_service import (
    TriggerResource,
    TriggerResponse,
)
from spaceone.inventory.model.cloud_build.trigger.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_build.trigger.data import Trigger

_LOGGER = logging.getLogger(__name__)


class CloudBuildTriggerManager(GoogleCloudManager):
    connector_name = "CloudBuildV1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "CloudBuild"
        self.cloud_service_type = "Trigger"

    def collect_cloud_service(self, params):
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
        _LOGGER.debug(
            f"** [{self.cloud_service_group}] {self.cloud_service_type} START **"
        )

        start_time = time.time()

        collected_cloud_services = []
        error_responses = []

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]
        
        self.cloud_build_v1_connector = CloudBuildV1Connector(**params)
        self.cloud_build_v2_connector = CloudBuildV2Connector(**params)

        # 1. 전역 triggers 조회 (global triggers)
        try:
            triggers = self.cloud_build_v1_connector.list_triggers()
            if triggers:
                _LOGGER.debug(f"Found {len(triggers)} global triggers")
                for trigger in triggers:
                    try:
                        # Trigger location 추출
                        trigger_location = "global"
                        if "location" in trigger:
                            trigger_location = trigger.get("location", "global")
                        
                        cloud_service = self._make_cloud_build_trigger_info(trigger, project_id, trigger_location)
                        collected_cloud_services.append(TriggerResponse({"resource": cloud_service}))
                    except Exception as e:
                        _LOGGER.error(f"Failed to process trigger {trigger.get('id', 'unknown')}: {str(e)}")
                        error_response = self.generate_resource_error_response(e, self.cloud_service_group, "Trigger", trigger.get('id', 'unknown'))
                        error_responses.append(error_response)
        except Exception as e:
            _LOGGER.error(f"Failed to query global triggers: {str(e)}")

        # 2. 각 리전별 triggers 조회 (regional triggers)
        try:
            locations = self.cloud_build_v2_connector.list_locations(f"projects/{project_id}")
            for location in locations:
                location_id = location.get("locationId", "")
                if not location_id:
                    continue
                    
                try:
                    parent = f"projects/{project_id}/locations/{location_id}"
                    regional_triggers = self.cloud_build_v1_connector.list_location_triggers(parent)
                    if regional_triggers:
                        _LOGGER.debug(f"Found {len(regional_triggers)} triggers in {location_id}")
                        for trigger in regional_triggers:
                            try:
                                cloud_service = self._make_cloud_build_trigger_info(trigger, project_id, location_id)
                                collected_cloud_services.append(TriggerResponse({"resource": cloud_service}))
                            except Exception as e:
                                _LOGGER.error(f"Failed to process regional trigger {trigger.get('id', 'unknown')}: {str(e)}")
                                error_response = self.generate_resource_error_response(e, self.cloud_service_group, "Trigger", trigger.get('id', 'unknown'))
                                error_responses.append(error_response)
                except Exception as e:
                    _LOGGER.error(f"Failed to query triggers in location {location_id}: {str(e)}")
        except Exception as e:
            _LOGGER.error(f"Failed to query locations: {str(e)}")

        _LOGGER.debug(
            f"** [{self.cloud_service_group}] {self.cloud_service_type} END ** "
            f"({time.time() - start_time:.2f}s)"
        )

        return collected_cloud_services, error_responses

    def _make_cloud_build_trigger_info(self, trigger: dict, project_id: str, location_id: str) -> TriggerResource:
        """Cloud Build Trigger 정보를 생성합니다."""
        trigger_id = trigger.get("id", "")
        trigger_name = trigger.get("name", trigger_id)
        
        formatted_trigger_data = {
            "id": trigger.get("id"),
            "name": trigger.get("name"),
            "description": trigger.get("description"),
            "tags": trigger.get("tags", []),
            "disabled": trigger.get("disabled", False),
            "substitutions": trigger.get("substitutions", {}),
            "filename": trigger.get("filename"),
            "ignoredFiles": trigger.get("ignoredFiles", []),
            "includedFiles": trigger.get("includedFiles", []),
            "filter": trigger.get("filter"),
            "triggerTemplate": trigger.get("triggerTemplate", {}),
            "github": trigger.get("github", {}),
            "pubsubConfig": trigger.get("pubsubConfig", {}),
            "webhookConfig": trigger.get("webhookConfig", {}),
            "repositoryEventConfig": trigger.get("repositoryEventConfig", {}),
            "build": trigger.get("build", {}),
            "autodetect": trigger.get("autodetect", False),
            "createTime": trigger.get("createTime"),
            "serviceAccount": trigger.get("serviceAccount"),
            "sourceToBuild": trigger.get("sourceToBuild", {}),
            "gitFileSource": trigger.get("gitFileSource", {}),
            "approvalConfig": trigger.get("approvalConfig", {}),
        }
        
        trigger_data = Trigger(formatted_trigger_data, strict=False)
        
        return TriggerResource({
            "name": trigger_name,
            "account": project_id,
            "region_code": location_id,
            "data": trigger_data,
            "reference": ReferenceModel({
                "resource_id": trigger_data.id,
                "external_link": f"https://console.cloud.google.com/cloud-build/triggers/edit/{trigger_data.id}?project={project_id}"
            })
        })
