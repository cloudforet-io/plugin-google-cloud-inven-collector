from schematics import Model
from schematics.types import StringType, ListType, BooleanType, ModelType, PolyModelType, DictType
from .dynamic_field import TextDyField, StateDyField, BadgeDyField, ListDyField, DictDyField, DateTimeDyField, \
    ImageDyField, EnumDyField, SizeField, ProgressField

class BaseDynamicWidgetKeyFields(Model):
    key = StringType(serialize_when_none=False)
    name = StringType(serialize_when_none=False)


class BaseDynamicWidgetGroupCondition(Model):
    key = StringType(serialize_when_none=False)
    value = StringType(serialize_when_none=False)
    operator = StringType(serialize_when_none=False)


class BaseDynamicWidgetQueryAggregateUnwind(Model):
    path = StringType(serialize_when_none=False)


class BaseDynamicWidgetQueryAggregateGroupKeys(BaseDynamicWidgetKeyFields):
    date_format = StringType(serialize_when_none=False)


class BaseDynamicWidgetQueryAggregateGroupFields(Model):
    key = StringType(serialize_when_none=False)
    name = StringType(serialize_when_none=False)
    operator = StringType(serialize_when_none=False)
    _fields = ListType(ModelType(BaseDynamicWidgetKeyFields), serialize_when_none=False, serialized_name='fields')
    conditions = ListType(ModelType(BaseDynamicWidgetGroupCondition), serialize_when_none=False)


class BaseDynamicWidgetQueryAggregateGroup(Model):
    keys = ListType(ModelType(BaseDynamicWidgetQueryAggregateGroupKeys), serialize_when_none=False)
    _fields = ListType(ModelType(BaseDynamicWidgetQueryAggregateGroupFields), serialize_when_none=False, serialized_name='fields')


class BaseDynamicWidgetQueryAggregateCount(Model):
    name = StringType(serialize_when_none=False)


class BaseDynamicWidgetQueryAggregateSortKey(Model):
    key = StringType(serialize_when_none=False)
    desc = BooleanType(serialize_when_none=False)


class BaseDynamicWidgetQueryAggregateSort(Model):
    key = StringType(serialize_when_none=False)
    desc = BooleanType(serialize_when_none=False)
    keys = ListType(ModelType(BaseDynamicWidgetQueryAggregateSortKey), serialize_when_none=False)


class BaseDynamicWidgetQueryAggregateProjectField(Model):
    key = StringType(serialize_when_none=False)
    name = StringType(serialize_when_none=False)
    operator = StringType(serialize_when_none=False)


class BaseDynamicWidgetQueryAggregateProject(Model):
    _fields = ListType(ModelType(BaseDynamicWidgetQueryAggregateProjectField), serialize_when_none=False, serialized_name='fields')


class BaseDynamicWidgetQueryAggregate(Model):
    unwind = ModelType(BaseDynamicWidgetQueryAggregateUnwind, serialize_when_none=False)
    group = ModelType(BaseDynamicWidgetQueryAggregateGroup, serialize_when_none=False)
    count = ModelType(BaseDynamicWidgetQueryAggregateCount, serialize_when_none=False)
    sort = ModelType(BaseDynamicWidgetQueryAggregateSort, serialize_when_none=False)
    project = ModelType(BaseDynamicWidgetQueryAggregateProject, serialize_when_none=False)


class BaseDynamicWidgetQueryFilter(Model):
    key = StringType(serialize_when_none=False)
    # value = PolyModelType([StringType], serialize_when_none=False)
    value = StringType(serialize_when_none=False)
    operator = StringType(serialize_when_none=False)


class BaseDynamicWidgetQuery(Model):
    aggregate = ListType(ModelType(BaseDynamicWidgetQueryAggregate), serialize_when_none=False)
    filter = ListType(ModelType(BaseDynamicWidgetQueryFilter), serialize_when_none=False)


class BaseDynamicWidgetOptions(Model):
    value_options = PolyModelType([TextDyField, StateDyField, BadgeDyField, ListDyField, DictDyField, DateTimeDyField,
                                   ImageDyField, EnumDyField, SizeField, ProgressField], serialize_when_none=False)
    name_options = PolyModelType([TextDyField, StateDyField, BadgeDyField, ListDyField, DictDyField, DateTimeDyField,
                                  ImageDyField, EnumDyField, SizeField, ProgressField], serialize_when_none=False)
    chart_type = StringType(choices=('COLUMN', 'DONUT', 'TREEMAP'), serialize_when_none=False)


class BaseDynamicWidget(Model):
    name = StringType(serialize_when_none=False)
    type = StringType(choices=('card', 'chart'), serialize_when_none=False)
    options = ModelType(BaseDynamicWidgetOptions, serialize_when_none=False)
    query = ModelType(BaseDynamicWidgetQuery, serialize_when_none=False)

    @classmethod
    def set(cls, cloud_service_group, cloud_service_type, name, query, options={}):
        # Query : aggregate
        query_aggrs = []
        for _aggregate in query.get('aggregate', []):
            _aggr_dict = {}
            if 'unwind' in _aggregate:
                _aggr_dict['unwind'] = BaseDynamicWidgetQueryAggregateUnwind(_aggregate['unwind'])

            if 'group' in _aggregate:
                _aggr_group = _aggregate['group']
                _aggr_group_keys = [BaseDynamicWidgetQueryAggregateGroupKeys(_aggr_group_key)
                                    for _aggr_group_key in _aggr_group.get('keys', [])]

                _aggr_group_fields = []
                for _aggr_group_field in _aggr_group.get('fields', []):
                    _aggr_group_field_fields = [BaseDynamicWidgetKeyFields(_aggr_group_field_fields) for
                                                _aggr_group_field_fields in _aggr_group_field.get('fields', [])]

                    if _aggr_group_field_fields:
                        _aggr_group_field['fields'] = _aggr_group_field_fields

                    if 'condition' in _aggr_group_field:
                        _aggr_group_field['condition'] = BaseDynamicWidgetGroupCondition(_aggr_group_field['condition'])

                    _aggr_group_fields.append(BaseDynamicWidgetQueryAggregateGroupFields(_aggr_group_field))

                if _aggr_group_keys:
                    _aggr_group['keys'] = _aggr_group_keys

                if _aggr_group_fields:
                    _aggr_group['fields'] = _aggr_group_fields

                _aggr_dict['group'] = BaseDynamicWidgetQueryAggregateGroup(_aggr_group)

            if 'count' in _aggregate:
                _aggr_dict['count'] = BaseDynamicWidgetQueryAggregateCount(_aggregate['count'])

            if 'sort' in _aggregate:
                _aggr_sort = _aggregate['sort']

                _aggr_sort_keys = [BaseDynamicWidgetQueryAggregateSortKey(_aggr_sort_key)
                                   for _aggr_sort_key in _aggr_sort.get('keys', [])]

                if _aggr_sort_keys:
                    _aggr_sort['keys'] = _aggr_sort_keys

                _aggr_dict['sort'] = BaseDynamicWidgetQueryAggregateSort(_aggr_sort)

            if 'project' in _aggregate:
                _aggr_project = _aggregate['project']
                _aggr_project_fields = [BaseDynamicWidgetQueryAggregateProjectField(_aggr_project_field)
                                        for _aggr_project_field in _aggr_project.get('fields', [])]

                _aggr_dict['project'] = BaseDynamicWidgetQueryAggregateProject({'fields': _aggr_project_fields})

            query_aggrs.append(BaseDynamicWidgetQueryAggregate(_aggr_dict))

        query['aggregate'] = query_aggrs

        # Query : filter
        filter = [{'key': 'provider', 'value': 'google_cloud', 'operator': 'eq'},
                  {'key': 'cloud_service_group', 'value': cloud_service_group, 'operator': 'eq'},
                  {'key': 'cloud_service_type', 'value': cloud_service_type, 'operator': 'eq'}]

        if 'filter' in query:
            query['filter'].extend(filter)
        else:
            query.update({'filter': filter})

        query['filter'] = [BaseDynamicWidgetQueryFilter(_filter) for _filter in query['filter']]

        if options:
            field_type_maps = {
                'text': TextDyField,
                'state': StateDyField,
                'badge': BadgeDyField,
                'list': ListDyField,
                'dict': DictDyField,
                'datetime': DateTimeDyField,
                'image': ImageDyField,
                'enum': EnumDyField,
                'size': SizeField,
                'progress': ProgressField
            }

            if 'name_options' in options:
                _name_options = options['name_options']
                _type = _name_options.get('type', 'text')

                if _type in field_type_maps:
                    options['name_options'] = field_type_maps[_type](_name_options)

            if 'value_options' in options:
                _value_options = options['value_options']
                _type = _value_options.get('type', 'text')

                if _type in field_type_maps:
                    options['value_options'] = field_type_maps[_type](_value_options)

        _dic = {
            'name': name,
            'query': BaseDynamicWidgetQuery(query),
            'options': BaseDynamicWidgetOptions(options)
        }

        return cls(_dic)


class CardWidget(BaseDynamicWidget):
    type = StringType(default='card')


class ChartWidget(BaseDynamicWidget):
    type = StringType(default='chart')