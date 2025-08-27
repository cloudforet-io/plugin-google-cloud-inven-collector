import logging
from typing import Dict, List

from googleapiclient.errors import HttpError

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["CloudBuildV1Connector"]
_LOGGER = logging.getLogger(__name__)


class CloudBuildV1Connector(GoogleCloudConnector):
    google_client_service = "cloudbuild"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_builds(self, **query) -> List[Dict]:
        builds = []
        query.update({"projectId": self.project_id})
        request = self.client.projects().builds().list(**query)
        
        while request is not None:
            try:
                response = request.execute()
                builds.extend(response.get("builds", []))
                request = self.client.projects().builds().list_next(request, response)
            except HttpError as e:
                _LOGGER.error(f"Failed to list builds: {e}")
                break
                
        return builds

    def list_location_builds(self, parent: str, **query) -> List[Dict]:
        builds = []
        query.update({"parent": parent})
        request = self.client.projects().locations().builds().list(**query)
        
        while request is not None:
            try:
                response = request.execute()
                builds.extend(response.get("builds", []))
                request = self.client.projects().locations().builds().list_next(request, response)
            except HttpError as e:
                _LOGGER.error(f"Failed to list location builds: {e}")
                break
                
        return builds

    def list_triggers(self, **query) -> List[Dict]:
        triggers = []
        query.update({"projectId": self.project_id})
        request = self.client.projects().triggers().list(**query)
        
        while request is not None:
            try:
                response = request.execute()
                triggers.extend(response.get("triggers", []))
                request = self.client.projects().triggers().list_next(request, response)
            except HttpError as e:
                _LOGGER.error(f"Failed to list triggers: {e}")
                break
                
        return triggers

    def list_location_triggers(self, parent: str, **query) -> List[Dict]:
        triggers = []
        query.update({"parent": parent})
        request = self.client.projects().locations().triggers().list(**query)
        
        while request is not None:
            try:
                response = request.execute()
                triggers.extend(response.get("triggers", []))
                request = self.client.projects().locations().triggers().list_next(request, response)
            except HttpError as e:
                _LOGGER.error(f"Failed to list location triggers: {e}")
                break
                
        return triggers

    def list_location_worker_pools(self, parent: str, **query) -> List[Dict]:
        worker_pools = []
        query.update({"parent": parent})
        request = self.client.projects().locations().workerPools().list(**query)
        
        while request is not None:
            try:
                response = request.execute()
                worker_pools.extend(response.get("workerPools", []))
                request = self.client.projects().locations().workerPools().list_next(request, response)
            except HttpError as e:
                _LOGGER.error(f"Failed to list worker pools: {e}")
                break
                
        return worker_pools

