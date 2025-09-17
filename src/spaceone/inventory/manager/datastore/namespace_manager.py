import logging
import time

from spaceone.inventory.connector.datastore.database_v1 import (
    DatastoreDatabaseV1Connector,
)
from spaceone.inventory.connector.datastore.namespace_v1 import (
    DatastoreNamespaceV1Connector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.datastore.namespace.cloud_service import (
    DatastoreNamespaceResource,
    DatastoreNamespaceResponse,
)
from spaceone.inventory.model.datastore.namespace.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.datastore.namespace.data import DatastoreNamespaceData

_LOGGER = logging.getLogger(__name__)


class DatastoreNamespaceManager(GoogleCloudManager):
    connector_name = "DatastoreNamespaceV1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    namespace_conn = None

    def collect_cloud_service(self, params):
        _LOGGER.debug("** Datastore Namespace START **")
        start_time = time.time()

        collected_cloud_services = []
        error_responses = []
        namespace_id = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        try:
            ##################################
            # 0. Gather All Related Resources
            ##################################
            self.namespace_conn: DatastoreNamespaceV1Connector = (
                self.locator.get_connector(self.connector_name, **params)
            )

            # Get DATASTORE_MODE database information (ID + locationId)
            database_infos = self._get_datastore_database_infos(params)

            # Get all namespaces for all databases
            namespaces = self._list_namespaces_for_databases(database_infos)

            # Create resources for each namespace
            for namespace in namespaces:
                try:
                    ##################################
                    # 1. Set Basic Information
                    ##################################
                    namespace_id = namespace.get("namespace_id", "(default)")
                    display_name = namespace_id or "Default Namespace"
                    region_code = namespace.get("location_id", "global")

                    ##################################
                    # 2. Make Base Data
                    ##################################
                    namespace.update(
                        {
                            "project": project_id,
                        }
                    )
                    namespace_data = DatastoreNamespaceData(namespace, strict=False)

                    ##################################
                    # 3. Make Return Resource
                    ##################################
                    namespace_resource = DatastoreNamespaceResource(
                        {
                            "name": display_name,
                            "account": project_id,
                            "data": namespace_data,
                            "region_code": region_code,
                            "reference": ReferenceModel(namespace_data.reference()),
                        }
                    )

                    ##################################
                    # 4. Make Collected Region Code
                    ##################################
                    self.set_region_code(region_code)

                    ##################################
                    # 5. Make Resource Response Object
                    ##################################
                    collected_cloud_services.append(
                        DatastoreNamespaceResponse({"resource": namespace_resource})
                    )

                except Exception as e:
                    _LOGGER.error(f"Failed to process namespace {namespace_id}: {e}")
                    error_response = self.generate_resource_error_response(
                        e, "Datastore", "Namespace", namespace_id
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(f"Failed to collect Datastore namespaces: {e}")
            error_response = self.generate_resource_error_response(
                e, "Datastore", "Namespace"
            )
            error_responses.append(error_response)

        # 수집 완료 로깅
        _LOGGER.debug(
            f"** Datastore Namespace Finished {time.time() - start_time} Seconds **"
        )
        return collected_cloud_services, error_responses

    def _list_namespaces_for_databases(self, database_infos):
        all_namespaces = []

        try:
            # Get namespaces for each database
            for database_info in database_infos:
                database_id = database_info["database_id"]
                location_id = database_info["location_id"]
                try:
                    # Get all namespaces list
                    response = self.namespace_conn.list_namespaces(database_id)

                    # Extract namespace list from API response (only user created namespaces)
                    user_namespace_ids = (
                        self.namespace_conn.extract_namespaces_from_response(response)
                    )

                    # Create total namespace list (default namespace + user created namespaces)
                    all_namespace_ids = [
                        None
                    ] + user_namespace_ids  # None = default namespace

                    # Get detailed information for all namespaces
                    for namespace_id in all_namespace_ids:
                        namespace_data = self._get_namespace_data(
                            namespace_id, database_id, location_id
                        )
                        if namespace_data:
                            all_namespaces.append(namespace_data)

                except Exception as e:
                    _LOGGER.error(
                        f"Error listing namespaces for database {database_id}: {e}"
                    )
                    # Try to get default namespace even if an error occurs
                    try:
                        default_namespace_data = self._get_namespace_data(
                            None, database_id, location_id
                        )
                        if default_namespace_data:
                            all_namespaces.append(default_namespace_data)
                    except Exception as default_e:
                        _LOGGER.error(
                            f"Error getting default namespace for database {database_id}: {default_e}"
                        )
                    continue

            _LOGGER.info(
                f"Found {len(all_namespaces)} total namespaces across all databases"
            )

        except Exception as e:
            _LOGGER.error(f"Error listing namespaces for databases: {e}")
            raise e

        return all_namespaces

    def _get_datastore_database_infos(self, params):
        try:
            database_conn: DatastoreDatabaseV1Connector = self.locator.get_connector(
                "DatastoreDatabaseV1Connector", **params
            )

            # Get database list
            datastore_databases = database_conn.list_databases()

            # Create database info list
            database_infos = []
            for database in datastore_databases:
                name = database.get("name", "")
                database_id = name.split("/")[-1] if "/" in name else name
                location_id = database.get("locationId", "global")

                if database_id:  # Not empty string only
                    database_infos.append(
                        {"database_id": database_id, "location_id": location_id}
                    )

            # Add default database if the list is empty
            if not database_infos:
                database_infos.append(
                    {"database_id": "(default)", "location_id": "global"}
                )

            _LOGGER.info(f"Found {len(database_infos)} DATASTORE_MODE databases")
            return database_infos

        except Exception as e:
            _LOGGER.error(f"Error getting datastore database infos: {e}")
            return [
                {"database_id": "(default)", "location_id": "global"}
            ]  # Error occurs, return default database

    def _get_namespace_data(
        self, namespace_id, database_id="(default)", location_id="global"
    ):
        try:
            kinds = self.namespace_conn.get_namespace_kinds(namespace_id, database_id)

            namespace_data = {
                "namespace_id": namespace_id
                or "(default)",  # Default namespace is (default)
                "display_name": namespace_id or "Default Namespace",
                "kinds": kinds,
                "kind_count": len(kinds),
                "database_id": database_id,
                "location_id": location_id,
            }

            return namespace_data

        except Exception as e:
            _LOGGER.error(
                f"Error getting namespace data for '{namespace_id}' in database '{database_id}': {e}"
            )
            return None
