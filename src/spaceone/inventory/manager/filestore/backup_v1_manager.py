import logging
import time
from typing import List, Tuple

from spaceone.inventory.connector.filestore.backup_v1 import (
    FilestoreBackupConnector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.filestore.backup.cloud_service import (
    FilestoreBackupResource,
    FilestoreBackupResponse,
)
from spaceone.inventory.model.filestore.backup.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.filestore.backup.data import FilestoreBackupData

_LOGGER = logging.getLogger(__name__)


class FilestoreBackupManager(GoogleCloudManager):
    """
    Google Cloud Filestore Backup Manager (v1 API)

    Filestore 백업 리소스를 수집하고 처리하는 매니저 클래스 (v1 API 전용)
    - 모든 리전의 백업 목록 수집 (v1 API)
    - 백업 상세 정보 처리 (v1 API)
    """

    connector_name = "FilestoreBackupConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    backup_conn = None

    def collect_cloud_service(
        self, params
    ) -> Tuple[List[FilestoreBackupResponse], List]:
        """
        Filestore 백업 리소스를 수집합니다 (v1 API).

        Args:
            params: 수집 파라미터
                - secret_data: 인증 정보
                - options: 옵션 설정

        Returns:
            성공한 리소스 응답 리스트와 에러 응답 리스트
        """
        _LOGGER.debug("** Filestore Backup START **")
        start_time = time.time()

        collected_cloud_services = []
        error_responses = []
        backup_id = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        try:
            ##################################
            # 0. Gather All Related Resources
            ##################################
            self.backup_conn: FilestoreBackupConnector = self.locator.get_connector(
                self.connector_name, **params
            )

            # Get Filestore backups (v1 API)
            filestore_backups = self.backup_conn.list_backups()

            for filestore_backup in filestore_backups:
                try:
                    ##################################
                    # 1. Set Basic Information
                    ##################################
                    backup_name = filestore_backup.get("name", "")
                    backup_id = (
                        backup_name.split("/")[-1]
                        if "/" in backup_name
                        else backup_name
                    )
                    location = filestore_backup.get("location", "")

                    ##################################
                    # 2. Make Base Data
                    ##################################
                    # 기본 정보 추출
                    labels = self.convert_labels_format(
                        filestore_backup.get("labels", {})
                    )

                    # 소스 인스턴스 정보 처리
                    source_instance = filestore_backup.get("sourceInstance", "")
                    source_instance_id = (
                        source_instance.split("/")[-1]
                        if "/" in source_instance
                        else source_instance
                    )

                    # 원본 데이터 기반으로 업데이트
                    filestore_backup.update(
                        {
                            "project": project_id,
                            "backup_id": backup_id,
                            "full_name": backup_name,
                            "location": location,
                            "source_instance": source_instance,
                            "source_instance_id": source_instance_id,
                            "labels": labels,
                        }
                    )

                    backup_data = FilestoreBackupData(filestore_backup, strict=False)

                    ##################################
                    # 3. Make Return Resource
                    ##################################
                    backup_resource = FilestoreBackupResource(
                        {
                            "name": backup_id,
                            "account": project_id,
                            "tags": labels,
                            "region_code": location,
                            "data": backup_data,
                            "reference": ReferenceModel(backup_data.reference()),
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
                        FilestoreBackupResponse({"resource": backup_resource})
                    )

                except Exception as e:
                    _LOGGER.error(
                        f"Failed to process backup {backup_id}: {e}",
                        exc_info=True,
                    )
                    error_response = self.generate_resource_error_response(
                        e, "Filestore", "Backup", backup_id
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(f"Failed to collect Filestore backups: {e}", exc_info=True)
            error_response = self.generate_resource_error_response(
                e, "Filestore", "Backup", "collection"
            )
            error_responses.append(error_response)

        _LOGGER.debug(
            f"** Filestore Backup Finished {time.time() - start_time} Seconds **"
        )
        return collected_cloud_services, error_responses
