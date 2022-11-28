from schematics import Model
from schematics.types import StringType, PolyModelType, ListType
from spaceone.inventory.libs.schema.metadata.dynamic_field import BaseDynamicField, TextDyField, MoreField


class LayoutOptions(Model):
    class Options:
        serialize_when_none = False

    root_path = StringType(serialize_when_none=False)


class BaseLayoutField(Model):
    @staticmethod
    def _set_fields(fields=[], **kwargs):
        _options = {'fields': fields}
        for k, v in kwargs.items():
            if v is not None:
                _options[k] = v
        return _options

    name = StringType(default='')
    type = StringType(default="item",
                      choices=("item", "table", "query-search-table", "simple-table", "list", "raw", "html"))
    options = PolyModelType(LayoutOptions, serialize_when_none=False)


class ItemLayoutOption(LayoutOptions):
    fields = ListType(PolyModelType(BaseDynamicField))


class SimpleTableLayoutOption(LayoutOptions):
    fields = ListType(PolyModelType(BaseDynamicField))


class TableLayoutOption(LayoutOptions):
    fields = ListType(PolyModelType(BaseDynamicField))


class QuerySearchTableLayoutOption(LayoutOptions):
    fields = ListType(PolyModelType(BaseDynamicField))


class RawLayoutOption(LayoutOptions):
    class Options:
        serialize_when_none = False


class HTMLLayoutOption(LayoutOptions):
    class Options:
        serialize_when_none = False


class ListLayoutOption(LayoutOptions):
    layouts = ListType(PolyModelType(BaseLayoutField))


class ItemDynamicLayout(BaseLayoutField):
    type = StringType(default='item')
    options = PolyModelType(ItemLayoutOption)

    @classmethod
    def set(cls, name='', root_path=''):
        return cls({'name': name, 'options': ItemLayoutOption({'root_path': root_path})})

    @classmethod
    def set_fields(cls, name='', root_path=None, fields=[]):
        _options = cls._set_fields(fields, root_path=root_path)
        return cls({'name': name, 'options': ItemLayoutOption(_options)})


class TableDynamicLayout(BaseLayoutField):
    type = StringType(default='table')
    options = PolyModelType(TableLayoutOption)

    @classmethod
    def set(cls, name='', root_path=''):
        return cls(name=name, root_path=root_path, options=TableLayoutOption({'root_path': root_path}))

    @classmethod
    def set_fields(cls, name='', root_path=None, fields=[]):
        _options = cls._set_fields(fields, root_path=root_path)
        return cls({'name': name, 'options': TableLayoutOption(_options)})


class QuerySearchTableDynamicLayout(BaseLayoutField):
    type = StringType(default='query-search-table')
    options = PolyModelType(QuerySearchTableLayoutOption)

    @classmethod
    def set(cls, name=''):
        return cls(name=name, options=QuerySearchTableLayoutOption())

    @classmethod
    def set_fields(cls, name='', fields=[]):
        _options = cls._set_fields(fields)
        return cls({'name': name, 'options': QuerySearchTableLayoutOption(_options)})


class SimpleTableDynamicLayout(BaseLayoutField):
    type = StringType(default='simple-table')
    options = PolyModelType(SimpleTableLayoutOption)

    @classmethod
    def set(cls, name='', root_path=''):
        return cls({'name': name, 'options': SimpleTableLayoutOption({'root_path': root_path})})

    @classmethod
    def set_fields(cls, name='', root_path=None, fields=[]):
        _options = cls._set_fields(fields, root_path=root_path)
        return cls({'name': name, 'options': SimpleTableLayoutOption(_options)})

    @classmethod
    def set_tags(cls, name='Tags', root_path='data.tags', fields=None):
        if fields is None:
            fields = [
                TextDyField.data_source('Key', 'key'),
                TextDyField.data_source('Value', 'value'),
            ]
        return cls.set_fields(name, root_path, fields)

    @classmethod
    def set_code_field(cls, name='Code sources', root_path='data.display.source_code', fields=None):
        if fields is None:
            fields = [
                TextDyField.data_source('File name', 'file_name'),
                MoreField.data_source('Source', 'output_display',
                                      options={
                                          'sub_key': 'content',
                                          'layout': {
                                              'name': 'Code',
                                              'type': 'popup',
                                              'options': {
                                                  'layout': {
                                                      'type': 'raw'
                                                  }
                                              }
                                          }
                                      })
            ]
        return cls.set_fields(name, root_path, fields)


class ListDynamicLayout(BaseLayoutField):
    type = StringType(default='list')
    options = PolyModelType(ListLayoutOption)

    @classmethod
    def set(cls, name='', layouts=[]):
        return cls(name=name, options=ListLayoutOption({'layouts': layouts}))

    @classmethod
    def set_layouts(cls, name='', layouts=[]):
        return cls({'name': name, 'options': ListLayoutOption({'layouts': layouts})})


class RawDynamicLayout(BaseLayoutField):
    type = StringType(default='raw')
    options = PolyModelType(RawLayoutOption)

    @classmethod
    def set(cls, name='', root_path=None):
        if root_path is None:
            _options = RawLayoutOption()
        else:
            _options = RawLayoutOption({'root_path': root_path})

        return cls({'name': name, 'options': _options})


class HTMLDynamicLayout(BaseLayoutField):
    type = StringType(default='html')
    options = PolyModelType(HTMLLayoutOption)

    @classmethod
    def set(cls, name='', root_path=None):
        if root_path is None:
            _options = HTMLLayoutOption()
        else:
            _options = HTMLLayoutOption({'root_path': root_path})

        return cls({'name': name, 'options': _options})
