from schematics import Model
from schematics.types import ModelType, ListType, StringType, IntType, DateTimeType
from spaceone.inventory.libs.schema.cloud_service import BaseResource


class Labels(Model):
    key = StringType()
    value = StringType()


class ComputeVM(Model):
    id = StringType()
    name = StringType()
    region = StringType()
    zone = StringType()
    address = StringType()
    project = StringType()
    subnetwork = StringType()
    tags = ListType(StringType(), default=[])
    service_accounts = ListType(StringType(), default=[])
    creation_timestamp = DateTimeType()
    labels = ListType(ModelType(Labels), default=[])
    labels_display = ListType(StringType(), default=[])


class RouteDisplay(Model):
    network_display = StringType()
    next_hop = StringType()
    instance_tags = ListType(StringType(), default=[])
    instance_tags_on_list = ListType(StringType(), default=[])


class Route(BaseResource):
    description = StringType()
    network = StringType()
    dest_range = StringType(deserialize_from='destRange')
    priority = IntType()
    tags = ListType(StringType(), default=[])
    applicable_instance = ListType(ModelType(ComputeVM), default=[])
    nextHopInstance = StringType(deserialize_from='nextHopInstance', serialize_when_none=False)
    nextHopIp = StringType(deserialize_from='nextHopIp', serialize_when_none=False)
    nextHopNetwork = StringType(deserialize_from='nextHopNetwork', serialize_when_none=False)
    nextHopGateway = StringType(deserialize_from='nextHopGateway', serialize_when_none=False)
    nextHopPeering = StringType(deserialize_from='nextHopPeering', serialize_when_none=False)
    nextHopIlb = StringType(deserialize_from='nextHopIlb', serialize_when_none=False)
    display = ModelType(RouteDisplay)
    creation_timestamp = DateTimeType(deserialize_from='creationTimestamp')

    def reference(self):
        return {
            "resource_id": self.self_link,
            "external_link": f"https://console.cloud.google.com/networking/routes/details/{self.name}?project={self.project}"
        }
