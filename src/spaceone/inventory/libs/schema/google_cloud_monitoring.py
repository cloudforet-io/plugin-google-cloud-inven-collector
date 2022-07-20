from schematics import Model
from schematics.types import StringType, ListType, ModelType


class GoogleCloudMonitoringFilterLabel(Model):
    key = StringType(serialize_when_none=False)
    value = StringType(serialize_when_none=False)


class GoogleCloudMonitoringFilter(Model):
    metric_type = StringType(serialize_when_none=False)
    labels = ListType(ModelType(GoogleCloudMonitoringFilterLabel, serialize_when_none=False), default=[])


class GoogleCloudMonitoringModel(Model):
    name = StringType(serialize_when_none=False)
    filters = ListType(ModelType(GoogleCloudMonitoringFilter, serialize_when_none=False), default=[])
