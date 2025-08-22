import logging
import google.oauth2.service_account
import googleapiclient.discovery

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["AppEngineApplicationV1Connector"]
_LOGGER = logging.getLogger(__name__)


class AppEngineApplicationV1Connector(GoogleCloudConnector):
    google_client_service = "appengine"
    version = "v1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def verify(self, options, secret_data):
        self.get_connect(secret_data)
        return "ACTIVE"

    def get_connect(self, secret_data):
        """
        cred(dict)
            - type: ..
            - project_id: ...
            - token_uri: ...
            - ...
        """
        self.project_id = secret_data.get("project_id")
        credentials = (
            google.oauth2.service_account.Credentials.from_service_account_info(
                secret_data
            )
        )
        self.client = googleapiclient.discovery.build(
            "appengine", "v1", credentials=credentials
        )

    def get_application(self, **query):
        """
        App Engine 애플리케이션 정보를 조회합니다 (v1 API).
        """
        try:
            request = self.client.apps().get(
                appsId=self.project_id
            )
            return request.execute()
        except Exception as e:
            _LOGGER.error(f"Failed to get App Engine application (v1): {e}")
            return None

    def list_services(self, **query):
        """
        App Engine 서비스 목록을 조회합니다 (v1 API).
        """
        service_list = []
        query.update({"appsId": self.project_id})
        
        try:
            request = self.client.apps().services().list(**query)
            while request is not None:
                response = request.execute()
                if "services" in response:
                    service_list.extend(response.get("services", []))
                
                # 페이지네이션 처리
                try:
                    request = self.client.apps().services().list_next(
                        previous_request=request, previous_response=response
                    )
                except AttributeError:
                    break
        except Exception as e:
            _LOGGER.error(f"Failed to list App Engine services (v1): {e}")
            
        return service_list

    def get_service(self, service_id, **query):
        """
        특정 App Engine 서비스 정보를 조회합니다 (v1 API).
        """
        try:
            request = self.client.apps().services().get(
                appsId=self.project_id,
                servicesId=service_id
            )
            return request.execute()
        except Exception as e:
            _LOGGER.error(f"Failed to get App Engine service {service_id} (v1): {e}")
            return None

    def list_versions(self, service_id, **query):
        """
        App Engine 버전 목록을 조회합니다 (v1 API).
        """
        version_list = []
        query.update({
            "appsId": self.project_id,
            "servicesId": service_id
        })
        
        try:
            request = self.client.apps().services().versions().list(**query)
            while request is not None:
                response = request.execute()
                if "versions" in response:
                    version_list.extend(response.get("versions", []))
                
                # 페이지네이션 처리
                try:
                    request = self.client.apps().services().versions().list_next(
                        previous_request=request, previous_response=response
                    )
                except AttributeError:
                    break
        except Exception as e:
            _LOGGER.error(f"Failed to list App Engine versions for service {service_id} (v1): {e}")
            
        return version_list

    def get_version(self, service_id, version_id, **query):
        """
        특정 App Engine 버전 정보를 조회합니다 (v1 API).
        """
        try:
            request = self.client.apps().services().versions().get(
                appsId=self.project_id,
                servicesId=service_id,
                versionsId=version_id
            )
            return request.execute()
        except Exception as e:
            _LOGGER.error(f"Failed to get App Engine version {version_id} (v1): {e}")
            return None

    def list_instances(self, service_id, version_id, **query):
        """
        App Engine 인스턴스 목록을 조회합니다 (v1 API).
        """
        instance_list = []
        query.update({
            "appsId": self.project_id,
            "servicesId": service_id,
            "versionsId": version_id
        })
        
        try:
            request = self.client.apps().services().versions().instances().list(**query)
            while request is not None:
                response = request.execute()
                if "instances" in response:
                    instance_list.extend(response.get("instances", []))
                
                # 페이지네이션 처리
                try:
                    request = self.client.apps().services().versions().instances().list_next(
                        previous_request=request, previous_response=response
                    )
                except AttributeError:
                    break
        except Exception as e:
            _LOGGER.error(f"Failed to list App Engine instances for version {version_id} (v1): {e}")
            
        return instance_list

    def get_instance(self, service_id, version_id, instance_id, **query):
        """
        특정 App Engine 인스턴스 정보를 조회합니다 (v1 API).
        """
        try:
            request = self.client.apps().services().versions().instances().get(
                appsId=self.project_id,
                servicesId=service_id,
                versionsId=version_id,
                instancesId=instance_id
            )
            return request.execute()
        except Exception as e:
            _LOGGER.error(f"Failed to get App Engine instance {instance_id} (v1): {e}")
            return None

    def list_operations(self, **query):
        """
        App Engine 작업 목록을 조회합니다 (v1 API).
        """
        operation_list = []
        query.update({"appsId": self.project_id})
        
        try:
            request = self.client.apps().operations().list(**query)
            while request is not None:
                response = request.execute()
                if "operations" in response:
                    operation_list.extend(response.get("operations", []))
                
                # 페이지네이션 처리
                try:
                    request = self.client.apps().operations().list_next(
                        previous_request=request, previous_response=response
                    )
                except AttributeError:
                    break
        except Exception as e:
            _LOGGER.error(f"Failed to list App Engine operations (v1): {e}")
            
        return operation_list
