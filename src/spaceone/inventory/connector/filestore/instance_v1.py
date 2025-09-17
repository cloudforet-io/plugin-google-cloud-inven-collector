import logging
from typing import Any, Dict, List

from googleapiclient.errors import HttpError

from spaceone.inventory.libs.connector import GoogleCloudConnector

_LOGGER = logging.getLogger(__name__)


class FilestoreInstanceConnector(GoogleCloudConnector):
    google_client_service = "file"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_instances(self, **query) -> List[Dict[str, Any]]:
        try:
            # https://cloud.google.com/filestore/docs/reference/rest/v1/projects.locations.instances/list
            # "To retrieve instance information for all locations,
            # use "-" for the {location} value."
            instances = []

            request = (
                self.client.projects()
                .locations()
                .instances()
                .list(
                    parent=f"projects/{self.project_id}/locations/-",
                    **query,
                )
            )

            while request is not None:
                response = request.execute()

                if "instances" in response:
                    for instance in response["instances"]:
                        # projects/my-project/locations/us-central1/
                        # instances/my-instance
                        location = self._extract_location_from_instance_name(
                            instance.get("name", "")
                        )
                        instance["location"] = location
                        instances.append(instance)

                # 다음 페이지가 있는지 확인
                request = (
                    self.client.projects()
                    .locations()
                    .instances()
                    .list_next(previous_request=request, previous_response=response)
                )

            return instances

        except HttpError as e:
            if e.resp.status == 404:
                _LOGGER.warning(
                    f"Filestore service not available for project {self.project_id} "
                )
                return []
            elif e.resp.status == 403:
                _LOGGER.warning(
                    f"Filestore API not enabled or insufficient permissions for project {self.project_id}, "
                )
                return []
            else:
                _LOGGER.error(
                    f"HTTP error listing Filestore instances for project {self.project_id}: {e}"
                )
                raise e
        except Exception as e:
            _LOGGER.error(
                f"Error listing Filestore instances for project {self.project_id}: {e}"
            )
            raise e from e

    def _extract_location_from_instance_name(self, instance_name: str) -> str:
        try:
            # projects/my-project/locations/us-central1/instances/my-instance
            parts = instance_name.split("/")
            if len(parts) >= 6 and parts[2] == "locations":
                return parts[3]
            return "unknown"
        except Exception:
            return "unknown"
