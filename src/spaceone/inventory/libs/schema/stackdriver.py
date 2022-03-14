from schematics import Model
from schematics.types import ListType, StringType, ModelType


class StackDriverFilters(Model):
    key = StringType()
    value = StringType()


class StackDriverModel(Model):
    class Option:
        serialize_when_none = False

    type = StringType()
    filters = ListType(ModelType(StackDriverFilters), default=[])
