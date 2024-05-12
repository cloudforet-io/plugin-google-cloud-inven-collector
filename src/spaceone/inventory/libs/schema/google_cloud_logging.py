from schematics import Model
from schematics.types import StringType, ListType, ModelType


class GoogleCloudLoggingFilterLabel(Model):
    key = StringType(serialize_when_none=False)
    value = StringType(serialize_when_none=False)


class GoogleCloudMonitoringFilter(Model):
    resource_type = StringType(serialize_when_none=False)
    labels = ListType(
        ModelType(GoogleCloudLoggingFilterLabel, serialize_when_none=False), default=[]
    )


class GoogleCloudLoggingModel(Model):
    name = StringType(serialize_when_none=False)
    resource_id = StringType(serialize_when_none=False)
    filters = ListType(
        ModelType(GoogleCloudMonitoringFilter, serialize_when_none=False), default=[]
    )
