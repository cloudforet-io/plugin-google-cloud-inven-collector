import logging
from schematics import Model
from schematics.types import (
    ModelType,
    ListType,
    StringType,
    BooleanType,
)
from spaceone.inventory.libs.schema.cloud_service import BaseResource

_LOGGER = logging.getLogger(__name__)


class FeatureSettings(Model):
    """AppEngine Feature Settings 모델"""
    split_health_checks = BooleanType(deserialize_from="splitHealthChecks", serialize_when_none=False)
    use_container_optimized_os = BooleanType(deserialize_from="useContainerOptimizedOs", serialize_when_none=False)


class IAPSettings(Model):
    """AppEngine IAP Settings 모델"""
    enabled = BooleanType(serialize_when_none=False)
    oauth2_client_id = StringType(deserialize_from="oauth2ClientId", serialize_when_none=False)
    oauth2_client_secret = StringType(deserialize_from="oauth2ClientSecret", serialize_when_none=False)


class DispatchRule(Model):
    """AppEngine Dispatch Rule 모델"""
    domain = StringType(serialize_when_none=False)
    path = StringType(serialize_when_none=False)
    service = StringType(serialize_when_none=False)


class AppEngineApplication(BaseResource):
    """AppEngine Application 데이터 모델"""
    name = StringType(serialize_when_none=False)
    project_id = StringType(deserialize_from="projectId", serialize_when_none=False)
    location_id = StringType(deserialize_from="locationId", serialize_when_none=False)
    serving_status = StringType(deserialize_from="servingStatus", serialize_when_none=False)
    default_hostname = StringType(deserialize_from="defaultHostname", serialize_when_none=False)
    default_cookie_expiration = StringType(deserialize_from="defaultCookieExpiration", serialize_when_none=False)
    code_bucket = StringType(deserialize_from="codeBucket", serialize_when_none=False)
    gcr_domain = StringType(deserialize_from="gcrDomain", serialize_when_none=False)
    database_type = StringType(deserialize_from="databaseType", serialize_when_none=False)
    create_time = StringType(deserialize_from="createTime", serialize_when_none=False)
    update_time = StringType(deserialize_from="updateTime", serialize_when_none=False)
    
    # Feature Settings
    feature_settings = ModelType(FeatureSettings, deserialize_from="featureSettings", serialize_when_none=False)
    
    # IAP Settings
    iap = ModelType(IAPSettings, serialize_when_none=False)
    
    # Dispatch Rules
    dispatch_rules = ListType(ModelType(DispatchRule), deserialize_from="dispatchRules", default=[], serialize_when_none=False)
    
    # Calculated fields
    version_count = StringType(serialize_when_none=False)
    instance_count = StringType(serialize_when_none=False)
    
    def reference(self, region_code):
        return {
            "resource_id": self.name,
            "external_link": f"https://console.cloud.google.com/appengine/instances?project={self.project_id}"
        }
