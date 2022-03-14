from schematics.types import ModelType, StringType, PolyModelType

from spaceone.inventory.model.cloud_sql.data import Instance
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, EnumDyField, ListDyField, DateTimeDyField
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, TableDynamicLayout
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta

'''
SQL INSTANCE
'''
# TAB - Instance
sql_meta_instance = ItemDynamicLayout.set_fields('Instance', fields=[
    TextDyField.data_source('Name', 'data.name'),
    EnumDyField.data_source('State', 'data.display_state', default_state={
        'safe': ['RUNNING'],
        'disable': ['UNKNOWN', 'ON-DEMAND'],
        'alert': ['STOPPED'],
    }),
    TextDyField.data_source('Type', 'data.database_version'),
    TextDyField.data_source('Project', 'data.project'),
    ListDyField.data_source('Public IP Address', 'data.ip_addresses', default_badge={'type': 'outline',
                                                                                     'sub_key': 'ip_address',
                                                                                     'delimiter': '<br>'}),
    TextDyField.data_source('Connection name', 'data.connection_name'),
    TextDyField.data_source('Location', 'data.gce_zone'),
    TextDyField.data_source('Service Account', 'data.service_account_email_address'),
])

# TAB - Configuration
sql_meta_configuration = ItemDynamicLayout.set_fields('Configuration', fields=[
    EnumDyField.data_source('Auto Storage Increased', 'data.settings.storage_auto_resize', default_badge={
        'indigo.500': ['true'], 'coral.600': ['false']
    }),
    TextDyField.data_source('Auto Storage Increased Limit Size (GB)', 'data.settings.storage_auto_resize_limit'),
    EnumDyField.data_source('Point-in-time recovery', 'data.settings.storage_auto_resize', default_badge={

    }),
    EnumDyField.data_source('Availability Type', 'data.settings.availability_type',
                            default_outline_badge=['ZONAL', 'REGIONAL', 'SQL_AVAILABILITY_TYPE_UNSPECIFIED']),
])

# TAB - Connections
sql_meta_connection = ItemDynamicLayout.set_fields('Connection', fields=[
    TextDyField.data_source('Connection name', 'data.connection_name'),
    ListDyField.data_source('IP Address Type', 'data.ip_addresses', default_badge={'type': 'outline',
                                                                                   'sub_key': 'type',
                                                                                   'delimiter': '<br>'}),
    ListDyField.data_source('Public IP Address', 'data.ip_addresses', default_badge={'type': 'outline',
                                                                                     'sub_key': 'ip_address',
                                                                                     'delimiter': '<br>'}),
    DateTimeDyField.data_source('SSL certificates Creation Time', 'data.server_ca_cert.create_time'),
    DateTimeDyField.data_source('SSL certificates Expiration Time', 'data.server_ca_cert.expiration_time'),
])

# TAB - Database
sql_meta_database = TableDynamicLayout.set_fields('Database', 'data.databases', fields=[
    TextDyField.data_source('Name', 'name'),
    TextDyField.data_source('charset', 'charset'),
    TextDyField.data_source('collation', 'collation'),
    TextDyField.data_source('Compatibility Level', 'sql_server_database_details.compatibility_level'),
    TextDyField.data_source('Recovery Model', 'sql_server_database_details.recovery_model'),
    TextDyField.data_source('Self Link', 'self_link'),
])

# TAB - User
sql_meta_user = TableDynamicLayout.set_fields('User', 'data.users', fields=[
    TextDyField.data_source('User Name', 'name'),
    EnumDyField.data_source('State', 'sql_server_user_details.disabled', default_badge={
        'indigo.500': ['true'], 'coral.600': ['false']
    }),
    TextDyField.data_source('Host', 'host'),
    ListDyField.data_source('Server Roles', 'sql_server_user_details.server_roles',
                            default_badge={'type': 'outline', 'delimiter': '<br>'}),
])

# TAB - Backup
sql_meta_backup = ItemDynamicLayout.set_fields('Backup', fields=[
    EnumDyField.data_source('Enabled', 'data.settings.backup_configuration.enabled', default_badge={
        'indigo.500': ['true'], 'coral.600': ['false']
    }),
    TextDyField.data_source('Location', 'data.settings.backup_configuration.location'),
    TextDyField.data_source('Start Time', 'data.settings.backup_configuration.start_time'),
    EnumDyField.data_source('Binary Log Enabled', 'data.settings.backup_configuration.binary_log_enabled',
                            default_badge={'indigo.500': ['true'], 'coral.600': ['false']}),
    EnumDyField.data_source('Replication Log Archiving Enabled',
                            'data.settings.backup_configuration.replication_log_archiving_enabled',
                            default_badge={'indigo.500': ['true'], 'coral.600': ['false']}),
    EnumDyField.data_source('Point In Time Recovery Enabled',
                            'data.settings.backup_configuration.point_in_time_recovery_enabled',
                            default_badge={'indigo.500': ['true'], 'coral.600': ['false']}),
])

cloud_sql_meta = CloudServiceMeta.set_layouts([sql_meta_instance, sql_meta_configuration, sql_meta_connection,
                                               sql_meta_database, sql_meta_user, sql_meta_backup])


class CloudSQLResource(CloudServiceResource):
    cloud_service_group = StringType(default='CloudSQL')


class InstanceResource(CloudSQLResource):
    cloud_service_type = StringType(default='Instance')
    data = ModelType(Instance)
    _metadata = ModelType(CloudServiceMeta, default=cloud_sql_meta, serialized_name='metadata')


class InstanceResponse(CloudServiceResponse):
    resource = PolyModelType(InstanceResource)
