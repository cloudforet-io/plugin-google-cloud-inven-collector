from schematics import Model
from schematics.types import StringType, ListType


class GoogleCloudMonitoringModel(Model):
    name = StringType(serialize_when_none=False)
    filters = ListType(StringType(serialize_when_none=False), default=[])
