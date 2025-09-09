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


class CloudBuildTriggerV1Manager(GoogleCloudManager):
    connector_name = "CloudBuildV1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug("** Cloud Build Trigger START **")
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
        trigger_id = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        cloud_build_v1_conn: CloudBuildV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )
        cloud_build_v2_conn: CloudBuildV2Connector = self.locator.get_connector(
            "CloudBuildV2Connector", **params
        )

        # Get lists that relate with triggers through Google Cloud API
        triggers = cloud_build_v1_conn.list_triggers()

        # Get locations using V2 API
        regional_triggers = []
        parent = f"projects/{project_id}"

        try:
            locations = cloud_build_v2_conn.list_locations(parent)
            _LOGGER.info(f"V2 API: Found {len(locations)} locations for triggers")
        except Exception as e:
            _LOGGER.warning(
                f"V2 API: Failed to get locations, falling back to empty list: {e}"
            )
            locations = []

        for location in locations:
            location_id = location.get("locationId", "")
            if location_id:
                try:
                    parent = f"projects/{project_id}/locations/{location_id}"
                    location_triggers = cloud_build_v1_conn.list_location_triggers(
                        parent
                    )
                    for trigger in location_triggers:
                        trigger["_location"] = location_id
                    regional_triggers.extend(location_triggers)
                except Exception as e:
                    _LOGGER.error(
                        f"Failed to query triggers in location {location_id}: {str(e)}"
                    )
                    continue

        # Combine all triggers
        all_triggers = triggers + regional_triggers
        for trigger in all_triggers:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                trigger_id = trigger.get("id")
                trigger_name = trigger.get("name", trigger_id)
                location_id = trigger.get("_location", "global")
                region = (
                    GoogleCloudManager.parse_region_from_zone(location_id)
                    if location_id != "global"
                    else "global"
                )

                ##################################
                # 2. Make Base Data
                ##################################
                # Convert boolean values to user-friendly strings for display
                autodetect = trigger.get("autodetect", False)
                disabled = trigger.get("disabled", False)

                # Convert autodetect to display string
                if autodetect:
                    autodetect_display = "Auto Detect"
                else:
                    autodetect_display = "Manual Config"

                # Convert disabled to display string
                if disabled:
                    disabled_display = "Disabled"
                else:
                    disabled_display = "Enabled"

                trigger.update(
                    {
                        "project": project_id,
                        "location": location_id,
                        "region": region,
                        "autodetect_display": autodetect_display,
                        "disabled_display": disabled_display,
                    }
                )

                ##################################
                # 3. Make Return Resource
                ##################################
                trigger_data = Trigger(trigger, strict=False)

                trigger_resource = TriggerResource(
                    {
                        "name": trigger_name,
                        "account": project_id,
                        "region_code": location_id,
                        "data": trigger_data,
                        "reference": ReferenceModel(
                            {
                                "resource_id": trigger_data.id,
                                "external_link": f"https://console.cloud.google.com/cloud-build/triggers?project={project_id}",
                            }
                        ),
                    },
                    strict=False,
                )

                collected_cloud_services.append(
                    TriggerResponse({"resource": trigger_resource})
                )

            except Exception as e:
                _LOGGER.error(f"Failed to process trigger {trigger_id}: {str(e)}")
                error_response = self.generate_resource_error_response(
                    e, "CloudBuild", "Trigger", trigger_id
                )
                error_responses.append(error_response)

        _LOGGER.debug(
            f"** Cloud Build Trigger END ** ({time.time() - start_time:.2f}s)"
        )

        return collected_cloud_services, error_responses
