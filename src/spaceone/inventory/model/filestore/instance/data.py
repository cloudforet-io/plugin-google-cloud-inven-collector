from schematics import Model
from schematics.types import DictType, ListType, ModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import BaseResource

"""
Filestore Instance Data 모델 정의

Google Cloud Filestore 인스턴스의 상세 데이터를 표현하기 위한 schematics 모델입니다.
"""


class Network(Model):
    """네트워크 정보 모델"""

    network = StringType()
    modes = ListType(StringType())
    reserved_ip_range = StringType()
    connect_mode = StringType(serialize_when_none=False)


class PerformanceLimits(Model):
    """성능 제한 정보 모델"""
    
    max_read_iops = StringType(serialize_when_none=False)
    max_write_iops = StringType(serialize_when_none=False)
    max_read_throughput_bps = StringType(serialize_when_none=False)
    max_write_throughput_bps = StringType(serialize_when_none=False)
    max_iops = StringType(serialize_when_none=False)


class UnifiedFileShare(Model):
    """통합 파일 공유 정보 모델 (기본 + 상세 정보)"""

    name = StringType()
    mount_name = StringType(serialize_when_none=False)
    description = StringType(serialize_when_none=False)
    capacity_gb = StringType()
    state = StringType(serialize_when_none=False)
    source_backup = StringType(serialize_when_none=False)
    nfs_export_options = ListType(StringType, default=[], serialize_when_none=False)
    data_source = StringType()  # "Basic" 또는 "Detailed" 표시


class Snapshot(Model):
    """스냅샷 정보 모델"""

    name = StringType()
    full_name = StringType()
    description = StringType()
    state = StringType()
    create_time = StringType()
    labels = ListType(DictType(StringType), default=[])


class Stats(Model):
    """통계 정보 모델"""

    total_capacity_gb = StringType()
    file_share_count = StringType()
    snapshot_count = StringType()
    network_count = StringType()


class FilestoreInstanceData(BaseResource):
    """Filestore 인스턴스 데이터 모델"""

    # 기본 정보
    full_name = StringType()  # reference 메서드용 전체 경로
    instance_id = StringType()
    state = StringType()
    description = StringType()
    location = StringType()
    tier = StringType()

    # 네트워크 정보
    networks = ListType(ModelType(Network))

    # 파일 공유 정보 (통합)
    unified_file_shares = ListType(ModelType(UnifiedFileShare), serialize_when_none=False)

    # 스냅샷 정보
    snapshots = ListType(ModelType(Snapshot))

    # 라벨 정보
    labels = ListType(DictType(StringType), default=[])

    # 시간 정보
    create_time = StringType(deserialize_from="createTime")

    # 통계 정보s
    stats = ModelType(Stats)
    
    # 인스턴스 레벨 성능 및 용량 정보
    protocol = StringType(serialize_when_none=False)
    custom_performance_supported = StringType(serialize_when_none=False)
    performance_limits = ModelType(PerformanceLimits, serialize_when_none=False)

    def reference(self):

        return {
            "resource_id": f"https://file.googleapis.com/v1/{self.full_name}",
            "external_link": f"https://console.cloud.google.com/filestore/instances/locations/{self.location}/id/{self.instance_id}?project={self.project}",
        }
