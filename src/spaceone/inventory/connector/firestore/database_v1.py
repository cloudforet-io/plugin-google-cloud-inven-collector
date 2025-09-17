import logging
from typing import List

from googleapiclient.errors import HttpError

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["FirestoreDatabaseConnector"]
_LOGGER = logging.getLogger(__name__)


class FirestoreDatabaseConnector(GoogleCloudConnector):
    google_client_service = "firestore"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._database_clients = {}

    def _get_admin_client(self, database_id="(default)"):
        if database_id not in self._database_clients:
            try:
                from google.cloud import firestore

                # Create a client for each database
                if database_id == "(default)":
                    # Create a client for the default database
                    client = firestore.Client(
                        project=self.project_id, credentials=self.credentials
                    )
                else:
                    # Create a client for a specific database
                    client = firestore.Client(
                        project=self.project_id,
                        database=database_id,
                        credentials=self.credentials,
                    )

                self._database_clients[database_id] = client

            except ImportError:
                _LOGGER.error(
                    "google-cloud-firestore library not found. "
                    "Please install: pip install google-cloud-firestore"
                )
                raise
            except Exception as e:
                _LOGGER.error(
                    f"Failed to initialize Firestore Admin SDK client for {database_id}: {e}"
                )
                raise

        return self._database_clients[database_id]

    def list_databases(self, **query):
        database_list = []
        query.update({"parent": f"projects/{self.project_id}"})

        try:
            request = self.client.projects().databases().list(**query)
            while request is not None:
                response = request.execute()
                all_databases = response.get("databases", [])
                # Filter out FIRESTORE_NATIVE type
                firestore_databases = list(
                    filter(
                        lambda db: db.get("type") == "FIRESTORE_NATIVE", all_databases
                    )
                )
                database_list.extend(firestore_databases)
                try:
                    request = (
                        self.client.projects()
                        .databases()
                        .list_next(previous_request=request, previous_response=response)
                    )
                except AttributeError:
                    break

            return database_list

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
                _LOGGER.error(
                    f"HTTP error listing Firestore databases for project {self.project_id}: {e}"
                )
                raise e
        except Exception as e:
            _LOGGER.error(
                f"Error listing Firestore databases for project {self.project_id}: {e}"
            )
            raise e

    def list_indexes(self, database_name, **query):
        indexes = []
        parent = f"{database_name}/collectionGroups/-"

        query.update({"parent": parent})

        try:
            request = (
                self.client.projects()
                .databases()
                .collectionGroups()
                .indexes()
                .list(**query)
            )
            while request is not None:
                response = request.execute()
                indexes.extend(response.get("indexes", []))
                try:
                    request = (
                        self.client.projects()
                        .databases()
                        .collectionGroups()
                        .indexes()
                        .list_next(previous_request=request, previous_response=response)
                    )
                except AttributeError:
                    break

            return indexes

        except HttpError as e:
            if e.resp.status == 404:
                _LOGGER.warning(
                    f"Firestore index service not available for database {database_name} "
                )
                return []
            elif e.resp.status == 403:
                _LOGGER.warning(
                    f"Firestore API not enabled or insufficient permissions for database {database_name}, "
                )
                return []
            else:
                _LOGGER.error(
                    f"HTTP error listing indexes for database {database_name}: {e}"
                )
                raise e
        except Exception as e:
            _LOGGER.error(f"Error listing indexes for database {database_name}: {e}")
            raise e

    def list_collections_with_documents(self, database_name, parent="", **query):
        """
        This method optimizes the combined method of list_collection_ids + list_documents
        to avoid duplicate calls to admin_client.document() for the same parent.

        Args:
            database_name: Database name
            parent: Parent document path (empty string for top level)
            **query: Additional query parameters

        Returns:
            List[dict]: List of dictionaries containing collection information and documents
            [
                {
                    "collection_id": str,
                    "documents": List[dict],
                }
            ]
        """
        try:
            database_id = "(default)"
            if "/databases/" in database_name:
                database_id = database_name.split("/databases/")[-1]

            admin_client = self._get_admin_client(database_id)

            collections_with_docs = []
            page_size = query.get("pageSize", 100)

            if not parent:
                # Handle top level collections
                collections = admin_client.collections()

                for collection in collections:
                    collection_id = collection.id

                    # Get documents for the collection
                    documents = []
                    try:
                        docs_stream = collection.limit(page_size).stream()
                        for doc in docs_stream:
                            doc_dict = {
                                "name": doc.reference.path,
                                "fields": doc.to_dict(),
                                "createTime": doc.create_time.isoformat()
                                if doc.create_time
                                else None,
                                "updateTime": doc.update_time.isoformat()
                                if doc.update_time
                                else None,
                            }
                            documents.append(doc_dict)
                    except Exception as e:
                        _LOGGER.warning(
                            f"Failed to get documents for collection {collection_id}: {e}"
                        )

                    collections_with_docs.append(
                        {
                            "collection_id": collection_id,
                            "documents": documents,
                        }
                    )

            else:
                # Handle subcollections (optimized with single document() call)
                parent_doc_ref = admin_client.document(parent)

                # Get subcollections
                subcollections = parent_doc_ref.collections()

                for collection in subcollections:
                    collection_id = collection.id

                    # Get documents for the collection (using the already obtained collection reference)
                    documents = []
                    try:
                        docs_stream = collection.limit(page_size).stream()
                        for doc in docs_stream:
                            doc_dict = {
                                "name": doc.reference.path,
                                "fields": doc.to_dict(),
                                "createTime": doc.create_time.isoformat()
                                if doc.create_time
                                else None,
                                "updateTime": doc.update_time.isoformat()
                                if doc.update_time
                                else None,
                            }
                            documents.append(doc_dict)
                    except Exception as e:
                        _LOGGER.warning(
                            f"Failed to get documents for subcollection {collection_id}: {e}"
                        )

                    collections_with_docs.append(
                        {
                            "collection_id": collection_id,
                            "documents": documents,
                        }
                    )

            return collections_with_docs

        except Exception as e:
            _LOGGER.error(
                f"Failed to list collections with documents using Admin SDK for parent '{parent}': {e}"
            )
            return []

    def list_backup_schedules(self, database_name: str, **query) -> List[dict]:
        backup_schedules = []

        try:
            query.update({"parent": database_name})

            request = self.client.projects().databases().backupSchedules().list(**query)

            while request is not None:
                response = request.execute()
                backup_schedules.extend(response.get("backupSchedules", []))

                try:
                    request = (
                        self.client.projects()
                        .databases()
                        .backupSchedules()
                        .list_next(previous_request=request, previous_response=response)
                    )
                except AttributeError:
                    break

            return backup_schedules

        except Exception as e:
            _LOGGER.error(f"Failed to list backup schedules for {database_name}: {e}")
            return []

    def list_all_backups(self, **query) -> List[dict]:
        backups = []

        try:
            # Use location='-' to retrieve backups from all locations at once
            parent = f"projects/{self.project_id}/locations/-"
            query.update({"parent": parent})

            request = self.client.projects().locations().backups().list(**query)

            while request is not None:
                response = request.execute()
                backups.extend(response.get("backups", []))

                try:
                    request = (
                        self.client.projects()
                        .locations()
                        .backups()
                        .list_next(previous_request=request, previous_response=response)
                    )
                except AttributeError:
                    break

            return backups

        except Exception as e:
            _LOGGER.error(
                f"Failed to list backups from all locations for project {self.project_id}: {e}"
            )
            return []
