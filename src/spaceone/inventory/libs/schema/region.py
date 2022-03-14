from schematics import Model
from schematics.types import ListType, StringType, PolyModelType, DictType
from .base import BaseResponse


class RegionResource(Model):
    name = StringType(default="")
    region_code = StringType()
    provider = StringType(default="google_cloud")
    tags = DictType(StringType)


class RegionResponse(BaseResponse):
    resource_type = StringType(default='inventory.Region')
    match_rules = DictType(ListType(StringType), default={'1': ['region_code', 'provider']})
    resource = PolyModelType(RegionResource)