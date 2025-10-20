from schematics import Model
from schematics.types import DictType, ListType, ModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import BaseResource


class Network(Model):
    """Network information model"""

    network = StringType()
    modes = ListType(StringType())
    reserved_ip_range = StringType()
    connect_mode = StringType(serialize_when_none=False)


class PerformanceLimits(Model):
    """Performance limit information model"""

    max_read_iops = StringType(serialize_when_none=False)
    max_write_iops = StringType(serialize_when_none=False)
    max_read_throughput_bps = StringType(serialize_when_none=False)
    max_write_throughput_bps = StringType(serialize_when_none=False)
    max_iops = StringType(serialize_when_none=False)


class UnifiedFileShare(Model):
    """Unified file share information model"""

    name = StringType()
    mount_name = StringType(serialize_when_none=False)
    description = StringType(serialize_when_none=False)
    capacity_tib = StringType()
    state = StringType(serialize_when_none=False)
    source_backup = StringType(serialize_when_none=False)
    nfs_export_options = ListType(StringType, default=[], serialize_when_none=False)
    data_source = StringType()  # "Basic" 또는 "Detailed" 표시


class Stats(Model):
    """Statistics information model"""

    total_capacity_tib = StringType()
    file_share_count = StringType()
    network_count = StringType()


class FilestoreInstanceData(BaseResource):
    """Filestore Instance data model"""

    full_name = StringType()
    instance_id = StringType()
    state = StringType()
    description = StringType()
    location = StringType()
    tier = StringType()

    networks = ListType(ModelType(Network))

    unified_file_shares = ListType(
        ModelType(UnifiedFileShare), serialize_when_none=False
    )

    labels = ListType(DictType(StringType), default=[])

    create_time = StringType(deserialize_from="createTime")

    stats = ModelType(Stats)

    protocol = StringType(serialize_when_none=False)
    custom_performance_supported = StringType(serialize_when_none=False)
    performance_limits = ModelType(PerformanceLimits, serialize_when_none=False)

    def reference(self):
        return {
            "resource_id": f"https://file.googleapis.com/v1/{self.full_name}",
            "external_link": f"https://console.cloud.google.com/filestore/instances/locations/{self.location}/id/{self.instance_id}?project={self.project}",
        }
