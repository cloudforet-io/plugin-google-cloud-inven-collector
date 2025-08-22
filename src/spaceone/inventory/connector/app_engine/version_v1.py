import logging
import google.oauth2.service_account
import googleapiclient.discovery

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["AppEngineVersionV1Connector"]
_LOGGER = logging.getLogger(__name__)


class AppEngineVersionV1Connector(GoogleCloudConnector):
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

    def get_version_with_instances(self, service_id, version_id, **query):
        """
        버전과 함께 인스턴스 정보를 포함하여 조회합니다 (v1 API).
        """
        try:
            version_info = self.get_version(service_id, version_id)
            if version_info:
                instances = self.list_instances(service_id, version_id)
                version_info["instances"] = instances
                
            return version_info
        except Exception as e:
            _LOGGER.error(f"Failed to get App Engine version with instances {version_id} (v1): {e}")
            return None

    def list_all_versions_with_instances(self, service_id, **query):
        """
        모든 버전과 인스턴스 정보를 포함하여 조회합니다 (v1 API).
        """
        try:
            versions = self.list_versions(service_id)
            
            for version in versions:
                version_id = version.get("id")
                if version_id:
                    instances = self.list_instances(service_id, version_id)
                    version["instances"] = instances
                    
            return versions
        except Exception as e:
            _LOGGER.error(f"Failed to list all App Engine versions with instances for service {service_id} (v1): {e}")
            return []

    def get_version_metrics(self, service_id, version_id, **query):
        """
        App Engine 버전 메트릭을 조회합니다 (v1 API).
        """
        try:
            # App Engine v1 API에서는 메트릭 정보를 직접 제공하지 않으므로
            # 인스턴스 정보에서 메트릭을 계산
            instances = self.list_instances(service_id, version_id)
            
            metrics = {
                "instance_count": len(instances),
                "memory_usage": 0,
                "cpu_usage": 0,
                "request_count": 0
            }
            
            for instance in instances:
                # 메모리 사용량 합계
                memory_usage = instance.get("memoryUsage", 0)
                if isinstance(memory_usage, (int, float)):
                    metrics["memory_usage"] += memory_usage
                
                # CPU 사용량 합계
                cpu_usage = instance.get("cpuUsage", 0)
                if isinstance(cpu_usage, (int, float)):
                    metrics["cpu_usage"] += cpu_usage
                
                # 요청 수 합계
                request_count = instance.get("requestCount", 0)
                if isinstance(request_count, (int, float)):
                    metrics["request_count"] += request_count
            
            return metrics
        except Exception as e:
            _LOGGER.error(f"Failed to get App Engine version metrics for {version_id} (v1): {e}")
            return None
