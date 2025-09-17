import logging
import time

from spaceone.inventory.connector.datastore.index_v1 import DatastoreIndexV1Connector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.datastore.index.cloud_service import (
    DatastoreIndexResource,
    DatastoreIndexResponse,
)
from spaceone.inventory.model.datastore.index.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.datastore.index.data import DatastoreIndexData

_LOGGER = logging.getLogger(__name__)


class DatastoreIndexManager(GoogleCloudManager):
    connector_name = "DatastoreIndexV1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug("** Datastore Index START **")
        start_time = time.time()

        collected_cloud_services = []
        error_responses = []
        index_id = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        try:
            ##################################
            # 0. Gather All Related Resources
            ##################################
            index_conn: DatastoreIndexV1Connector = self.locator.get_connector(
                self.connector_name, **params
            )

            # Get all indexes (project level)
            indexes = index_conn.list_indexes()
            _LOGGER.info(f"Found {len(indexes)} total indexes")

            # Create resources for each index
            for index in indexes:
                try:
                    ##################################
                    # 1. Set Basic Information
                    ##################################
                    index_id = index.get("indexId", "")

                    ##################################
                    # 2. Make Base Data
                    ##################################
                    properties = index.get("properties", [])
                    property_count = len(properties)
                    sorted_properties = []
                    unsorted_properties = []

                    for prop in properties:
                        prop_name = prop.get("name", "")
                        direction = prop.get("direction", "ASCENDING")
                        if direction in ["ASCENDING", "DESCENDING"]:
                            sorted_properties.append(f"{prop_name} ({direction})")
                        else:
                            unsorted_properties.append(prop_name)

                    index.update(
                        {
                            "property_count": property_count,
                            "sorted_properties": sorted_properties,
                            "unsorted_properties": unsorted_properties,
                            "project": project_id,
                        }
                    )

                    index_data = DatastoreIndexData(index, strict=False)

                    ##################################
                    # 3. Make Return Resource
                    ##################################
                    index_resource = DatastoreIndexResource(
                        {
                            "name": index_id,
                            "account": project_id,
                            "data": index_data,
                            "region_code": "global",
                            "reference": ReferenceModel(index_data.reference()),
                        }
                    )

                    ##################################
                    # 4. Make Collected Region Code
                    ##################################
                    self.set_region_code("global")

                    ##################################
                    # 5. Make Resource Response Object
                    ##################################
                    collected_cloud_services.append(
                        DatastoreIndexResponse({"resource": index_resource})
                    )

                except Exception as e:
                    _LOGGER.error(f"Failed to process index {index_id}: {e}")
                    error_response = self.generate_resource_error_response(
                        e, "Datastore", "Index", index_id
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(f"Failed to collect Datastore indexes: {e}")
            error_response = self.generate_resource_error_response(
                e, "Datastore", "Index"
            )
            error_responses.append(error_response)

        _LOGGER.debug(
            f"** Datastore Namespace Finished {time.time() - start_time} Seconds **"
        )
        return collected_cloud_services, error_responses
