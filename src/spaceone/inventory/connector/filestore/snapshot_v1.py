import logging
from typing import Any, Dict, List

from googleapiclient.errors import HttpError

from spaceone.inventory.libs.connector import GoogleCloudConnector

_LOGGER = logging.getLogger(__name__)


class FilestoreSnapshotConnector(GoogleCloudConnector):
    google_client_service = "file"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_all_snapshots(self, **query) -> List[Dict[str, Any]]:
        try:
            # https://cloud.google.com/filestore/docs/reference/rest/v1/projects.locations.instances.snapshots/list
            snapshots = []

            instances = self._list_all_instances()

            for instance in instances:
                instance_name = instance.get("name", "")
                if instance_name:
                    instance_snapshots = self.list_snapshots_for_instance(
                        instance_name, **query
                    )
                    snapshots.extend(instance_snapshots)

            return snapshots

        except HttpError as e:
            if e.resp.status == 404:
                _LOGGER.warning(
                    f"Filestore service not available for project {self.project_id}"
                )
                return []
            elif e.resp.status == 403:
                _LOGGER.warning(
                    f"Filestore API not enabled or insufficient permissions for project {self.project_id}"
                )
                return []
            else:
                _LOGGER.error(
                    f"HTTP error listing Filestore snapshots for project {self.project_id}: {e}"
                )
                raise e
        except Exception as e:
            _LOGGER.error(
                f"Error listing Filestore snapshots for project {self.project_id}: {e}"
            )
            raise e from e

    def list_snapshots_for_instance(
        self, instance_name: str, **query
    ) -> List[Dict[str, Any]]:
        try:
            snapshots = []
            request = (
                self.client.projects()
                .locations()
                .instances()
                .snapshots()
                .list(parent=instance_name, **query)
            )

            while request is not None:
                response = request.execute()

                if "snapshots" in response:
                    for snapshot in response["snapshots"]:
                        snapshot["instance_name"] = instance_name
                        location = self._extract_location_from_instance_name(
                            instance_name
                        )
                        snapshot["location"] = location
                        snapshots.append(snapshot)

                request = (
                    self.client.projects()
                    .locations()
                    .instances()
                    .snapshots()
                    .list_next(previous_request=request, previous_response=response)
                )

            return snapshots

        except HttpError as e:
            if e.resp.status == 404:
                _LOGGER.warning(
                    f"Filestore snapshot service not available for instance {instance_name}"
                )
                return []
            elif e.resp.status == 403:
                _LOGGER.warning(
                    f"Filestore API not enabled or insufficient permissions for instance {instance_name}"
                )
                return []
            else:
                _LOGGER.error(
                    f"HTTP error listing snapshots for instance {instance_name}: {e}"
                )
                raise e
        except Exception as e:
            _LOGGER.error(f"Error listing snapshots for instance {instance_name}: {e}")
            raise e from e

    def _list_all_instances(self, **query) -> List[Dict[str, Any]]:
        try:
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
                    instances.extend(response["instances"])

                request = (
                    self.client.projects()
                    .locations()
                    .instances()
                    .list_next(previous_request=request, previous_response=response)
                )

            return instances

        except HttpError as e:
            if e.resp.status in [404, 403]:
                return []
            else:
                raise e
        except Exception as e:
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
