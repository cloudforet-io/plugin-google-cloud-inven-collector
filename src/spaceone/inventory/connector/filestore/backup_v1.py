import logging
from typing import Any, Dict, List

from googleapiclient.errors import HttpError

from spaceone.inventory.libs.connector import GoogleCloudConnector

_LOGGER = logging.getLogger(__name__)


class FilestoreBackupConnector(GoogleCloudConnector):
    google_client_service = "file"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_backups(self, **query) -> List[Dict[str, Any]]:
        try:
            # https://cloud.google.com/filestore/docs/reference/rest/v1/projects.locations.backups/list
            # "To retrieve backup information for all locations,
            # use "-" for the {location} value."
            backups = []

            request = (
                self.client.projects()
                .locations()
                .backups()
                .list(
                    parent=f"projects/{self.project_id}/locations/-",
                    **query,
                )
            )

            while request is not None:
                response = request.execute()

                if "backups" in response:
                    for backup in response["backups"]:
                        # projects/my-project/locations/us-central1/backups/my-backup
                        location = self._extract_location_from_backup_name(
                            backup.get("name", "")
                        )
                        backup["location"] = location
                        backups.append(backup)

                request = (
                    self.client.projects()
                    .locations()
                    .backups()
                    .list_next(previous_request=request, previous_response=response)
                )

            return backups

        except HttpError as e:
            if e.resp.status == 404:
                _LOGGER.warning(
                    f"Filestore backup service not available for project {self.project_id}"
                )
                return []
            elif e.resp.status == 403:
                _LOGGER.warning(
                    f"Filestore API not enabled or insufficient permissions for project {self.project_id}"
                )
                return []
            else:
                _LOGGER.error(
                    f"HTTP error listing Filestore backups for project {self.project_id}: {e}"
                )
                raise e
        except Exception as e:
            _LOGGER.error(
                f"Error listing Filestore backups for project {self.project_id}: {e}"
            )
            raise e from e

    def _extract_location_from_backup_name(self, backup_name: str) -> str:
        try:
            # projects/my-project/locations/us-central1/backups/my-backup
            parts = backup_name.split("/")
            if len(parts) >= 6 and parts[2] == "locations":
                return parts[3]
            return "unknown"
        except Exception:
            return "unknown"
