from schematics import Model
from schematics.types import (
    ModelType,
    ListType,
    StringType,
    FloatType,
    DateTimeType,
    IntType,
)
from spaceone.inventory.libs.schema.cloud_service import BaseResource


class Labels(Model):
    key = StringType()
    value = StringType()


class HourlySchedule(Model):
    hours_in_cycle = IntType(deserialize_from="hoursInCycle")
    start_time = StringType(deserialize_from="startTime")
    duration = StringType()


class DailySchedule(Model):
    days_in_cycle = IntType(deserialize_from="daysInCycle")
    start_time = StringType(deserialize_from="startTime")
    duration = StringType()


class DayOfWeek(Model):
    day = StringType(
        choices=(
            "MONDAY",
            "TUESDAY",
            "WEDNESDAY",
            "THURSDAY",
            "FRIDAY",
            "SATURDAY",
            "SUNDAY",
        )
    )
    start_time = StringType(deserialize_from="startTime")
    duration = StringType()


class WeeklySchedule(Model):
    day_of_weeks = ListType(ModelType(DayOfWeek), default=[])


class Schedule(Model):
    hourly_schedule = ModelType(
        HourlySchedule, deserialize_from="hourlySchedule", serialize_when_none=False
    )
    daily_schedule = ModelType(
        DailySchedule, deserialize_from="dailySchedule", serialize_when_none=False
    )
    weekly_schedule = ModelType(
        WeeklySchedule, deserialize_from="weeklySchedule", serialize_when_none=False
    )


class RetentionPolicy(Model):
    max_retention_days_display = StringType(serialize_when_none=False)
    max_retention_days = IntType(
        deserialize_from="maxRetentionDays", serialize_when_none=False
    )
    on_source_disk_delete = StringType(
        deserialize_from="onSourceDiskDelete", serialize_when_none=False
    )


class SnapshotSchedulePolicy(Model):
    schedule_display = ListType(StringType(), default=[])
    schedule = ModelType(
        Schedule, deserialize_from="schedule", serialize_when_none=False
    )
    retention_policy = ModelType(
        RetentionPolicy, deserialize_from="retentionPolicy", serialize_when_none=False
    )


class SnapShotSchedule(Model):
    id = StringType()
    name = StringType()
    status = StringType()
    description = StringType()
    region = StringType()
    self_link = StringType(deserialize_from="selfLink")
    snapshot_schedule_policy = ModelType(
        SnapshotSchedulePolicy, deserialize_from="snapshotSchedulePolicy"
    )
    storage_locations = ListType(StringType(), default=[])
    labels = ListType(ModelType(Labels), default=[])
    tags = ListType(ModelType(Labels), default=[])
    creation_timestamp = DateTimeType(deserialize_from="creationTimestamp")


class Disk(BaseResource):
    zone = StringType()
    disk_type = StringType(
        choices=("local-ssd", "pd-balanced", "pd-ssd", "pd-standard"),
        serialize_when_none=False,
    )
    read_iops = FloatType(serialize_when_none=False)
    write_iops = FloatType(serialize_when_none=False)
    read_throughput = FloatType(serialize_when_none=False)
    write_throughput = FloatType(serialize_when_none=False)
    in_used_by = ListType(StringType(), default=[])
    in_used_by_count_display = IntType(serialize_when_none=False, default=0)
    source_image_display = StringType(serialize_when_none=False)
    source_image_id = StringType(
        deserialize_from="sourceImageId", serialize_when_none=False
    )
    source_image = StringType(deserialize_from="sourceImage", serialize_when_none=False)
    status = StringType(
        choices=("INVALID", "CREATING", "machine_image_conn", "DELETING", "UPLOADING")
    )
    encryption = StringType(
        choices=("Google managed", "Customer managed, Customer supplied")
    )
    size = FloatType()
    fingerprint = StringType(deserialize_from="labelFingerprint")
    snapshot_schedule_display = ListType(StringType(), default=[])
    snapshot_schedule = ListType(ModelType(SnapShotSchedule), default=[])
    labels = ListType(ModelType(Labels), default=[])
    creation_timestamp = DateTimeType(deserialize_from="creationTimestamp")
    last_attach_timestamp = DateTimeType(
        deserialize_from="lastAttachTimestamp", serialize_when_none=False
    )
    last_detach_timestamp = DateTimeType(
        deserialize_from="lastDetachTimestamp", serialize_when_none=False
    )

    def reference(self):
        return {
            "resource_id": self.self_link,
            "external_link": f"https://console.cloud.google.com/compute/disksDetail/zones/{self.zone}/disks/{self.name}?project={self.project}",
        }
