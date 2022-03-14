from schematics.types import ModelType, StringType, PolyModelType

from spaceone.inventory.model.bigquery.data import *
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, DateTimeDyField, EnumDyField, \
    ListDyField, SizeField
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, TableDynamicLayout, \
    ListDynamicLayout, SimpleTableDynamicLayout
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta

'''
INSTANCE
'''

# TAB - Bucket
dataset_details_meta = ItemDynamicLayout.set_fields('Information', fields=[
    TextDyField.data_source('ID', 'data.id'),
    TextDyField.data_source('Name', 'data.name'),
    TextDyField.data_source('Location', 'data.location'),
    TextDyField.data_source('Default Partition Expires', 'data.default_partition_expiration_ms_display'),
    TextDyField.data_source('Default Table Expires', 'data.default_table_expiration_ms_display'),
    EnumDyField.data_source('Visible on Console', 'data.visible_on_console', default_badge={
        'indigo.500': ['true'], 'coral.600': ['false']
    }),
    DateTimeDyField.data_source('Creation Time', 'data.creation_time'),
    DateTimeDyField.data_source('Last Modified Time', 'data.last_modified_time'),
])

access_table_meta = SimpleTableDynamicLayout.set_fields('Access',
                                                        root_path='data.access',
                                                        fields=[
                                                            TextDyField.data_source('Role', 'role'),
                                                            TextDyField.data_source('Special Group', 'special_group'),
                                                            TextDyField.data_source('User by E-mail', 'user_by_email')
                                                        ])

workspace_dataset_meta = ListDynamicLayout.set_layouts('Dataset Details', layouts=[dataset_details_meta,
                                                                                   access_table_meta])


workspace_matching_project_meta = TableDynamicLayout.set_fields('Project', root_path='data.matching_projects', fields=[
    TextDyField.data_source('ID', 'id'),
    TextDyField.data_source('Numeric Id', 'numeric_id'),
    TextDyField.data_source('kind', 'kind'),
    TextDyField.data_source('Friendly Name', 'friendly_name')
])


workspace_table_meta = TableDynamicLayout.set_fields('Tables', root_path='data.tables', fields=[
    TextDyField.data_source('ID', 'id'),
    TextDyField.data_source('Name', 'table_reference.table_id'),
    TextDyField.data_source('Type', 'type'),
    TextDyField.data_source('Dataset', 'table_reference.dataset_id'),
    TextDyField.data_source('Number of Rows', 'num_rows'),
    DateTimeDyField.data_source('Creation Time', 'creation_time'),
    DateTimeDyField.data_source('Last Modified Time', 'last_modified_time'),
    DateTimeDyField.data_source('Expiration Time', 'expiration_time'),
])

workspace_table_schema_meta = TableDynamicLayout.set_fields('Table Schema', root_path='data.table_schemas', fields=[
    TextDyField.data_source('Table Name', 'table_id'),
    TextDyField.data_source('Column Name', 'name'),
    TextDyField.data_source('Column Type', 'type'),
    TextDyField.data_source('Column Mode', 'mode'),
])


workspace_labels_meta = TableDynamicLayout.set_fields('Labels', root_path='data.labels', fields=[
    TextDyField.data_source('Key', 'key'),
    TextDyField.data_source('Value', 'value'),
])

big_query_workspace_meta = CloudServiceMeta.set_layouts([workspace_dataset_meta,
                                                       workspace_table_meta,
                                                       workspace_table_schema_meta,
                                                       workspace_matching_project_meta,
                                                       workspace_labels_meta])


class BigQueryGroupResource(CloudServiceResource):
    cloud_service_group = StringType(default='BigQuery')


class SQLWorkSpaceResource(BigQueryGroupResource):
    cloud_service_type = StringType(default='SQLWorkspace')
    data = ModelType(BigQueryWorkSpace)
    _metadata = ModelType(CloudServiceMeta, default=big_query_workspace_meta, serialized_name='metadata')


class SQLWorkSpaceResponse(CloudServiceResponse):
    resource = PolyModelType(SQLWorkSpaceResource)
