from schematics.types import ModelType, StringType, PolyModelType

from spaceone.inventory.model.app_engine.application.data import AppEngineApplication
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    TextDyField,
    EnumDyField,
    DateTimeDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
    TableDynamicLayout,
)
from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)

"""
AppEngine Application
"""
app_engine_application = ItemDynamicLayout.set_fields(
    "AppEngine Application",
    fields=[
        TextDyField.data_source("Name", "data.name"),
        TextDyField.data_source("Project ID", "data.project_id"),
        TextDyField.data_source("Location", "data.location_id"),
        EnumDyField.data_source(
            "Serving Status",
            "data.serving_status",
            default_state={
                "safe": ["SERVING"],
                "warning": ["USER_DISABLED"],
                "alert": ["STOPPED"],
            },
        ),
        TextDyField.data_source("Default Hostname", "data.default_hostname"),
        TextDyField.data_source("Default Cookie Expiration", "data.default_cookie_expiration"),
        TextDyField.data_source("Code Bucket", "data.code_bucket"),
        TextDyField.data_source("GCR Domain", "data.gcr_domain"),
        TextDyField.data_source("Database Type", "data.database_type"),
        DateTimeDyField.data_source("Created", "data.create_time"),
        DateTimeDyField.data_source("Updated", "data.update_time"),
    ],
)

feature_settings = ItemDynamicLayout.set_fields(
    "Feature Settings",
    fields=[
        EnumDyField.data_source(
            "Split Health Checks",
            "data.feature_settings.splitHealthChecks",
            default_badge={"indigo.500": ["true"], "coral.600": ["false"]},
        ),
        EnumDyField.data_source(
            "Use Container Optimized OS",
            "data.feature_settings.useContainerOptimizedOs",
            default_badge={"indigo.500": ["true"], "coral.600": ["false"]},
        ),
    ],
)

iap_settings = ItemDynamicLayout.set_fields(
    "IAP Settings",
    fields=[
        EnumDyField.data_source(
            "Enabled",
            "data.iap.enabled",
            default_badge={"indigo.500": ["true"], "coral.600": ["false"]},
        ),
        TextDyField.data_source("OAuth2 Client ID", "data.iap.oauth2ClientId"),
        TextDyField.data_source("OAuth2 Client Secret", "data.iap.oauth2ClientSecret"),
    ],
)

dispatch_rules = TableDynamicLayout.set_fields(
    "Dispatch Rules",
    root_path="data.dispatch_rules",
    fields=[
        TextDyField.data_source("Domain", "domain"),
        TextDyField.data_source("Path", "path"),
        TextDyField.data_source("Service", "service"),
    ],
)

app_engine_application_meta = CloudServiceMeta.set_layouts(
    [app_engine_application, feature_settings, iap_settings, dispatch_rules]
)


class AppEngineResource(CloudServiceResource):
    cloud_service_group = StringType(default="AppEngine")


class AppEngineApplicationResource(AppEngineResource):
    cloud_service_type = StringType(default="Application")
    data = ModelType(AppEngineApplication)
    _metadata = ModelType(
        CloudServiceMeta, default=app_engine_application_meta, serialized_name="metadata"
    )


class AppEngineApplicationResponse(CloudServiceResponse):
    resource = PolyModelType(AppEngineApplicationResource)
