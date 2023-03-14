import math
from schematics import Model
from schematics.types import ModelType, StringType, PolyModelType, DictType, BooleanType, BaseType

from spaceone.inventory.libs.schema.metadata.dynamic_search import BaseDynamicSearch

BACKGROUND_COLORS = [
    'black', 'white',
    'gray', 'gray.100', 'gray.200', 'gray.300', 'gray.400', 'gray.500', 'gray.600', 'gray.700', 'gray.800', 'gray.900',
    'red', 'red.100', 'red.200', 'red.300', 'red.400', 'red.500', 'red.600', 'red.700', 'red.800', 'red.900',
    'coral', 'coral.100', 'coral.200', 'coral.300', 'coral.400', 'coral.500', 'coral.600', 'coral.700', 'coral.800',
    'coral.900',
    'yellow', 'yellow.100', 'yellow.200', 'yellow.300', 'yellow.400', 'yellow.500', 'yellow.600', 'yellow.700',
    'yellow.800', 'yellow.900',
    'green', 'green.100', 'green.200', 'green.300', 'green.400', 'green.500', 'green.600', 'green.700', 'green.800',
    'green.900',
    'blue', 'blue.100', 'blue.200', 'blue.300', 'blue.400', 'blue.500', 'blue.600', 'blue.700', 'blue.800', 'blue.900',
    'violet', 'violet.100', 'violet.200', 'violet.300', 'violet.400', 'violet.500', 'violet.600', 'violet.700',
    'violet.800', 'violet.900',
    'peacock', 'peacock.100', 'peacock.200', 'peacock.300', 'peacock.400', 'peacock.500', 'peacock.600', 'peacock.700',
    'peacock.800', 'peacock.900',
    'indigo', 'indigo.100', 'indigo.200', 'indigo.300', 'indigo.400', 'indigo.500', 'indigo.600', 'indigo.700',
    'indigo.800', 'indigo.900',
]

TYPE_BADGE = ['primary', 'indigo.500', 'coral.600', 'peacock.500', 'green.500', 'gray.500', 'red.500']


class FieldReference(Model):
    resource_type = StringType()
    reference_key = StringType(serialize_when_none=False)


class Icon(Model):
    image = StringType(serialize_when_none=False)
    color = StringType(default='green', choices=BACKGROUND_COLORS)


class BaseField(Model):
    type = StringType(choices=["text", "state", "badge", "list", "dict",
                               "datetime", "image", "enum", "progress", "size"],
                      serialize_when_none=False)
    options = PolyModelType([Model, DictType(PolyModelType(Model))], serialize_when_none=False)


class FieldViewOption(Model):
    link = StringType(serialize_when_none=False)
    variables = StringType(serialize_when_none=False)
    sortable = BooleanType(serialize_when_none=False)
    sort_key = StringType(serialize_when_none=False)
    translation_id = StringType(serialize_when_none=False)
    default = StringType(serialize_when_none=False)
    is_optional = BooleanType(serialize_when_none=False)
    postfix = StringType(serialize_when_none=False)
    prefix = StringType(serialize_when_none=False)
    field_description = StringType(serialize_when_none=False)


class BaseDynamicField(BaseField):
    name = StringType()
    key = StringType()
    reference = ModelType(FieldReference, serialize_when_none=False)

    @classmethod
    def data_source(cls, name, key, **kwargs):
        return cls({'key': key, 'name': name, **kwargs})


class TextDyFieldOptions(FieldViewOption):
    pass


class BadgeDyFieldOptions(FieldViewOption):
    text_color = StringType(serialize_when_none=False)
    shape = StringType(serialize_when_none=False, choices=['SQUARE', 'ROUND'])
    outline_color = StringType(serialize_when_none=False, choices=BACKGROUND_COLORS)
    background_color = StringType(serialize_when_none=False, choices=BACKGROUND_COLORS)


class StateDyFieldOptions(FieldViewOption):
    text_color = StringType(serialize_when_none=False)
    icon = ModelType(Icon, serialize_when_none=False)


class ImageDyFieldOptions(FieldViewOption):
    image_url = StringType(default='')
    width = StringType(serialize_when_none=False)
    height = StringType(serialize_when_none=False)


class DateTimeDyFieldOptions(FieldViewOption):
    source_type = StringType(default='timestamp', choices=['iso8601', 'timestamp'])
    source_format = StringType(serialize_when_none=False)
    display_format = StringType(serialize_when_none=False)


class ProgressFieldOptions(FieldViewOption):
    unit = StringType(serialize_when_none=False)


class SizeFieldOptions(FieldViewOption):
    display_unit = StringType(serialize_when_none=False, choices=('BYTES', 'KB', 'MB', 'GB', 'TB', 'PB'))
    source_unit = StringType(serialize_when_none=False, choices=('BYTES', 'KB', 'MB', 'GB', 'TB', 'PB'))


class TextDyField(BaseDynamicField):
    type = StringType(default="text")
    options = PolyModelType(TextDyFieldOptions, serialize_when_none=False)

    @classmethod
    def data_source(cls, name, key, **kwargs):
        _data_source = {'key': key, 'name': name}
        if 'options' in kwargs:
            _data_source.update({'options': TextDyFieldOptions(kwargs.get('options'))})

        if 'reference' in kwargs:
            _data_source.update({'reference': kwargs.get('reference')})

        return cls(_data_source)


class StateDyField(BaseDynamicField):
    type = StringType(default="state")
    options = PolyModelType(StateDyFieldOptions, serialize_when_none=False)

    @classmethod
    def data_source(cls, name, key, **kwargs):
        _data_source = {'key': key, 'name': name}
        if 'options' in kwargs:
            _data_source.update({'options': StateDyFieldOptions(kwargs.get('options'))})

        if 'reference' in kwargs:
            _data_source.update({'reference': kwargs.get('reference')})

        return cls(_data_source)


class BadgeDyField(BaseDynamicField):
    type = StringType(default="badge")
    options = PolyModelType(BadgeDyFieldOptions, serialize_when_none=False)

    @classmethod
    def data_source(cls, name, key, **kwargs):
        _data_source = {'key': key, 'name': name}

        if 'options' in kwargs:
            _data_source.update({'options': BadgeDyFieldOptions(kwargs.get('options'))})
        else:
            _data_source.update({'options': BadgeDyFieldOptions({'background_color': 'gray.200',
                                                                 'text_color': 'gray.900'})})

        if 'reference' in kwargs:
            _data_source.update({'reference': kwargs.get('reference')})

        return cls(_data_source)


class ImageDyField(BaseDynamicField):
    type = StringType(default="image")
    options = PolyModelType(ImageDyFieldOptions, serialize_when_none=False)

    @classmethod
    def data_source(cls, name, key, **kwargs):
        _data_source = {'key': key, 'name': name}
        if 'options' in kwargs:
            _data_source.update({'options': ImageDyFieldOptions(kwargs.get('options'))})

        if 'reference' in kwargs:
            _data_source.update({'reference': kwargs.get('reference')})

        return cls(_data_source)


class DateTimeDyField(BaseDynamicField):
    type = StringType(default="datetime")
    options = PolyModelType(DateTimeDyFieldOptions, serialize_when_none=False)

    @classmethod
    def data_source(cls, name, key, **kwargs):
        _data_source = {'key': key, 'name': name}
        if 'options' in kwargs:
            _data_source.update({'options': DateTimeDyFieldOptions(kwargs.get('options'))})

        if 'reference' in kwargs:
            _data_source.update({'reference': kwargs.get('reference')})

        return cls(_data_source)


class DictDyField(BaseDynamicField):
    type = StringType(default="dict")
    options = PolyModelType(FieldViewOption, serialize_when_none=False)


class StateItemDyField(BaseField):
    type = StringType(default="state")
    options = PolyModelType(StateDyFieldOptions, serialize_when_none=False)

    @classmethod
    def set(cls, options):
        return cls({'options': StateDyFieldOptions(options)})


class BadgeItemDyField(BaseField):
    type = StringType(default="badge")
    options = PolyModelType(BadgeDyFieldOptions, serialize_when_none=False)

    @classmethod
    def set(cls, options):
        return cls({'options': BadgeDyFieldOptions(options)})


class ImageItemDyField(BaseField):
    type = StringType(default="image")
    options = PolyModelType(ImageDyFieldOptions, serialize_when_none=False)

    @classmethod
    def set(cls, options):
        return cls({'options': ImageDyFieldOptions(options)})


class DatetimeItemDyField(BaseField):
    type = StringType(default="datetime")
    options = PolyModelType(DateTimeDyFieldOptions, serialize_when_none=False)

    @classmethod
    def set(cls, options):
        return cls({'options': DateTimeDyFieldOptions(options)})


class ListDyFieldOptions(FieldViewOption):
    item = PolyModelType([BadgeItemDyField, StateDyField, DateTimeDyField, DictDyField], serialize_when_none=False)
    sub_key = StringType(serialize_when_none=False)
    delimiter = StringType(serialize_when_none=False)


class ListDyField(BaseDynamicField):
    type = StringType(default="list")
    options = PolyModelType(ListDyFieldOptions, serialize_when_none=False)

    @classmethod
    def data_source(cls, name, key, **kwargs):
        _data_source = {'key': key, 'name': name}
        if 'default_badge' in kwargs:
            _default_badge = kwargs.get('default_badge')
            _list_options = {'delimiter': '  '}

            if 'type' in _default_badge and _default_badge.get('type') == 'outline':
                _list_options.update({'item': BadgeItemDyField.set({'outline_color': 'violet.500'})})
            elif 'type' in _default_badge and _default_badge.get('type') == 'inline':
                _list_options.update({'item': BadgeItemDyField.set({'background_color': 'violet.500'})})

            if 'sub_key' in _default_badge:
                _list_options.update({'sub_key': _default_badge.get('sub_key')})

            if 'delimiter' in _default_badge:
                _list_options.update({'delimiter': _default_badge.get('delimiter')})

            _data_source.update({'options': ListDyFieldOptions(_list_options)})

        if 'options' in kwargs:
            _data_source.update({'options': ListDyFieldOptions(kwargs.get('options'))})

        if 'reference' in kwargs:
            _data_source.update({'reference': kwargs.get('reference')})

        return cls(_data_source)


class EnumDyField(BaseDynamicField):
    type = StringType(default="enum")
    options = DictType(PolyModelType([StateItemDyField, BadgeItemDyField, ImageItemDyField, DatetimeItemDyField]),
                       serialize_when_none=False,
                       default={})

    @classmethod
    def data_source(cls, name, key, **kwargs):
        _data_source = {'key': key, 'name': name}
        _default_badge = kwargs.get('default_badge', {})
        _default_state = kwargs.get('default_state', {})
        _default_outline_badge = kwargs.get('default_outline_badge', [])

        _options_dic = {}

        for _key in _default_outline_badge:
            _round_index = len(TYPE_BADGE)
            _index = _default_outline_badge.index(_key)
            _num = math.floor(_index / len(TYPE_BADGE))

            if _num > 0:
                _round_index = len(TYPE_BADGE) * _num

            if _round_index - 1 < _index:
                _index = _index - _round_index

            _options_dic[_key] = BadgeItemDyField.set({'outline_color': TYPE_BADGE[_index]})

        for _key in _default_badge:
            for _badge in _default_badge[_key]:
                _options_dic[_badge] = BadgeItemDyField.set({'background_color': _key})

        for _key in _default_state:
            for _state in _default_state[_key]:
                _state_options = {'icon': {'color': 'gray.400'}}

                if _key == 'safe':
                    _state_options = {'icon': {'color': 'green.500'}}
                elif _key == 'disable':
                    _state_options.update({'text_color': 'gray.400'})
                elif _key == 'warning':
                    _state_options = {'icon': {'color': 'yellow.500'}}
                elif _key == 'available':
                    _state_options = {'icon': {'color': 'blue.400'}}
                elif _key == 'alert':
                    _state_options = {'text_color': 'red.500', 'icon': {'color': 'red.500'}}

                _options_dic[_state] = StateItemDyField.set(_state_options)

        _data_source.update({'options': _options_dic})

        if 'options' in kwargs:
            _data_source.update({'options': kwargs.get('options')})

        if 'reference' in kwargs:
            _data_source.update({'reference': kwargs.get('reference')})

        return cls(_data_source)


class ProgressField(BaseDynamicField):
    type = StringType(default="progress")
    options = PolyModelType(ProgressFieldOptions, serialize_when_none=False, )

    @classmethod
    def data_source(cls, name, key, **kwargs):
        _data_source = {'key': key, 'name': name}

        if 'options' in kwargs:
            _data_source.update({'options': kwargs.get('options')})

        return cls(_data_source)


class SizeField(BaseDynamicField):
    type = StringType(default="size")
    options = PolyModelType(SizeFieldOptions, serialize_when_none=False)

    @classmethod
    def data_source(cls, name, key, **kwargs):
        _data_source = {'key': key, 'name': name}

        if 'options' in kwargs:
            _data_source.update({'options': kwargs.get('options')})

        return cls(_data_source)


class SearchEnumField(Model):
    label = StringType(serialize_when_none=False)
    icon = ModelType(Icon, serialize_when_none=False)

    @classmethod
    def set_field(cls, label=None, icon=None):
        return_dic = {}

        if label is not None:
            return_dic.update({'label': label})

        if icon is not None:
            return_dic.update({'icon': Icon(icon)})

        return cls(return_dic)


class SearchField(BaseDynamicSearch):
    enums = DictType(ModelType(SearchEnumField), serialize_when_none=False)
    reference = StringType(serialize_when_none=False)

    @classmethod
    def set(cls, name='', key='', data_type=None, enums=None, reference=None):
        return_dic = {
            'name': name,
            'key': key
        }

        if data_type is not None:
            return_dic.update({'data_type': data_type})

        if reference is not None:
            return_dic.update({'reference': reference})

        if enums is not None:
            convert_enums = {}
            for enum_key in enums:
                enum_v = enums[enum_key]
                convert_enums[enum_key] = SearchEnumField.set_field(**enum_v)

            return_dic.update({
                'enums': convert_enums
            })

        return cls(return_dic)


class MoreLayoutField(Model):
    name = StringType(default='')
    type = StringType(default="popup")
    options = DictType(BaseType, serialize_when_none=False)


class MoreFieldOptions(FieldViewOption):
    sub_key = StringType(serialize_when_none=False)
    layout = PolyModelType(MoreLayoutField, serialize_when_none=False)


class MoreField(BaseDynamicField):
    type = StringType(default="more")
    options = PolyModelType(MoreFieldOptions, serialize_when_none=False)

    @classmethod
    def data_source(cls, name, key, **kwargs):
        _data_source = {'key': key, 'name': name}

        if 'options' in kwargs:
            _data_source.update({'options': kwargs.get('options')})

        return cls(_data_source)
