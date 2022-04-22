from schematics import Model
from schematics.types import ModelType, ListType, StringType, IntType, DateTimeType, BooleanType, FloatType


class Labels(Model):
    key = StringType()
    value = StringType()


class HourlySchedule(Model):
    hours_in_cycle = IntType(deserialize_from='hoursInCycle')
    start_time = StringType(deserialize_from='startTime')
    duration = StringType()


class DailySchedule(Model):
    days_in_cycle = IntType(deserialize_from='daysInCycle')
    start_time = StringType(deserialize_from='startTime')
    duration = StringType()


class DayOfWeek(Model):
    day = StringType(choices=('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'))
    start_time = StringType(deserialize_from='startTime')
    duration = StringType()


class WeeklySchedule(Model):
    day_of_weeks = ListType(ModelType(DayOfWeek), default=[])


class Schedule(Model):
    hourly_schedule = ModelType(HourlySchedule, deserialize_from='hourlySchedule', serialize_when_none=False)
    daily_schedule = ModelType(DailySchedule, deserialize_from='dailySchedule', serialize_when_none=False)
    weekly_schedule = ModelType(WeeklySchedule, deserialize_from='weeklySchedule', serialize_when_none=False)


class RetentionPolicy(Model):
    max_retention_days_display = StringType(serialize_when_none=False)
    max_retention_days = IntType(deserialize_from='maxRetentionDays', serialize_when_none=False)
    on_source_disk_delete = StringType(deserialize_from='onSourceDiskDelete', serialize_when_none=False)


class Disk(Model):
    source_disk = StringType()
    source_disk_display = StringType()
    source_disk_id = StringType()
    disk_size = FloatType()
    storage_bytes = IntType()


class Encryption(Model):
    sha256 = StringType(deserialize_from='sha256')
    kmsKey_service_account = StringType(deserialize_from='kmsKeyServiceAccount')
    raw_key = StringType(deserialize_from='rawKey')
    kms_key_name = StringType(deserialize_from='kmsKeyName')


class Snapshot(Model):
    id = StringType()
    name = StringType()
    project = StringType()
    status = StringType(choices=('CREATING', 'DELETING', 'FAILED', 'READY', 'UPLOADING'))
    self_link = StringType(deserialize_from='selfLink')
    disk = ModelType(Disk, default={})
    fingerprint = StringType(deserialize_from='labelFingerprint')
    snapshot_encryption_key = ModelType(Encryption, serialize_when_none=False, deserialize_from='snapshotEncryptionKey')
    source_disk_encryption_key = ModelType(Encryption, serialize_when_none=False, deserialize_from='sourceDiskEncryptionKey')
    storage_locations = ListType(StringType(), default=[], deserialize_from='storageLocations')
    creation_timestamp = DateTimeType(deserialize_from='creationTimestamp')
    creation_type = StringType(choices=('Manual', 'Scheduled'))
    encryption = StringType(choices=('Google managed', 'Customer managed', 'Customer supplied'))
    labels = ListType(ModelType(Labels), default=[])

    def reference(self):
        return {
            "resource_id": self.self_link,
            "external_link": f"https://console.cloud.google.com/compute/snapshotsDetail/projects/{self.project}/global/snapshots/{self.name}?authuser=2&project={self.project}"
        }
