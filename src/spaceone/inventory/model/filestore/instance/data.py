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


class FileShare(Model):
    """파일 공유 정보 모델"""

    name = StringType()
    capacity_gb = StringType()
    source_backup = StringType()
    nfs_export_options = ListType(StringType)


class DetailedShare(Model):
    """상세 파일 공유 정보 모델 (v1beta1 API)"""

    name = StringType()
    mount_name = StringType()
    description = StringType()
    capacity_gb = StringType()
    state = StringType()
    labels = DictType(StringType)
    nfs_export_options = ListType(StringType)


class Snapshot(Model):
    """스냅샷 정보 모델"""

    name = StringType()
    state = StringType()
    create_time = StringType()
    source_file_share = StringType()


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

    # 파일 공유 정보
    file_shares = ListType(ModelType(FileShare))
    detailed_shares = ListType(ModelType(DetailedShare), serialize_when_none=False)

    # 스냅샷 정보
    snapshots = ListType(ModelType(Snapshot))

    # 라벨 정보
    labels = DictType(StringType)

    # 시간 정보
    create_time = StringType()
    update_time = StringType()

    # 통계 정보
    stats = ModelType(Stats)

    def reference(self):
        # 프로젝트 ID와 리전 추출 (full_name 사용)
        parts = self.full_name.split("/")
        project_id = parts[1]  # projects/{project_id}
        location = parts[3]  # locations/{location}

        return {
            "resource_id": self.full_name,
            "external_link": f"https://console.cloud.google.com/filestore/instances?project={project_id}&location={location}",
        }
