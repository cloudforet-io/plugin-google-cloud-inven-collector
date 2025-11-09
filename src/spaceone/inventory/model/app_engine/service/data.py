import logging

from schematics import Model
from schematics.types import DictType, ListType, ModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import BaseResource

_LOGGER = logging.getLogger(__name__)


class TrafficSplit(Model):
    """AppEngine Traffic Split 모델"""
    allocations = DictType(StringType, serialize_when_none=False)
    shard_by = StringType(deserialize_from="shardBy", serialize_when_none=False)


class VpcAccessConnector(Model):
    """AppEngine VPC Access Connector 모델"""
    name = StringType(serialize_when_none=False)
    egress_setting = StringType(deserialize_from="egressSetting", serialize_when_none=False)


class NetworkSettings(Model):
    """AppEngine Network Settings 모델"""
    forwarded_ports = ListType(StringType, deserialize_from="forwardedPorts", default=[], serialize_when_none=False)
    instance_tag = StringType(deserialize_from="instanceTag", serialize_when_none=False)
    name = StringType(serialize_when_none=False)
    subnetwork_name = StringType(deserialize_from="subnetworkName", serialize_when_none=False)
    ingress_traffic_allowed = StringType(deserialize_from="ingressTrafficAllowed", serialize_when_none=False)


class AppEngineService(BaseResource):
    """AppEngine Service 데이터 모델"""
    name = StringType(serialize_when_none=False)
    project_id = StringType(deserialize_from="projectId", serialize_when_none=False)
    service_id = StringType(deserialize_from="id", serialize_when_none=False)
    
    # Traffic Split
    split = ModelType(TrafficSplit, serialize_when_none=False)
    
    # Network Settings
    network = ModelType(NetworkSettings, serialize_when_none=False)
    
    # VPC Access Connector
    vpc_access_connector = ModelType(VpcAccessConnector, deserialize_from="vpcAccessConnector", serialize_when_none=False)
    
    # Labels (from generatedCustomerMetadata)
    labels = DictType(StringType, serialize_when_none=False)
    
    # Calculated fields
    version_count = StringType(serialize_when_none=False)
    instance_count = StringType(serialize_when_none=False)
    
    # Latest version info (aggregated from versions)
    latest_version_deployed = StringType(serialize_when_none=False)
    
    def reference(self, region_code):
        return {
            "resource_id": self.service_id,
            "external_link": f"https://console.cloud.google.com/appengine/services?project={self.project_id}"
        }
