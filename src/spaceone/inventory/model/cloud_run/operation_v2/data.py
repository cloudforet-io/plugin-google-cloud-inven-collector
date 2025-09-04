from schematics import Model
from schematics.types import (
    BaseType,
    BooleanType,
    DateTimeType,
    DictType,
    IntType,
    StringType,
)


class OperationV2(Model):
    # Basic operation information
    name = StringType()
    done = BooleanType()
    
    # Metadata from operation response
    metadata = BaseType()  # Complex metadata structure
    
    # Response data
    response = BaseType()  # Operation response data
    
    # Error information
    error = BaseType()  # Error details if operation failed
    
    # Additional fields
    project = StringType()
    location = StringType()
    region = StringType()
    
    # Timestamps
    create_time = DateTimeType()
    end_time = DateTimeType()
    
    # Operation type and target
    operation_type = StringType()
    target_resource = StringType()
    
    # Status information
    status = StringType()
    progress = IntType(default=0)
    
    # Labels and annotations
    labels = DictType(StringType, default={})
    annotations = DictType(StringType, default={})
