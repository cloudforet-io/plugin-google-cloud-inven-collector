from schematics.types import ModelType, PolyModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.model.batch.location.data import (
    Location,
    batch_location_meta,
)

"""
Batch Location
"""


class BatchGroupResource(CloudServiceResource):
    cloud_service_group = StringType(default="Batch")


class LocationResource(BatchGroupResource):
    cloud_service_type = StringType(default="Location")
    data = ModelType(Location)
    _metadata = ModelType(
        CloudServiceMeta, default=batch_location_meta, serialized_name="metadata"
    )


class LocationResponse(CloudServiceResponse):
    resource = PolyModelType(LocationResource)
