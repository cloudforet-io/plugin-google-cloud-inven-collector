from schematics import Model
from schematics.types import ListType, StringType, PolyModelType, DictType, BooleanType
from spaceone.inventory.libs.schema.metadata.dynamic_layout import QuerySearchTableDynamicLayout
from .base import BaseMetaData, BaseResponse, MetaDataViewTable, MetaDataView


class CloudServiceTypeMeta(BaseMetaData):
    @classmethod
    def set_fields(cls, name='', fields=[]):
        _table = MetaDataViewTable({'layout': QuerySearchTableDynamicLayout.set_fields(name, fields)})
        return cls({'view': MetaDataView({'table': _table})})

    @classmethod
    def set_meta(cls, name='', fields=[], search=[], widget=[]):
        table_meta = MetaDataViewTable({'layout': QuerySearchTableDynamicLayout.set_fields(name, fields)})
        return cls({'view': MetaDataView({'table': table_meta, 'search': search, 'widget': widget})})


class CloudServiceTypeResource(Model):
    name = StringType()
    provider = StringType()
    group = StringType()
    _metadata = PolyModelType(CloudServiceTypeMeta, serialize_when_none=False, serialized_name='metadata')
    labels = ListType(StringType(), serialize_when_none=False)
    tags = DictType(StringType, serialize_when_none=False)
    is_primary = BooleanType(default=False)
    is_major = BooleanType(default=False)
    resource_type = StringType(default='inventory.CloudService')
    service_code = StringType(serialize_when_none=False)


class CloudServiceTypeResponse(BaseResponse):
    resource_type = StringType(default='inventory.CloudServiceType')
    match_rules = DictType(ListType(StringType), default={'1': ['name', 'group', 'provider']})
    resource = PolyModelType(CloudServiceTypeResource)


class CloudServiceTypeResourceResponse(BaseResponse):
    state = StringType(default='SUCCESS')
    resource_type = StringType(default='inventory.CloudServiceType')
    match_rules = DictType(ListType(StringType), default={'1': ['name', 'group', 'provider']})
    resource = PolyModelType(CloudServiceTypeResource)

