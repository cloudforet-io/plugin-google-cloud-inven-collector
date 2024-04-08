import logging
import time

from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.connector.bigquery.sql_workspace import SQLWorkspaceConnector
from spaceone.inventory.model.bigquery.sql_workspace.cloud_service import (
    BigQueryWorkSpace,
    SQLWorkSpaceResource,
    SQLWorkSpaceResponse,
    # ProjectModel,
)
from spaceone.inventory.model.bigquery.sql_workspace.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from datetime import datetime

_LOGGER = logging.getLogger(__name__)


class SQLWorkspaceManager(GoogleCloudManager):
    connector_name = "SQLWorkspaceConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug(f"** Big Query SQL Workspace START **")
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

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        big_query_conn: SQLWorkspaceConnector = self.locator.get_connector(
            self.connector_name, **params
        )
        data_sets = big_query_conn.list_dataset()
        # projects = big_query_conn.list_projects()

        for data_set in data_sets:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################

                updated_bq_tables = []

                data_refer = data_set.get("datasetReference", {})
                data_set_id = data_refer.get("datasetId", "")
                dataset_project_id = data_refer.get("projectId")
                bq_dataset = big_query_conn.get_dataset(data_set_id)
                creation_time = bq_dataset.get("creationTime", "")
                last_modified_time = bq_dataset.get("lastModifiedTime")
                region = self._get_region(bq_dataset.get("location", ""))
                exp_partition_ms = bq_dataset.get("defaultPartitionExpirationMs")
                exp_table_ms = bq_dataset.get("defaultTableExpirationMs")

                bq_tables = big_query_conn.list_tables(data_set_id)
                if bq_tables:
                    updated_bq_tables = self._preprocess_bigquery_tables_info(bq_tables)

                labels = self.convert_labels_format(bq_dataset.get("labels", {}))
                google_cloud_monitoring_filters = [
                    {"key": "resource.labels.dataset_id", "value": data_set_id}
                ]

                ##################################
                # 2. Make Base Data
                ##################################

                bq_dataset.update(
                    {
                        "name": data_set_id,
                        "project": project_id,
                        "tables": updated_bq_tables,
                        "region": region,
                        # "matching_project": self._get_matching_project(
                        #     dataset_project_id, projects
                        # ),
                        "creationTime": self._convert_unix_timestamp(creation_time),
                        "lastModifiedTime": self._convert_unix_timestamp(
                            last_modified_time
                        ),
                        "default_partition_expiration_ms_display": self._convert_milliseconds_to_minutes(
                            exp_partition_ms
                        ),
                        "default_table_expiration_ms_display": self._convert_milliseconds_to_minutes(
                            exp_table_ms
                        ),
                        "labels": labels,
                        "google_cloud_monitoring": self.set_google_cloud_monitoring(
                            project_id,
                            "bigquery.googleapis.com",
                            data_set_id,
                            google_cloud_monitoring_filters,
                        ),
                    }
                )
                big_query_data = BigQueryWorkSpace(bq_dataset, strict=False)

                ##################################
                # 3. Make Return Resource
                ##################################
                big_query_work_space_resource = SQLWorkSpaceResource(
                    {
                        "name": data_set_id,
                        "account": project_id,
                        "region_code": region,
                        "tags": labels,
                        "data": big_query_data,
                        "reference": ReferenceModel(big_query_data.reference()),
                    }
                )

                ##################################
                # 4. Make Collected Region Code
                ##################################
                self.set_region_code(region)

                ##################################
                # 5. Make Resource Response Object
                # List of SQLWorkSpaceResponse Object
                ##################################
                collected_cloud_services.append(
                    SQLWorkSpaceResponse({"resource": big_query_work_space_resource})
                )
            except Exception as e:
                _LOGGER.error(f"[collect_cloud_service] => {e}", exc_info=True)
                error_response = self.generate_resource_error_response(
                    e, "BigQuery", "SQLWorkspace", data_set_id
                )
                error_responses.append(error_response)

        _LOGGER.debug(f"** Big Query Finished {time.time() - start_time} Seconds **")
        return collected_cloud_services, error_responses

    def _get_region(self, location):
        matched_info = self.match_region_info(location)
        return matched_info.get("region_code") if matched_info else "global"

    def _preprocess_bigquery_tables_info(self, bq_tables):
        preprocessed_bq_tables = []
        for bq_table in bq_tables:
            table_id = bq_table.get("id")
            name = bq_table.get("tableReference", {}).get("tableId")
            table_type = bq_table.get("type")
            creation_time = bq_table.get("creationTime")
            expiration_time = bq_table.get("expirationTime")
            last_modified_time = bq_table.get("lastModifiedTime")

            bq_table.update(
                {
                    "id": table_id,
                    "name": name,
                    "type": table_type,
                    "creationTime": self._convert_unix_timestamp(creation_time),
                    "expirationTime": self._convert_unix_timestamp(expiration_time),
                    "lastModifiedTime": self._convert_unix_timestamp(
                        last_modified_time
                    ),
                }
            )
            preprocessed_bq_tables.append(bq_table)

        return preprocessed_bq_tables

    # @staticmethod
    # def _get_matching_project(project_id, projects):
    #     _projects = []
    #     for project in projects:
    #         if project_id == project.get("id"):
    #             _projects.append(ProjectModel(project, strict=False))
    #     return _projects

    @staticmethod
    def _convert_milliseconds_to_minutes(milliseconds):
        if milliseconds:
            minutes = (int(milliseconds) / 1000) / 60
            return minutes
        else:
            return None

    @staticmethod
    def _convert_unix_timestamp(unix_timestamp):
        if unix_timestamp:
            try:
                return datetime.fromtimestamp(int(unix_timestamp) / 1000)
            except Exception as e:
                _LOGGER.error(f"[_convert_unix_timestamp] {e}")

        return None
