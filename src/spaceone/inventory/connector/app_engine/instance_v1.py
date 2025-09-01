import logging
import google.oauth2.service_account
import googleapiclient.discovery

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["AppEngineInstanceV1Connector"]
_LOGGER = logging.getLogger(__name__)


class AppEngineInstanceV1Connector(GoogleCloudConnector):
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

    def list_all_instances(self, **query):
        """
        모든 App Engine 인스턴스를 조회합니다 (v1 API).
        """
        all_instances = []
        
        try:
            # 현재 인스턴스의 client를 사용하여 서비스 목록 조회
            services_response = self.client.apps().services().list(appsId=self.project_id).execute()
            services = services_response.get("services", [])
            
            for service in services:
                service_id = service.get("id")
                if service_id:
                    # 각 서비스의 모든 버전을 조회
                    versions_response = self.client.apps().services().versions().list(
                        appsId=self.project_id, 
                        servicesId=service_id
                    ).execute()
                    versions = versions_response.get("versions", [])
                    
                    for version in versions:
                        version_id = version.get("id")
                        if version_id:
                            # 각 버전의 모든 인스턴스를 조회
                            instances = self.list_instances(service_id, version_id)
                            
                            # 인스턴스에 서비스 및 버전 정보 추가
                            for instance in instances:
                                instance["service_id"] = service_id
                                instance["version_id"] = version_id
                                instance["service_name"] = service.get("name", "")
                                instance["version_name"] = version.get("name", "")
                            
                            all_instances.extend(instances)
                            
        except Exception as e:
            _LOGGER.error(f"Failed to list all App Engine instances (v1): {e}")
            
        return all_instances

    def get_instance_metrics(self, service_id, version_id, instance_id, **query):
        """
        App Engine 인스턴스 메트릭을 조회합니다 (v1 API).
        """
        try:
            instance_info = self.get_instance(service_id, version_id, instance_id)
            if not instance_info:
                return None
            
            metrics = {
                "memory_usage": instance_info.get("memoryUsage", 0),
                "cpu_usage": instance_info.get("cpuUsage", 0),
                "request_count": instance_info.get("requestCount", 0),
                "vm_status": instance_info.get("vmStatus", ""),
                "vm_debug_enabled": instance_info.get("vmDebugEnabled", False),
                "vm_liveness": instance_info.get("vmLiveness", "")
            }
            
            return metrics
        except Exception as e:
            _LOGGER.error(f"Failed to get App Engine instance metrics for {instance_id} (v1): {e}")
            return None

    def list_instances_by_status(self, service_id, version_id, status, **query):
        """
        특정 상태의 App Engine 인스턴스 목록을 조회합니다 (v1 API).
        """
        try:
            all_instances = self.list_instances(service_id, version_id)
            filtered_instances = []
            
            for instance in all_instances:
                if instance.get("vmStatus") == status:
                    filtered_instances.append(instance)
                    
            return filtered_instances
        except Exception as e:
            _LOGGER.error(f"Failed to list App Engine instances by status {status} (v1): {e}")
            return []

    def get_instance_details(self, service_id, version_id, instance_id, **query):
        """
        App Engine 인스턴스 상세 정보를 조회합니다 (v1 API).
        """
        try:
            instance_info = self.get_instance(service_id, version_id, instance_id)
            if not instance_info:
                return None
            
            # 메트릭 정보 추가
            metrics = self.get_instance_metrics(service_id, version_id, instance_id)
            if metrics:
                instance_info["metrics"] = metrics
            
            # VM 상세 정보 추가
            vm_details = instance_info.get("vmDetails", {})
            if vm_details:
                instance_info["vm_zone_name"] = vm_details.get("vmZoneName", "")
                instance_info["vm_id"] = vm_details.get("vmId", "")
                instance_info["vm_ip"] = vm_details.get("vmIp", "")
                instance_info["vm_name"] = vm_details.get("vmName", "")
            
            # 네트워크 정보 추가
            network = instance_info.get("network", {})
            if network:
                instance_info["forwarded_ports"] = network.get("forwardedPorts", "")
                instance_info["instance_tag"] = network.get("instanceTag", "")
                instance_info["network_name"] = network.get("name", "")
                instance_info["subnetwork_name"] = network.get("subnetworkName", "")
            
            # 리소스 정보 추가
            resources = instance_info.get("resources", {})
            if resources:
                instance_info["cpu"] = resources.get("cpu", "")
                instance_info["disk_gb"] = resources.get("diskGb", "")
                instance_info["memory_gb"] = resources.get("memoryGb", "")
                instance_info["volumes"] = resources.get("volumes", "")
            
            return instance_info
        except Exception as e:
            _LOGGER.error(f"Failed to get App Engine instance details for {instance_id} (v1): {e}")
            return None
