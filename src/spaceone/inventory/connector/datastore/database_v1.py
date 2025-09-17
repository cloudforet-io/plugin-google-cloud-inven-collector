import logging

from googleapiclient.errors import HttpError

from spaceone.inventory.libs.connector import GoogleCloudConnector

_LOGGER = logging.getLogger(__name__)


class DatastoreDatabaseV1Connector(GoogleCloudConnector):
    google_client_service = "firestore"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_databases(self):
        try:
            # https://cloud.google.com/firestore/docs/reference/rest/v1/projects.databases
            parent = f"projects/{self.project_id}"
            request = self.client.projects().databases().list(parent=parent)

            response = request.execute()

            all_databases = response.get("databases", [])

            # filter DATASTORE_MODE
            datastore_databases = list(
                filter(lambda db: db.get("type") == "DATASTORE_MODE", all_databases)
            )

            return datastore_databases

        except HttpError as e:
            if e.resp.status == 404:
                _LOGGER.warning(
                    f"Firestore service not available for project {self.project_id} "
                )
                return []
            elif e.resp.status == 403:
                _LOGGER.warning(
                    f"Firestore API not enabled or insufficient permissions for project {self.project_id}, "
                )
                return []
            else:
                _LOGGER.error(f"HTTP error listing databases for project {self.project_id}: {e}")
                raise e
        except Exception as e:
            _LOGGER.error(f"Error listing databases for project {self.project_id}: {e}")
            raise e
