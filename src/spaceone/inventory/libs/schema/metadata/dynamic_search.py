from schematics import Model
from schematics.types import StringType


class BaseDynamicSearch(Model):
    name = StringType()
    key = StringType()
    data_type = StringType(choices=['string', 'integer', 'float', 'boolean', 'datetime'],
                           serialize_when_none=False)

