from schematics import Model
from schematics.types import (
    BaseType,
    DictType,
    ListType,
    StringType,
)


class Build(Model):
    id = StringType()
    name = StringType()
    status = StringType()
    source = DictType(BaseType, default={})
    steps = ListType(DictType(BaseType), default=[])
    results = DictType(BaseType, default={})
    create_time = StringType(deserialize_from="createTime")  
    start_time = StringType(deserialize_from="startTime")    
    finish_time = StringType(deserialize_from="finishTime")  
    timeout = StringType()
    images = ListType(StringType, default=[])
    artifacts = DictType(BaseType, default={})
    logs_bucket = StringType(deserialize_from="logsBucket")
    source_provenance = DictType(BaseType, deserialize_from="sourceProvenance", default={})
    build_trigger_id = StringType(deserialize_from="buildTriggerId")
    options = DictType(BaseType, default={})
    log_url = StringType(deserialize_from="logUrl")
    substitutions = DictType(BaseType, default={})
    tags = ListType(StringType, default=[])
    timing = DictType(BaseType, default={})
    approval = DictType(BaseType, default={})
    service_account = StringType(deserialize_from="serviceAccount")
    available_secrets = DictType(BaseType, deserialize_from="availableSecrets", default={})
    warnings = ListType(DictType(BaseType), default=[])
    failure_info = DictType(BaseType, deserialize_from="failureInfo", default={})
