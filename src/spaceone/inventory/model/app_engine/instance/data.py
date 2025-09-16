import logging
from schematics import Model
from schematics.types import (
    ModelType,
    ListType,
    StringType,
    IntType,
    BooleanType,
    FloatType,
    DictType,
)
from spaceone.inventory.libs.schema.cloud_service import BaseResource

_LOGGER = logging.getLogger(__name__)


class VMDetails(Model):
    """AppEngine VM Details 모델"""
    vm_zone_name = StringType(deserialize_from="vmZoneName", serialize_when_none=False)
    vm_id = StringType(deserialize_from="vmId", serialize_when_none=False)
    vm_ip = StringType(deserialize_from="vmIp", serialize_when_none=False)
    vm_name = StringType(deserialize_from="vmName", serialize_when_none=False)


class Availability(Model):
    """AppEngine Availability 모델"""
    liveness = StringType(serialize_when_none=False, default="")
    readiness = StringType(serialize_when_none=False, default="")


class Network(Model):
    """AppEngine Network 모델"""
    forwarded_ports = ListType(StringType, deserialize_from="forwardedPorts", default=[], serialize_when_none=False)
    instance_tag = StringType(deserialize_from="instanceTag", serialize_when_none=False)
    name = StringType(serialize_when_none=False)
    subnetwork_name = StringType(deserialize_from="subnetworkName", serialize_when_none=False)


class Resources(Model):
    """AppEngine Resources 모델"""
    cpu = FloatType(serialize_when_none=False)
    disk_gb = FloatType(deserialize_from="diskGb", serialize_when_none=False)
    memory_gb = FloatType(deserialize_from="memoryGb", serialize_when_none=False)
    volumes = ListType(DictType(StringType), default=[], serialize_when_none=False)


class AppEngineInstance(BaseResource):
    """AppEngine Instance 데이터 모델"""
    name = StringType(serialize_when_none=False)
    project_id = StringType(serialize_when_none=False)
    service_id = StringType(serialize_when_none=False)
    version_id = StringType(serialize_when_none=False)
    instance_id = StringType(serialize_when_none=False)
    vm_status = StringType(serialize_when_none=False)
    vm_debug_enabled = BooleanType(serialize_when_none=False)
    vm_liveness = StringType(serialize_when_none=False)
    request_count = IntType(serialize_when_none=False)
    memory_usage = FloatType(serialize_when_none=False)
    cpu_usage = FloatType(serialize_when_none=False)
    create_time = StringType(serialize_when_none=False)
    update_time = StringType(serialize_when_none=False)
    start_time = StringType(serialize_when_none=False)
    
    # VM Details
    vm_details = ModelType(VMDetails, deserialize_from="vmDetails", serialize_when_none=False)
    
    # AppEngine Release
    app_engine_release = StringType(deserialize_from="appEngineRelease", serialize_when_none=False)
    
    # Availability
    availability = ModelType(Availability, serialize_when_none=False)
    
    # Network
    network = ModelType(Network, serialize_when_none=False)
    
    # Resources
    resources = ModelType(Resources, serialize_when_none=False)
    
    def reference(self, region_code):
        return {
            "resource_id": self.instance_id,
            "external_link": f"https://console.cloud.google.com/appengine/instances?project={self.project_id}&serviceId={self.service_id}&versionId={self.version_id}"
        }
