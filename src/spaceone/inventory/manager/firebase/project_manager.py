import logging
import time

from spaceone.inventory.connector.firebase.project import FirebaseProjectConnector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.firebase.project.cloud_service import (
    ProjectResource,
    ProjectResponse,
)
from spaceone.inventory.model.firebase.project.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.firebase.project.data import Project

_LOGGER = logging.getLogger(__name__)


class FirebaseProjectManager(GoogleCloudManager):
    connector_name = "FirebaseProjectConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        """
        Args:
            params:
                - options
                - schema
                - secret_data
                - filter
        Response:
            CloudServiceResponse/ErrorResourceResponse
        """
        _LOGGER.debug("** Firebase Project START **")

        start_time = time.time()
        collected_cloud_services = []
        error_responses = []
        project_id = ""

        secret_data = params["secret_data"]

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        firebase_conn: FirebaseProjectConnector = self.locator.get_connector(
            self.connector_name, **params
        )

        # Firebase Management API를 통해 사용 가능한 프로젝트 목록 가져오기
        try:
            available_projects = firebase_conn.list_available_projects()

        except Exception as e:
            _LOGGER.error(f"Failed to list available Firebase projects: {e}")
            error_responses.append(
                self.generate_error_response(e, "", "inventory.Error")
            )
            return [], error_responses

        for project_data in available_projects:
            try:
                project_id = project_data.get("projectId", "")

                # Firebase 프로젝트 데이터 파싱
                firebase_project = Project(project_data)

                # Cloud Service 리소스 생성
                firebase_project_resource = ProjectResource(
                    {
                        "name": firebase_project.project_id,
                        "data": firebase_project,
                        "reference": ReferenceModel(firebase_project.reference()),
                        "region_code": "global",
                        "account": secret_data.get("project_id", ""),
                    }
                )

                collected_cloud_services.append(
                    ProjectResponse({"resource": firebase_project_resource})
                )

            except Exception as e:
                _LOGGER.error(
                    f"[collect_cloud_service] Firebase Project {project_id} => {e}",
                    exc_info=True,
                )
                error_responses.append(
                    self.generate_error_response(e, project_id, "inventory.Error")
                )

        _LOGGER.debug(
            f"** Firebase Project Finished {time.time() - start_time} Seconds **"
        )

        return collected_cloud_services, error_responses
