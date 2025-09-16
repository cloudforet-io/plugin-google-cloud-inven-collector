import logging
import time
from typing import Any, Dict, List, Tuple

from spaceone.inventory.connector.filestore.instance_v1 import (
    FilestoreInstanceConnector,
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

    def collect_cloud_service(
        self, params
    ) -> Tuple[List[FilestoreInstanceResponse], List]:
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

        collected_cloud_services = []
        error_responses = []
        instance_id = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        try:
            ##################################
            # 0. Gather All Related Resources
            ##################################
            self.instance_conn: FilestoreInstanceConnector = self.locator.get_connector(
                self.connector_name, **params
            )

            # Get Filestore instances (v1 API)
            filestore_instances = self.instance_conn.list_instances()

            for filestore_instance in filestore_instances:
                try:
                    ##################################
                    # 1. Set Basic Information
                    ##################################
                    instance_name = filestore_instance.get("name", "")
                    instance_id = (
                        instance_name.split("/")[-1]
                        if "/" in instance_name
                        else instance_name
                    )
                    location = filestore_instance.get("location", "")

                    ##################################
                    # 2. Make Base Data
                    ##################################
                    # 파일 공유 정보 처리 및 용량 계산
                    unified_file_shares, total_capacity_gb = (
                        self._process_file_shares_directly(
                            filestore_instance.get("fileShares", [])
                        )
                    )

                    # 기본 정보 추출
                    labels = self.convert_labels_format(
                        filestore_instance.get("labels", {})
                    )

                    # 네트워크 및 스냅샷 정보 수집
                    networks = self._process_networks(
                        filestore_instance.get("networks", [])
                    )
                    snapshots = self._collect_snapshots(instance_name, instance_id)

                    # 원본 데이터 기반으로 업데이트
                    filestore_instance.update(
                        {
                            "project": project_id,
                            "name": instance_id,
                            "full_name": instance_name,
                            "instance_id": instance_id,
                            "location": location,
                            "networks": networks,
                            "unified_file_shares": unified_file_shares,
                            "snapshots": snapshots,
                            "labels": labels,
                            "stats": {
                                "total_capacity_gb": str(total_capacity_gb),
                                "file_share_count": str(len(unified_file_shares)),
                                "snapshot_count": str(len(snapshots)),
                                "network_count": str(len(networks)),
                            },
                            "custom_performance_supported": str(
                                filestore_instance.get(
                                    "customPerformanceSupported", False
                                )
                            ).lower()
                            if filestore_instance.get("customPerformanceSupported")
                            is not None
                            else None,
                            "performance_limits": self._process_performance_limits(
                                filestore_instance.get("performanceLimits", {})
                            ),
                            "google_cloud_monitoring": self.set_google_cloud_monitoring(
                                project_id,
                                "file.googleapis.com/nfs/server/free_raw_capacity_percent",
                                instance_id,
                                [
                                    {
                                        "key": "resource.labels.instance_name",
                                        "value": instance_id,
                                    }
                                ],
                            ),
                            "google_cloud_logging": self.set_google_cloud_logging(
                                "Filestore", "Instance", project_id, instance_id
                            ),
                        }
                    )

                    instance_data = FilestoreInstanceData(
                        filestore_instance, strict=False
                    )

                    ##################################
                    # 3. Make Return Resource
                    ##################################
                    instance_resource = FilestoreInstanceResource(
                        {
                            "name": instance_id,
                            "account": project_id,
                            "instance_type": filestore_instance.get("tier", ""),
                            "instance_size": total_capacity_gb,
                            "tags": labels,
                            "region_code": location,
                            "data": instance_data,
                            "reference": ReferenceModel(instance_data.reference()),
                        }
                    )

                    ##################################
                    # 4. Make Collected Region Code
                    ##################################
                    self.set_region_code(location)

                    ##################################
                    # 5. Make Resource Response Object
                    ##################################
                    collected_cloud_services.append(
                        FilestoreInstanceResponse({"resource": instance_resource})
                    )

                except Exception as e:
                    _LOGGER.error(
                        f"Failed to process instance {instance_id}: {e}",
                        exc_info=True,
                    )
                    error_response = self.generate_resource_error_response(
                        e, "Filestore", "Instance", instance_id
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(f"Failed to collect Filestore instances: {e}", exc_info=True)
            error_response = self.generate_resource_error_response(
                e, "Filestore", "Instance", "collection"
            )
            error_responses.append(error_response)

        _LOGGER.debug(
            f"** Filestore Instance Finished {time.time() - start_time} Seconds **"
        )
        return collected_cloud_services, error_responses

    def _process_networks(self, networks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """네트워크 정보를 처리합니다."""
        network_info = []
        for network in networks:
            network_info.append(
                {
                    "network": network.get("network", ""),
                    "modes": network.get("modes", []),
                    "reserved_ip_range": network.get("reservedIpRange", ""),
                    "connect_mode": network.get("connectMode", ""),
                }
            )
        return network_info

    def _process_file_shares_directly(
        self, file_shares: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], int]:
        """파일 공유 정보를 처리합니다."""
        unified_shares = []
        total_capacity_gb = 0

        for file_share in file_shares:
            capacity_gb = int(file_share.get("capacityGb", 0))
            total_capacity_gb += capacity_gb

            unified_shares.append(
                {
                    "name": file_share.get("name", ""),
                    "capacity_gb": str(
                        capacity_gb
                    ),  # StringType 필드이므로 문자열로 변환
                    "source_backup": file_share.get("sourceBackup", ""),
                    "nfs_export_options": file_share.get("nfsExportOptions", []),
                    "data_source": "Basic",
                }
            )

        return unified_shares, total_capacity_gb

    def _process_performance_limits(
        self, performance_limits: Dict[str, Any]
    ) -> Dict[str, str]:
        """성능 제한 정보를 처리합니다."""
        if not performance_limits:
            return None

        return {
            "max_read_iops": performance_limits.get("maxReadIops") or None,
            "max_write_iops": performance_limits.get("maxWriteIops") or None,
            "max_read_throughput_bps": performance_limits.get("maxReadThroughputBps")
            or None,
            "max_write_throughput_bps": performance_limits.get("maxWriteThroughputBps")
            or None,
            "max_iops": performance_limits.get("maxIops") or None,
        }

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
                # (name, description, state, createTime, labels)
                name = snapshot.get("name", "")
                snapshot_id = name.split("/")[-1] if "/" in name else name
                snapshot.update(
                    {
                        "name": snapshot_id,
                        "full_name": name,
                        "create_time": snapshot.get("createTime", ""),
                        "labels": self.convert_labels_format(
                            snapshot.get("labels", {})
                        ),
                    }
                )
                snapshots.append(snapshot)

        except Exception as e:
            _LOGGER.warning(
                f"Failed to collect snapshots for instance {instance_id}: {e}"
            )

        return snapshots
