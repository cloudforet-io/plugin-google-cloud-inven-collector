import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Tuple

from spaceone.inventory.connector.filestore.instance_v1 import (
    FilestoreInstanceConnector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.libs.schema.cloud_service import ErrorResourceResponse
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
    Google Cloud Filestore Instance Manager (v1 API)

    Filestore 인스턴스 리소스를 수집하고 처리하는 매니저 클래스 (v1 API 전용)
    - 인스턴스 목록 수집 (v1 API)
    - 인스턴스 상세 정보 처리 (v1 API)
    - 스냅샷 정보 수집 (v1 API)

    Note: 파일 공유 상세 정보(v1beta1 API)는 별도 매니저에서 처리
    """

    connector_name = "FilestoreInstanceConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    instance_conn = None

    def _convert_google_cloud_datetime(self, google_cloud_datetime: str) -> str:
        """
        Google Cloud API의 날짜 형식을 SpaceONE에서 사용하는 형식으로 변환합니다.

        Args:
            google_cloud_datetime: Google Cloud API 날짜 형식
                (예: 2025-08-18T06:13:54.868444486Z)

        Returns:
            변환된 날짜 형식 (예: 2025-08-18T06:13:54Z)
        """
        try:
            if not google_cloud_datetime:
                return ""

            # 나노초를 마이크로초로 자르기 (소수점 이하 6자리까지만)
            processed_datetime = google_cloud_datetime
            if "." in processed_datetime and "Z" in processed_datetime:
                parts = processed_datetime.split(".")
                if len(parts) == 2:
                    # 마이크로초(6자리)까지만 유지하고 나머지 나노초 제거
                    microseconds = parts[1].replace("Z", "")[:6]
                    processed_datetime = f"{parts[0]}.{microseconds}Z"

            # Google Cloud API 날짜 형식 파싱 (Z를 +00:00으로 변경)
            # 예: 2025-08-18T06:13:54.868444Z
            dt = datetime.fromisoformat(processed_datetime.replace("Z", "+00:00"))

            # 초 단위까지로 변환
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except (ValueError, TypeError) as e:
            _LOGGER.warning(f"Failed to convert datetime {google_cloud_datetime}: {e}")
            return google_cloud_datetime

    def collect_cloud_service(
        self, params: Dict[str, Any]
    ) -> Tuple[List[FilestoreInstanceResponse], List[ErrorResourceResponse]]:
        """
        Filestore 인스턴스 리소스를 수집합니다 (v1 API).

        Args:
            params: 수집 파라미터
                - secret_data: 인증 정보
                - options: 옵션 설정

        Returns:
            성공한 리소스 응답 리스트와 에러 응답 리스트
        """
        _LOGGER.debug("** Filestore Instance START **")
        start_time = time.time()

        resource_responses = []
        error_responses = []
        instance_id = ""

        secret_data = params.get("secret_data", {})
        project_id = secret_data.get("project_id", "")

        try:
            ##################################
            # 0. Filestore Instance Connector 초기화 (v1 API만)
            ##################################
            self.instance_conn: FilestoreInstanceConnector = self.locator.get_connector(
                self.connector_name, **params
            )

            # Filestore 인스턴스 목록 조회 (v1 API)
            filestore_instances = self.instance_conn.list_instances()

            ##################################
            # 1. 각 Filestore 인스턴스 처리 (v1 API 데이터만)
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
                    # 3. Filestore 인스턴스 리소스 생성 (v1 API 데이터만)
                    ##################################
                    resource = self.get_filestore_instance_resource(
                        project_id, location, filestore_instance
                    )

                    ##################################
                    # 4. 리소스 응답 객체 생성
                    ##################################
                    response = FilestoreInstanceResponse({"resource": resource})
                    resource_responses.append(response)

                except Exception as e:
                    _LOGGER.error(
                        f"Failed to process instance {instance_id}: {e}",
                        exc_info=True,
                    )
                    error_response = ErrorResourceResponse.create_with_logging(
                        error_message=str(e),
                        error_code=type(e).__name__,
                        resource_type="inventory.CloudService",
                        additional_data={
                            "cloud_service_group": "Filestore",
                            "cloud_service_type": "Instance",
                            "instance_id": instance_id,
                        },
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(f"Failed to initialize Filestore collection: {e}")
            error_response = ErrorResourceResponse.create_with_logging(
                error_message=str(e),
                error_code=type(e).__name__,
                resource_type="inventory.CloudService",
                additional_data={
                    "cloud_service_group": "Filestore",
                    "cloud_service_type": "Instance",
                },
            )
            error_responses.append(error_response)

        _LOGGER.debug(
            f"** Filestore Instances Finished {time.time() - start_time} Seconds **"
        )
        return resource_responses, error_responses

    def get_filestore_instance_resource(
        self, project_id: str, location: str, instance: Dict[str, Any]
    ) -> FilestoreInstanceResource:
        """
        Filestore 인스턴스 리소스 객체를 생성합니다 (v1 API 데이터만).

        Args:
            project_id: 프로젝트 ID
            location: 리전
            instance: Filestore 인스턴스 정보 (v1 API)

        Returns:
            Filestore 인스턴스 리소스 객체
        """
        # 기본 인스턴스 정보 추출
        instance_name = instance.get("name", "")
        instance_id = instance.get("name", "").split("/")[-1]
        state = instance.get("state", "")
        description = instance.get("description", "")
        tier = instance.get("tier", "")

        # 네트워크 정보 처리
        network_info = self._process_network_info(instance.get("networks", []))

        # 파일 공유 정보 처리 (v1 API 기본 정보만)
        file_share_info, total_capacity_gb = self._process_file_share_info(
            instance.get("fileShares", [])
        )

        # 라벨 정보 처리
        labels = instance.get("labels", {})
        label_list = [{"key": k, "value": v} for k, v in labels.items()]

        # 스냅샷 정보 수집 (v1 API)
        snapshots = self._collect_snapshots(instance_name, instance_id)

        # 모니터링 정보 설정
        google_cloud_filters = [
            {"key": "resource.labels.instance_id", "value": instance_id}
        ]

        # 리소스 데이터 구성 (v1 API 데이터만)
        instance_data = self._build_instance_data(
            instance_id,
            instance_name,
            state,
            description,
            location,
            tier,
            instance,
            network_info,
            file_share_info,
            snapshots,
            labels,
            total_capacity_gb,
            len(network_info),
            project_id,
            google_cloud_filters,
        )

        # FilestoreInstanceData 객체 생성
        instance_data_obj = FilestoreInstanceData(instance_data, strict=False)

        # FilestoreInstanceResource 객체 생성
        resource_data = {
            "name": instance_id,
            "account": project_id,
            "instance_type": tier,
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
            raise e from e

    def _process_network_info(
        self, networks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """네트워크 정보를 처리합니다."""
        network_info = []
        for network in networks:
            network_info.append(
                {
                    "network": network.get("network", ""),
                    "modes": network.get("modes", []),
                    "reserved_ip_range": network.get("reservedIpRange", ""),
                }
            )
        return network_info

    def _process_file_share_info(
        self, file_shares: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], int]:
        """파일 공유 정보를 처리합니다 (v1 API 기본 정보만)."""
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

        return file_share_info, total_capacity_gb

    def _collect_snapshots(
        self, instance_name: str, instance_id: str
    ) -> List[Dict[str, Any]]:
        """인스턴스의 스냅샷 정보를 수집합니다 (v1 API)."""
        snapshots = []
        try:
            instance_snapshots = self.instance_conn.list_snapshots_for_instance(
                instance_name
            )

            for snapshot in instance_snapshots:
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

        return snapshots

    def _build_instance_data(
        self,
        instance_id: str,
        instance_name: str,
        state: str,
        description: str,
        location: str,
        tier: str,
        instance: Dict[str, Any],
        network_info: List[Dict[str, Any]],
        file_share_info: List[Dict[str, Any]],
        snapshots: List[Dict[str, Any]],
        labels: Dict[str, Any],
        total_capacity_gb: int,
        network_count: int,
        project_id: str,
        google_cloud_filters: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """인스턴스 데이터를 구성합니다."""
        return {
            "name": instance_id,
            "full_name": instance_name,
            "instance_id": instance_id,
            "state": state,
            "description": description,
            "location": location,
            "tier": tier,
            "networks": network_info,
            "file_shares": file_share_info,
            "snapshots": snapshots,
            "labels": labels,
            "create_time": self._convert_google_cloud_datetime(
                instance.get("createTime", "")
            ),
            "update_time": self._convert_google_cloud_datetime(
                instance.get("updateTime", "")
            ),
            "stats": {
                "total_capacity_gb": total_capacity_gb,
                "file_share_count": len(file_share_info),
                "snapshot_count": len(snapshots),
                "network_count": network_count,
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

    def _extract_file_share_from_snapshot_name(self, snapshot_name: str) -> str:
        """
        스냅샷 이름에서 파일 공유 정보를 추출합니다.

        Args:
            snapshot_name: 스냅샷 이름

        Returns:
            파일 공유 이름
        """
        try:
            # 예: projects/my-project/locations/us-central1/instances/my-instance/
            # fileShares/my-share/snapshots/my-snapshot
            parts = snapshot_name.split("/")
            if len(parts) >= 10 and parts[6] == "fileShares":
                return parts[7]
            return "unknown"
        except Exception:
            return "unknown"
