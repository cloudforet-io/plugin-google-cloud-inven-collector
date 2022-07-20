from schematics import Model
from schematics.types import ModelType, ListType, StringType, IntType, DateTimeType, BooleanType, FloatType, DictType, UnionType, MultiType
from spaceone.inventory.libs.schema.cloud_service import BaseResource


class Labels(Model):
    key = StringType()
    value = StringType()


class RetentionPolicy(Model):
    effective_time = DateTimeType(deserialize_from='effectiveTime')
    is_locked = BooleanType(deserialize_from='isLocked')
    retention_period = IntType(deserialize_from='retentionPeriod')


class Location(Model):
    location = StringType(default='')
    location_type = StringType(choices=('Multi-region', 'Dual-region', 'Region'))
    location_display = StringType(default='')


class ProjectTeam(Model):
    project_number = StringType(deserialize_from='projectNumber')
    team = StringType(deserialize_from='team')


class BucketAccessControls(Model):
    bucket = StringType(deserialize_from='bucket', serialize_when_none=False)
    entity = StringType(deserialize_from='entity', serialize_when_none=False)
    etag = StringType(deserialize_from='etag', serialize_when_none=False)
    id = StringType(deserialize_from='id', serialize_when_none=False)
    kind = StringType(deserialize_from='kind', serialize_when_none=False)
    role = StringType(deserialize_from='role', serialize_when_none=False)
    self_link = StringType(deserialize_from='selfLink', serialize_when_none=False)
    project_team = ModelType(ProjectTeam, deserialize_from='projectTeam', serialize_when_none=False)


class ObjectACL(Model):
    entity = StringType(deserialize_from='entity', serialize_when_none=False)
    etag = StringType(deserialize_from='etag', serialize_when_none=False)
    kind = StringType(deserialize_from='kind', serialize_when_none=False)
    role = StringType(deserialize_from='role', serialize_when_none=False)
    email = StringType(deserialize_from='email', serialize_when_none=False)
    project_team = ModelType(ProjectTeam, deserialize_from='projectTeam', serialize_when_none=False)


class Action(Model):
    type = StringType(serialize_when_none=False)
    storage_class = StringType(deserialize_from='storageClass', serialize_when_none=False)


class Condition(Model):
    age = IntType(deserialize_from='age', serialize_when_none=False)
    created_before = StringType(deserialize_from='createdBefore', serialize_when_none=False)
    custom_time_before = StringType(deserialize_from='customTimeBefore', serialize_when_none=False)
    days_since_custom_time = IntType(deserialize_from='daysSinceCustomTime', serialize_when_none=False)
    days_since_non_current_time = IntType(deserialize_from='daysSinceNoncurrentTime', serialize_when_none=False)
    is_live = BooleanType(deserialize_from='isLive', serialize_when_none=False)
    matches_storage_class = ListType(StringType(), deserialize_from='matchesStorageClass', serialize_when_none=False)
    non_current_time_before = StringType(deserialize_from='noncurrentTimeBefore', serialize_when_none=False)
    num_newer_versions = IntType(deserialize_from='numNewerVersions', serialize_when_none=False)


class Rule(Model):
    action = ModelType(Action)
    action_display = StringType(serialize_when_none=False)
    condition = ModelType(Condition)
    condition_display = StringType(serialize_when_none=False)


class Lifecycle(Model):
    lifecycle_rule_display = StringType()
    rule = ListType(ModelType(Rule), default=[], serialize_when_none=False)


class Link(Model):
    link_url = StringType()
    gsutil_link = StringType()


class BucketAccess(Model):
    enabled = BooleanType(serialize_when_none=False)
    locked_time = DateTimeType(deserialize_from='lockedTime', serialize_when_none=False)


class BindingCondition(Model):
    title = StringType()
    description = StringType()
    expression = StringType()


class Binding(Model):
    role = StringType()
    members = ListType(StringType())
    condition = ModelType(BindingCondition, serialize_when_none=False)


class IAMPolicy(Model):
    version = IntType()
    kind = StringType()
    resource_id = StringType(deserialize_from='resourceId')
    bindings = ListType(ModelType(Binding), default=[])
    etag = StringType(serialize_when_none=False)
    error_flag = StringType(serialize_when_none=False)


class PolicyBinding(Model):
    member = StringType()
    role = StringType()


class IAMConfiguration(Model):
    bucket_policy_only = ModelType(BucketAccess, deserialize_from='bucketPolicyOnly', serialize_when_none=False)
    uniform_bucket_level_access = ModelType(BucketAccess, deserialize_from='uniformBucketLevelAccess', serialize_when_none=False)


class Storage(BaseResource):
    links = ModelType(Link)
    acl = ListType(ModelType(BucketAccessControls), default=[], deserialize_from='acl')
    default_event_based_hold = StringType(choices=('Enabled', 'Disabled'))
    default_object_acl = ListType(ModelType(ObjectACL), default=[], serialize_when_none=False, deserialize_from='defaultObjectAcl')
    public_access = StringType(choices=('Subject to object ACLs', 'Not Public', 'Public to Internet'))
    access_control = StringType(choices=('Fine-grained', 'Uniform'))
    lifecycle_rule = ModelType(Lifecycle, serialize_when_none=False)
    retention_policy = ModelType(RetentionPolicy, deserialize_from='retentionPolicy', serialize_when_none=False)
    retention_policy_display = StringType()
    location = ModelType(Location)
    default_storage_class = StringType(choices=('Standard', 'Nearline', 'Coldline', 'Archive'))
    iam_configuration = ModelType(IAMConfiguration, deserialize_from='iamConfiguration', serialize_when_none=False)
    iam_policy = ModelType(IAMPolicy, serialize_when_none=False)
    iam_policy_binding = ListType(ModelType(PolicyBinding), serialize_when_none=False)
    requester_pays = StringType(choices=('ON', 'OFF'))
    object_count = IntType(default=0)
    object_total_size = FloatType(default=0.0)
    size = FloatType(default=0.0)
    labels = ListType(ModelType(Labels), default=[])
    encryption = StringType(choices=('Google-managed', 'Customer-managed'))
    creation_timestamp = DateTimeType(deserialize_from='timeCreated')
    update_timestamp = DateTimeType(deserialize_from='updated')

    def reference(self):
        return {
            "resource_id": self.self_link,
            "external_link": f"https://console.cloud.google.com/storage/browser/{self.name}"
        }
