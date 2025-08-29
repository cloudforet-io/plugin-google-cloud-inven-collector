import logging
from schematics import Model
from schematics.types import (
    ModelType,
    ListType,
    StringType,
    IntType,
    FloatType,
    DictType,
)
from spaceone.inventory.libs.schema.cloud_service import BaseResource

_LOGGER = logging.getLogger(__name__)


class AutomaticScaling(Model):
    """AppEngine Automatic Scaling 모델"""
    cool_down_period = StringType(deserialize_from="coolDownPeriod", serialize_when_none=False)
    cpu_utilization = DictType(StringType, deserialize_from="cpuUtilization", serialize_when_none=False)
    max_concurrent_requests = IntType(deserialize_from="maxConcurrentRequests", serialize_when_none=False)
    max_idle_instances = IntType(deserialize_from="maxIdleInstances", serialize_when_none=False)
    max_total_instances = IntType(deserialize_from="maxTotalInstances", serialize_when_none=False)
    min_idle_instances = IntType(deserialize_from="minIdleInstances", serialize_when_none=False)
    min_total_instances = IntType(deserialize_from="minTotalInstances", serialize_when_none=False)


class ManualScaling(Model):
    """AppEngine Manual Scaling 모델"""
    instances = IntType(serialize_when_none=False)


class BasicScaling(Model):
    """AppEngine Basic Scaling 모델"""
    idle_timeout = StringType(deserialize_from="idleTimeout", serialize_when_none=False)
    max_instances = IntType(deserialize_from="maxInstances", serialize_when_none=False)


class Resources(Model):
    """AppEngine Resources 모델"""
    cpu = FloatType(serialize_when_none=False)
    disk_gb = FloatType(deserialize_from="diskGb", serialize_when_none=False)
    memory_gb = FloatType(deserialize_from="memoryGb", serialize_when_none=False)
    volumes = ListType(DictType(StringType), default=[], serialize_when_none=False)


class AppEngineVersion(BaseResource):
    """AppEngine Version 데이터 모델"""
    name = StringType(serialize_when_none=False)
    project_id = StringType(deserialize_from="projectId", serialize_when_none=False)
    service_id = StringType(deserialize_from="serviceId", serialize_when_none=False)
    version_id = StringType(deserialize_from="id", serialize_when_none=False)
    serving_status = StringType(deserialize_from="servingStatus", serialize_when_none=False)
    runtime = StringType(serialize_when_none=False)
    environment = StringType(serialize_when_none=False)
    create_time = StringType(deserialize_from="createTime", serialize_when_none=False)
    update_time = StringType(deserialize_from="updateTime", serialize_when_none=False)
    
    # Scaling configurations
    automatic_scaling = ModelType(AutomaticScaling, deserialize_from="automaticScaling", serialize_when_none=False)
    manual_scaling = ModelType(ManualScaling, deserialize_from="manualScaling", serialize_when_none=False)
    basic_scaling = ModelType(BasicScaling, deserialize_from="basicScaling", serialize_when_none=False)
    
    # Resources
    resources = ModelType(Resources, serialize_when_none=False)
    
    # Calculated fields
    instance_count = StringType(serialize_when_none=False)
    memory_usage = StringType(serialize_when_none=False)
    cpu_usage = StringType(serialize_when_none=False)
    
    def reference(self, region_code):
        return {
            "resource_id": self.version_id,
            "external_link": f"https://console.cloud.google.com/appengine/versions?project={self.project_id}&serviceId={self.service_id}"
        }
