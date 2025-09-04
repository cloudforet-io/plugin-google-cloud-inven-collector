import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["CloudRunV1Connector"]

_LOGGER = logging.getLogger(__name__)


class CloudRunV1Connector(GoogleCloudConnector):
    google_client_service = "run"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_domain_mappings(self, parent, **query):
        domain_mappings = []
        query.update({"parent": parent})

        while True:
            try:
                response = (
                    self.client.namespaces().domainmappings().list(**query).execute()
                )
                domain_mappings.extend(response.get("items", []))

                continue_token = response.get("metadata", {}).get("continue")
                if continue_token:
                    query["continue"] = continue_token
                else:
                    break
            except Exception as e:
                _LOGGER.error(f"Failed to list domain mappings: {e}")
                break

        return domain_mappings

    def list_services(self, parent, **query):
        """V1 API에서 services 조회 (namespace 기반)"""
        services = []
        query.update({"parent": parent})
        
        while True:
            try:
                response = self.client.namespaces().services().list(**query).execute()
                services.extend(response.get("items", []))
                
                continue_token = response.get("metadata", {}).get("continue")
                if continue_token:
                    query["continue"] = continue_token
                else:
                    break
            except Exception as e:
                _LOGGER.debug(f"Services API not available in v1: {e}")
                break
                
        return services

    def list_jobs(self, parent, **query):
        """V1 API에서 jobs 조회 (제한적 지원, namespace 기반)"""
        jobs = []
        query.update({"parent": parent})
        
        while True:
            try:
                response = self.client.namespaces().jobs().list(**query).execute()
                jobs.extend(response.get("items", []))
                
                continue_token = response.get("metadata", {}).get("continue")
                if continue_token:
                    query["continue"] = continue_token
                else:
                    break
            except Exception as e:
                _LOGGER.debug(f"Jobs API not available in v1: {e}")
                break
                
        return jobs

    def list_revisions(self, parent, **query):
        """V1 API에서 revisions 조회 (namespace 기반)"""
        revisions = []
        query.update({"parent": parent})
        
        while True:
            try:
                response = self.client.namespaces().revisions().list(**query).execute()
                revisions.extend(response.get("items", []))
                
                continue_token = response.get("metadata", {}).get("continue")
                if continue_token:
                    query["continue"] = continue_token
                else:
                    break
            except Exception as e:
                _LOGGER.debug(f"Revisions API not available in v1: {e}")
                break
                
        return revisions

    def list_executions(self, parent, **query):
        """V1 API에서 executions 조회 (namespace 기반)"""
        executions = []
        query.update({"parent": parent})
        
        while True:
            try:
                response = self.client.namespaces().executions().list(**query).execute()
                executions.extend(response.get("items", []))
                
                continue_token = response.get("metadata", {}).get("continue")
                if continue_token:
                    query["continue"] = continue_token
                else:
                    break
            except Exception as e:
                _LOGGER.debug(f"Executions API not available in v1: {e}")
                break
                
        return executions

    def list_tasks(self, parent, **query):
        """V1 API에서 tasks 조회 (namespace 기반)"""
        tasks = []
        query.update({"parent": parent})
        
        while True:
            try:
                response = self.client.namespaces().tasks().list(**query).execute()
                tasks.extend(response.get("items", []))
                
                continue_token = response.get("metadata", {}).get("continue")
                if continue_token:
                    query["continue"] = continue_token
                else:
                    break
            except Exception as e:
                _LOGGER.debug(f"Tasks API not available in v1: {e}")
                break
                
        return tasks

    def list_routes(self, parent, **query):
        """V1 API에서 routes 조회 (namespace 기반)"""
        routes = []
        query.update({"parent": parent})
        
        while True:
            try:
                response = self.client.namespaces().routes().list(**query).execute()
                routes.extend(response.get("items", []))
                
                continue_token = response.get("metadata", {}).get("continue")
                if continue_token:
                    query["continue"] = continue_token
                else:
                    break
            except Exception as e:
                _LOGGER.debug(f"Routes API not available in v1: {e}")
                break
                
        return routes

    def list_configurations(self, parent, **query):
        """V1 API에서 configurations 조회 (namespace 기반)"""
        configurations = []
        query.update({"parent": parent})
        
        while True:
            try:
                response = self.client.namespaces().configurations().list(**query).execute()
                configurations.extend(response.get("items", []))
                
                continue_token = response.get("metadata", {}).get("continue")
                if continue_token:
                    query["continue"] = continue_token
                else:
                    break
            except Exception as e:
                _LOGGER.debug(f"Configurations API not available in v1: {e}")
                break
                
        return configurations

    def list_worker_pools(self, parent, **query):
        """V1 API에서 worker pools 조회 (namespace 기반)"""
        worker_pools = []
        query.update({"parent": parent})
        
        while True:
            try:
                response = self.client.namespaces().workerpools().list(**query).execute()
                worker_pools.extend(response.get("items", []))
                
                continue_token = response.get("metadata", {}).get("continue")
                if continue_token:
                    query["continue"] = continue_token
                else:
                    break
            except Exception as e:
                _LOGGER.debug(f"WorkerPools API not available in v1: {e}")
                break
                
        return worker_pools
