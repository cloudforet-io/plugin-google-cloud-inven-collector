import logging
import time

from spaceone.inventory.connector.cloud_run.cloud_run_v1 import CloudRunV1Connector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.cloud_run.route_v1.cloud_service import (
    RouteV1Resource,
    RouteV1Response,
)
from spaceone.inventory.model.cloud_run.route_v1.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_run.route_v1.data import RouteV1

_LOGGER = logging.getLogger(__name__)


class CloudRunRouteV1Manager(GoogleCloudManager):
    connector_name = "CloudRunV1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug("** Cloud Run Route V1 START **")
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
        route_id = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        cloud_run_v1_conn: CloudRunV1Connector = self.locator.get_connector(
            self.connector_name, **params
        )

        # Get lists that relate with routes through Google Cloud API
        # V1은 namespace 기반이므로 단일 namespace로 모든 리소스 조회 가능
        try:
            namespace = f"namespaces/{project_id}"
            routes = cloud_run_v1_conn.list_routes(namespace)

            for route in routes:
                # V1에서는 location 정보가 metadata에 포함되어 있을 수 있음
                location_id = (
                    route.get("metadata", {})
                    .get("labels", {})
                    .get("cloud.googleapis.com/location")
                    or route.get("metadata", {}).get("namespace", "").split("/")[-1]
                    or ""  # default location
                )
                route["_location"] = location_id
        except Exception as e:
            _LOGGER.warning(f"Failed to query routes from namespace: {str(e)}")
            routes = []

        for route in routes:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                route_id = route.get("metadata", {}).get("name", "")
                location_id = route.get("_location", "")
                region = self.parse_region_from_zone(location_id) if location_id else ""

                ##################################
                # 2. Make Base Data
                ##################################
                # Latest Ready Revision 추출
                latest_ready_revision_name = ""
                revision_count = 0

                status_traffic = route.get("status", {}).get("traffic", [])
                for traffic_item in status_traffic:
                    if traffic_item.get("latestRevision") is True:
                        latest_ready_revision_name = traffic_item.get(
                            "revisionName", ""
                        )
                    revision_count += 1

                route.update(
                    {
                        "project": project_id,
                        "location": location_id,
                        "region": region,
                        "latest_ready_revision_name": latest_ready_revision_name,
                        "revision_count": revision_count,
                    }
                )

                ##################################
                # 3. Make Return Resource
                ##################################
                try:
                    route_data = RouteV1(route, strict=False)
                except Exception as e:
                    _LOGGER.error(
                        f"Route {route_id}: Failed to create RouteV1: {str(e)}"
                    )
                    continue

                route_resource = RouteV1Resource(
                    {
                        "name": route_id,
                        "account": project_id,
                        "region_code": location_id,
                        "data": route_data,
                        "reference": ReferenceModel(
                            {
                                "resource_id": route_data.metadata.uid,
                                "external_link": f"https://console.cloud.google.com/run/routes/details/{location_id}/{route_id}?project={project_id}",
                            }
                        ),
                    },
                    strict=False,
                )

                collected_cloud_services.append(
                    RouteV1Response({"resource": route_resource})
                )

            except Exception as e:
                _LOGGER.error(f"Failed to process route {route_id}: {str(e)}")
                error_response = self.generate_resource_error_response(
                    e, "Route", "CloudRun", route_id
                )
                error_responses.append(error_response)

        _LOGGER.debug(f"** Cloud Run Route V1 END ** ({time.time() - start_time:.2f}s)")

        return collected_cloud_services, error_responses
