import logging
import time
from datetime import datetime

from spaceone.inventory.connector.filestore.instance_v1 import (
    FilestoreInstanceConnector,
)
from spaceone.inventory.connector.filestore.instance_v1beta1 import (
    FilestoreInstanceV1Beta1Connector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.filestore.instance.cloud_service import (
    FilestoreInstanceResource,
    FilestoreInstanceResponse,
)
from spaceone.inventory.model.filestore.instance.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.filestore.instance.data import FilestoreInstanceData

_LOGGER = logging.getLogger(__name__)


class FilestoreInstanceManager(GoogleCloudManager):
    """
    Google Cloud Filestore Instance Manager

    Filestore 인스턴스 리소스를 수집하고 처리하는 매니저 클래스
    - 인스턴스 목록 수집
    - 인스턴스 상세 정보 처리
    - 리소스 응답 생성
    """

    connector_name = "FilestoreInstanceConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    instance_conn = None
    instance_v1beta1_conn = None

    def _convert_google_cloud_datetime(self, google_cloud_datetime: str) -> str:
        """
        Google Cloud API의 날짜 형식을 SpaceONE에서 사용하는 형식으로 변환합니다.

        Args:
            google_cloud_datetime (str): Google Cloud API 날짜 형식 (예: 2025-08-18T06:13:54.868444486Z)

        Returns:
            str: 변환된 날짜 형식 (예: 2025-08-18T06:13:54Z)
        """
        try:
            if not google_cloud_datetime:
                return ""

            # Google Cloud API 날짜 형식 파싱 (나노초 포함)
            # 예: 2025-08-18T06:13:54.868444486Z
            dt = datetime.fromisoformat(google_cloud_datetime.replace("Z", "+00:00"))

            # 초 단위까지로 변환
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception as e:
            _LOGGER.warning(f"Failed to convert datetime {google_cloud_datetime}: {e}")
            return google_cloud_datetime

    def collect_cloud_service(self, params):
        """
        Filestore 인스턴스 리소스를 수집합니다.

        Args:
            params (dict): 수집 파라미터
                - secret_data: 인증 정보
                - options: 옵션 설정

        Returns:
            Tuple[List[FilestoreInstanceResponse], List[ErrorResourceResponse]]:
                성공한 리소스 응답 리스트와 에러 응답 리스트
        """
        _LOGGER.debug("** Filestore Instance START **")

        resource_responses = []
        error_responses = []
        instance_id = ""

        start_time = time.time()
        secret_data = params.get("secret_data", {})
        project_id = secret_data.get("project_id", "")

        ##################################
        # 0. Filestore Instance Connector 초기화
        # Google Cloud Filestore API를 통해 인스턴스 정보를 조회
        ##################################
        self.instance_conn: FilestoreInstanceConnector = self.locator.get_connector(
            self.connector_name, **params
        )

        # v1beta1 API connector 초기화 (파일 공유 조회용)
        self.instance_v1beta1_conn: FilestoreInstanceV1Beta1Connector = (
            self.locator.get_connector("FilestoreInstanceV1Beta1Connector", **params)
        )

        # Filestore 인스턴스 목록 조회
        filestore_instances = self.instance_conn.list_instances()

        ##################################
        # 1. 각 Filestore 인스턴스 처리
        ##################################
        for filestore_instance in filestore_instances:
            try:
                ##################################
                # 2. 기본 정보 설정
                ##################################
                instance_id = filestore_instance.get("name", "")
                location = filestore_instance.get("location", "")

                # 리전 코드 설정
                self.set_region_code(location)

                ##################################
                # 3. Filestore 인스턴스 리소스 생성
                ##################################
                resource = self.get_filestore_instance_resource(
                    project_id, location, filestore_instance
                )

                ##################################
                # 4. 리소스 응답 객체 생성
                ##################################
                resource_responses.append(
                    FilestoreInstanceResponse({"resource": resource})
                )

            except Exception as e:
                _LOGGER.error(
                    f"[list_resources] instance_id => {instance_id}, error => {e}",
                    exc_info=True,
                )
                error_response = self.generate_resource_error_response(
                    e, "Filestore", "Instance", instance_id
                )
                error_responses.append(error_response)

        _LOGGER.debug(
            f"** Filestore Instances Finished {time.time() - start_time} Seconds **"
        )
        return resource_responses, error_responses

    def get_filestore_instance_resource(
        self, project_id: str, location: str, instance: dict
    ) -> FilestoreInstanceResource:
        """
        Filestore 인스턴스 리소스 객체를 생성합니다.

        Args:
            project_id (str): 프로젝트 ID
            location (str): 리전
            instance (dict): Filestore 인스턴스 정보

        Returns:
            FilestoreInstanceResource: Filestore 인스턴스 리소스 객체
        """

        ##################################
        # 1. 기본 인스턴스 정보 추출
        ##################################
        instance_name = instance.get("name", "")
        instance_id = instance.get("name", "").split("/")[
            -1
        ]  # 마지막 부분이 인스턴스 ID

        # 상태 정보
        state = instance.get("state", "")
        description = instance.get("description", "")

        # 네트워크 정보
        networks = instance.get("networks", [])
        network_info = []
        for network in networks:
            network_info.append(
                {
                    "network": network.get("network", ""),
                    "modes": network.get("modes", []),
                    "reserved_ip_range": network.get("reservedIpRange", ""),
                }
            )

        # 파일 공유 정보 (v1 API에서 제공)
        file_shares = instance.get("fileShares", [])
        file_share_info = []
        total_capacity_gb = 0
        for file_share in file_shares:
            capacity_gb = int(file_share.get("capacityGb", 0))
            total_capacity_gb += capacity_gb
            file_share_info.append(
                {
                    "name": file_share.get("name", ""),
                    "capacity_gb": capacity_gb,
                    "source_backup": file_share.get("sourceBackup", ""),
                    "nfs_export_options": file_share.get("nfsExportOptions", []),
                }
            )

        # 라벨 정보
        labels = instance.get("labels", {})
        label_list = [{"key": k, "value": v} for k, v in labels.items()]

        ##################################
        # 2. 파일 공유 상세 정보 수집 (티어별 처리)
        ##################################
        detailed_shares = []

        # Enterprise 티어에서만 shares API 호출 시도
        tier = instance.get("tier", "")
        multishare_enabled = instance.get("multishareEnabled", False)

        if (
            tier in ["ENTERPRISE", "ENTERPRISE_TIER_1", "ENTERPRISE_TIER_2"]
            and multishare_enabled
        ):
            try:
                # v1beta1 API로 파일 공유 상세 정보 조회 (멀티쉐어가 활성화된 경우)
                shares = self.instance_v1beta1_conn.list_shares_for_instance(
                    instance_name
                )
                for share in shares:
                    detailed_shares.append(
                        {
                            "name": share.get("name", ""),
                            "mount_name": share.get("mountName", ""),
                            "description": share.get("description", ""),
                            "capacity_gb": share.get("capacityGb", 0),
                            "state": share.get("state", ""),
                            "labels": share.get("labels", {}),
                            "nfs_export_options": share.get("nfsExportOptions", []),
                        }
                    )
            except Exception as e:
                if "ListShares operation is not supported" in str(e):
                    _LOGGER.info(
                        f"ListShares operation is not supported for Enterprise instance {instance_id}. "
                        "This may be due to region limitations or instance state."
                    )
                else:
                    _LOGGER.warning(
                        f"Failed to collect detailed shares for Enterprise instance {instance_id}: {e}"
                    )

        ##################################
        # 3. 인스턴스의 스냅샷 정보 수집
        ##################################
        snapshots = []
        try:
            # 인스턴스의 스냅샷 목록 조회 (v1 API 사용)
            # Google Cloud Filestore v1에서는 스냅샷이 인스턴스 레벨에서 관리됨
            instance_snapshots = self.instance_conn.list_snapshots_for_instance(
                instance_name
            )

            for snapshot in instance_snapshots:
                # 스냅샷 이름에서 파일 공유 정보 추출
                # 예: projects/my-project/locations/us-central1/instances/my-instance/fileShares/my-share/snapshots/my-snapshot
                snapshot_name = snapshot.get("name", "")
                source_file_share = self._extract_file_share_from_snapshot_name(
                    snapshot_name
                )
                snapshot["source_file_share"] = source_file_share

                # 스냅샷 날짜 형식 변환
                if "createTime" in snapshot:
                    snapshot["createTime"] = self._convert_google_cloud_datetime(
                        snapshot["createTime"]
                    )

                snapshots.append(snapshot)

        except Exception as e:
            _LOGGER.warning(
                f"Failed to collect snapshots for instance {instance_id}: {e}"
            )

        ##################################
        # 4. 모니터링 정보 설정
        ##################################
        google_cloud_filters = [
            {"key": "resource.labels.instance_id", "value": instance_id}
        ]

        ##################################
        # 5. 리소스 데이터 구성
        ##################################
        instance_data = {
            "name": instance_id,
            "full_name": instance_name,  # reference 메서드용 전체 경로
            "instance_id": instance_id,
            "state": state,
            "description": description,
            "location": location,
            "tier": instance.get("tier", ""),
            "networks": network_info,
            "file_shares": file_share_info,
            "detailed_shares": detailed_shares,  # v1beta1 API에서 조회한 상세 정보
            "snapshots": snapshots,
            "labels": label_list,
            "create_time": self._convert_google_cloud_datetime(
                instance.get("createTime", "")
            ),
            "update_time": self._convert_google_cloud_datetime(
                instance.get("updateTime", "")
            ),
            "stats": {
                "total_capacity_gb": total_capacity_gb,
                "file_share_count": len(file_shares),
                "snapshot_count": len(snapshots),
                "network_count": len(networks),
            },
            "google_cloud_monitoring": self.set_google_cloud_monitoring(
                project_id,
                "file.googleapis.com/instance",
                instance_id,
                google_cloud_filters,
            ),
            "google_cloud_logging": self.set_google_cloud_logging(
                "Filestore", "Instance", project_id, instance_id
            ),
        }

        ##################################
        # 6. FilestoreInstanceData 객체 생성
        ##################################
        instance_data_obj = FilestoreInstanceData(instance_data, strict=False)

        ##################################
        # 7. FilestoreInstanceResource 객체 생성
        ##################################
        resource_data = {
            "name": instance_id,
            "account": project_id,
            "instance_type": instance.get(
                "tier", ""
            ),  # BASIC_HDD, BASIC_SSD, ENTERPRISE 등
            "instance_size": total_capacity_gb,
            "tags": label_list,
            "region_code": location,
            "data": instance_data_obj,
            "reference": ReferenceModel(instance_data_obj.reference()),
        }

        try:
            resource = FilestoreInstanceResource(resource_data, strict=False)
            return resource
        except Exception as e:
            _LOGGER.error(
                f"Failed to create FilestoreInstanceResource for {instance_id}: {e}"
            )
            raise

    def _extract_file_share_from_snapshot_name(self, snapshot_name):
        """
        스냅샷 이름에서 파일 공유 정보를 추출합니다.

        Args:
            snapshot_name (str): 스냅샷 이름

        Returns:
            str: 파일 공유 이름
        """
        try:
            # 예: projects/my-project/locations/us-central1/instances/my-instance/fileShares/my-share/snapshots/my-snapshot
            parts = snapshot_name.split("/")
            if len(parts) >= 10 and parts[6] == "fileShares":
                return parts[7]
            return "unknown"
        except Exception:
            return "unknown"
