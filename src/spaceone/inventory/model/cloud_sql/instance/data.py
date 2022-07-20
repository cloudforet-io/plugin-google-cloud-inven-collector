from schematics import Model
from schematics.types import ModelType, ListType, StringType, BooleanType, IntType, DateTimeType
from spaceone.inventory.libs.schema.cloud_service import BaseResource


class SQLServerUserDetail(Model):
    disabled = BooleanType()
    server_roles = ListType(StringType, deserialize_from='serverRoles')


class User(Model):
    kind = StringType()
    etag = StringType()
    name = StringType()
    host = StringType()
    instance = StringType()
    project = StringType()
    sql_server_user_details = ModelType(SQLServerUserDetail,
                                        deserialize_from='sqlserverUserDetails',
                                        serialize_when_none=False)


class SQLServerDatabaseDetail(Model):
    compatibility_level = IntType(deserialize_from='compatibilityLevel')
    recovery_model = StringType(deserialize_from='recoveryModel')


class Database(Model):
    self_link = StringType(deserialize_from='selfLink')
    kind = StringType()
    charset = StringType()
    collation = StringType()
    etag = StringType()
    name = StringType()
    instance = StringType()
    project = StringType()
    sql_server_database_details = ModelType(SQLServerDatabaseDetail,
                                            deserialize_from='sqlserverDatabaseDetails',
                                            serialize_when_none=False)


class ServerCACert(Model):
    kind = StringType()
    cert_serial_number = StringType(deserialize_from="certSerialNumber")
    common_name = StringType(deserialize_from="commonName")
    sha1_fingerprint = StringType(deserialize_from="sha1Fingerprint")
    instance = StringType()
    create_time = DateTimeType(deserialize_from="createTime")
    expiration_time = DateTimeType(deserialize_from="expirationTime")


class BackupRetentionSettings(Model):
    retention_unit = StringType(deserialize_from="retentionUnit")
    retained_backups = IntType(deserialize_from="retainedBackups")


class BackupConfiguration(Model):
    start_time = StringType(deserialize_from="startTime")
    kind = StringType()
    location = StringType()
    binary_log_enabled = BooleanType(deserialize_from="binaryLogEnabled", serialize_when_none=False)
    replication_log_archiving_enabled = BooleanType(deserialize_from="replicationLogArchivingEnabled",
                                                    serialize_when_none=False)
    backup_retention_settings = ModelType(BackupRetentionSettings, deserialize_from="backupRetentionSettings")
    enabled = BooleanType()
    point_in_time_recovery_enabled = BooleanType(deserialize_from="pointInTimeRecoveryEnabled",
                                                 serialize_when_none=False)
    transaction_log_retention_days = IntType(deserialize_from="transactionLogRetentionDays")


class MaintenanceWindow(Model):
    kind = StringType()
    hour = IntType()
    day = IntType()


class AuthorizedNetworks(Model):
    value = StringType()
    name = StringType()
    kind = StringType()


class IPConfiguration(Model):
    authorized_networks = ListType(ModelType(AuthorizedNetworks), deserialize_from="authorizedNetworks")
    ipv4_enabled = BooleanType()


class LocationPreference(Model):
    zone = StringType()
    kind = StringType()


class InstanceSetting(Model):
    authorize_gae_applications = ListType(StringType, deserialize_from="authorizedGaeApplications")
    tier = StringType()
    kind = StringType()
    availability_type = StringType(deserialize_from="availabilityType")
    pricing_plan = StringType(deserialize_from="pricingPlan")
    replication_type = StringType(deserialize_from="replicationType")
    activation_policy = StringType(deserialize_from="activationPolicy")
    ip_configuration = ModelType(IPConfiguration, deserialize_from="ipConfiguration")
    location_preference = ModelType(LocationPreference, deserialize_from="locationPreference")
    data_disk_type = StringType(deserialize_from="dataDiskType")
    maintenance_window = ModelType(MaintenanceWindow, deserialize_from="maintenanceWindow")
    backup_configuration = ModelType(BackupConfiguration, deserialize_from="backupConfiguration")
    collation = StringType()
    settings_version = StringType(deserialize_from="settingsVersion")
    storage_auto_resize_limit = StringType(deserialize_from="storageAutoResizeLimit")
    storage_auto_resize = BooleanType(deserialize_from="storageAutoResize")
    data_disk_size_gb = StringType(deserialize_from="dataDiskSizeGb")


class IPAddress(Model):
    type = StringType(deserialize_from="type")
    ip_address = StringType(deserialize_from="ipAddress")


class Instance(BaseResource):
    kind = StringType()
    display_state = StringType(choices=('RUNNING', 'STOPPED', 'UNKNOWN', 'ON-DEMAND'))
    state = StringType(choices=('SQL_INSTANCE_STATE_UNSPECIFIED', 'RUNNABLE', 'SUSPENDED', 'PENDING_DELETE',
                                'PENDING_CREATE', 'MAINTENANCE', 'FAILED'))
    gce_zone = StringType(deserialize_from="gceZone")
    database_version = StringType(deserialize_from="databaseVersion")
    settings = ModelType(InstanceSetting)
    etag = StringType()
    ip_addresses = ListType(ModelType(IPAddress), deserialize_from="ipAddresses")
    server_ca_cert = ModelType(ServerCACert, deserialize_from="serverCaCert")
    instance_type = StringType(deserialize_from="instanceType")
    service_account_email_address = StringType(deserialize_from="serviceAccountEmailAddress")
    backend_type = StringType(deserialize_from="backendType")
    databases = ListType(ModelType(Database))
    users = ListType(ModelType(User))
    connection_name = StringType(deserialize_from="connectionName", serialize_when_none=False)

    def reference(self):
        return {
            "resource_id": self.self_link,
            "external_link": f"https://console.cloud.google.com/sql/instances/{self.name}/overview?authuser=1&project={self.project}"
        }
