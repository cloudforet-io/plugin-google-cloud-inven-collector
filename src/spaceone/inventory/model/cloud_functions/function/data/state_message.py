from schematics import Model
from schematics.types import StringType

__all__ = ['StateMessage']


class StateMessage(Model):
    severity = StringType(choices=('SEVERITY_UNSPECIFIED', 'ERROR', 'WARNING', 'INFO'), serialize_when_none=False)
    type = StringType(serialize_when_none=False)
    message = StringType(serialize_when_none=False)
