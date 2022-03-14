from schematics import Model
from schematics.types import ListType, StringType, PolyModelType, DictType, ModelType

from spaceone.inventory.libs.schema.metadata.dynamic_layout import BaseLayoutField
from spaceone.inventory.libs.schema.metadata.dynamic_search import BaseDynamicSearch
from spaceone.inventory.libs.schema.metadata.dynamic_widget import BaseDynamicWidget


class MetaDataViewSubData(Model):
    layouts = ListType(PolyModelType(BaseLayoutField))


class MetaDataViewTable(Model):
    layout = PolyModelType(BaseLayoutField)


class MetaDataView(Model):
    table = PolyModelType(MetaDataViewTable, serialize_when_none=False)
    sub_data = PolyModelType(MetaDataViewSubData, serialize_when_none=False)
    search = ListType(PolyModelType(BaseDynamicSearch), serialize_when_none=False)
    widget = ListType(PolyModelType(BaseDynamicWidget), serialize_when_none=False)


class BaseMetaData(Model):
    view = ModelType(MetaDataView)


class BaseResponse(Model):
    state = StringType(default='SUCCESS', choices=('SUCCESS', 'FAILURE', 'TIMEOUT'))
    message = StringType(default='')
    resource_type = StringType(required=True)
    match_rules = DictType(ListType(StringType), serialize_when_none=False)
    resource = PolyModelType(Model, default={})


class ReferenceModel(Model):
    class Option:
        serialize_when_none = False
    resource_id = StringType(required=False, serialize_when_none=False)
    external_link = StringType(required=False, serialize_when_none=False)


'''
Schematic 방식으로 ServerMetadata를 처리하고 난 후에는 삭제 해도 됨
일시적으로 넣어둠
'''
class ServerMetadata(Model):
    view = ModelType(MetaDataView)

    @classmethod
    def set_layouts(cls, layouts=[]):
        sub_data = MetaDataViewSubData({'layouts': layouts})
        return cls({'view': MetaDataView({'sub_data': sub_data})})
