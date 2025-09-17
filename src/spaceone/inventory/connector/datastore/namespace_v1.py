import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

_LOGGER = logging.getLogger(__name__)


class DatastoreNamespaceV1Connector(GoogleCloudConnector):
    google_client_service = "datastore"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run_query(self, namespace_id=None, database_id="(default)", **query):
        try:
            # https://cloud.google.com/datastore/docs/reference/data/rest/v1/projects/runQuery
            query_body = {
                "query": {
                    "kind": [{"name": "__kind__"}],
                }
            }

            # Convert (default) to empty string when calling API
            api_database_id = "" if database_id == "(default)" else database_id
            api_namespace_id = (
                ""
                if namespace_id == "(default)" or namespace_id is None
                else namespace_id
            )

            query_body["databaseId"] = api_database_id
            query_body["partitionId"] = {"namespaceId": api_namespace_id}

            # For named database, set routing header
            headers = {}
            if api_database_id:  # Not empty string (named database)
                headers["x-goog-request-params"] = (
                    f"project_id={self.project_id}&database_id={api_database_id}"
                )

            request = self.client.projects().runQuery(
                projectId=self.project_id, body=query_body, **query
            )

            if headers:
                request.headers.update(headers)

            response = request.execute()

            return response

        except Exception as e:
            _LOGGER.error(
                f"Error running query for namespace '{namespace_id}' in database '{database_id}': {e}"
            )
            raise e

    def list_namespaces(self, database_id="(default)", **query):
        try:
            # https://cloud.google.com/datastore/docs/reference/data/rest/v1/projects/runQuery
            query_body = {
                "query": {
                    "kind": [{"name": "__namespace__"}],
                },
            }

            # Convert (default) to empty string when calling API
            api_database_id = "" if database_id == "(default)" else database_id

            query_body["databaseId"] = api_database_id

            # For named database, set routing header
            headers = {}
            if api_database_id:
                headers["x-goog-request-params"] = (
                    f"project_id={self.project_id}&database_id={api_database_id}"
                )

            request = self.client.projects().runQuery(
                projectId=self.project_id, body=query_body, **query
            )

            if headers:
                request.headers.update(headers)

            response = request.execute()

            return response

        except Exception as e:
            _LOGGER.error(f"Error listing namespaces for database {database_id}: {e}")
            raise e

    def get_namespace_kinds(self, namespace_id=None, database_id="(default)"):
        try:
            response = self.run_query(
                namespace_id=namespace_id, database_id=database_id
            )

            # Parse the response according to the API response structure
            if "batch" in response and "entityResults" in response["batch"]:
                entity_results = response["batch"]["entityResults"]

                # Filter out kinds that do not start with __
                all_kinds = []
                for entity_result in entity_results:
                    if "entity" in entity_result and "key" in entity_result["entity"]:
                        key = entity_result["entity"]["key"]
                        if "path" in key and len(key["path"]) > 0:
                            # Extract kind name from the first element of the path
                            path_element = key["path"][0]
                            kind_name = path_element.get("name", "")
                            if kind_name:
                                all_kinds.append(kind_name)

                # Filter out kinds that do not start with __ (before the for loop)
                kinds = list(filter(lambda kind: not kind.startswith("__"), all_kinds))
            else:
                kinds = []

            return kinds

        except Exception as e:
            _LOGGER.error(
                f"Error getting kinds for namespace '{namespace_id}' in database '{database_id}': {e}"
            )
            raise e

    def extract_namespaces_from_response(self, response):
        namespaces = []

        try:
            if "batch" in response and "entityResults" in response["batch"]:
                for entity_result in response["batch"]["entityResults"]:
                    if "entity" in entity_result and "key" in entity_result["entity"]:
                        key = entity_result["entity"]["key"]
                        if "path" in key and len(key["path"]) > 0:
                            # Extract namespace information from the first element of the path
                            path_element = key["path"][0]
                            namespace_name = path_element.get("name", "")
                            namespace_id = path_element.get("id", "")

                            if namespace_name:
                                # Collect only namespaces that were actually created by users (name field exists)
                                namespaces.append(namespace_name)
                            elif namespace_id and namespace_id != "1":
                                # Other ID namespaces (excluding default namespace "1")
                                namespaces.append(f"namespace-{namespace_id}")

            return namespaces

        except Exception as e:
            _LOGGER.error(f"Error extracting namespaces from response: {e}")
            return []
