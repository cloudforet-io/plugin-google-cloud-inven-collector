import logging
from typing import Any, Dict, List

from googleapiclient.errors import HttpError

from spaceone.inventory.libs.connector import GoogleCloudConnector

_LOGGER = logging.getLogger(__name__)


class FilestoreBackupConnector(GoogleCloudConnector):
    """
    Google Cloud Filestore Backup Connector (v1 API)

    Filestore 백업 관련 API 호출을 담당하는 클래스
    - 모든 리전의 백업 조회 (v1 API)
    """

    google_client_service = "file"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_backups(self, **query) -> List[Dict[str, Any]]:
        """
        모든 리전의 Filestore 백업 목록을 조회합니다.
        Google Cloud Filestore v1 API의 locations/- 와일드카드를 사용하여
        모든 리전의 백업을 한 번에 조회합니다.

        Args:
            **query: 추가 쿼리 파라미터 (filter, orderBy 등)

        Returns:
            Filestore 백업 목록
        """
        try:
            # 모든 리전의 Filestore 백업을 한 번에 조회
            # API 문서:
            # https://cloud.google.com/filestore/docs/reference/rest/v1/projects.locations.backups/list
            # "To retrieve backup information for all locations,
            # use "-" for the {location} value."
            backups = []

            request = (
                self.client.projects()
                .locations()
                .backups()
                .list(
                    parent=f"projects/{self.project_id}/locations/-",
                    **query,
                )
            )

            while request is not None:
                response = request.execute()

                # 응답에서 백업 목록 추출
                if "backups" in response:
                    for backup in response["backups"]:
                        # 백업 이름에서 리전 정보 추출
                        # 예: projects/my-project/locations/us-central1/backups/my-backup
                        location = self._extract_location_from_backup_name(
                            backup.get("name", "")
                        )
                        backup["location"] = location
                        backups.append(backup)

                # 다음 페이지가 있는지 확인
                request = (
                    self.client.projects()
                    .locations()
                    .backups()
                    .list_next(previous_request=request, previous_response=response)
                )

            return backups

        except HttpError as e:
            if e.resp.status == 404:
                _LOGGER.warning(
                    f"Filestore backup service not available for project {self.project_id}"
                )
                return []
            elif e.resp.status == 403:
                _LOGGER.warning(
                    f"Filestore API not enabled or insufficient permissions for project {self.project_id}"
                )
                return []
            else:
                _LOGGER.error(
                    f"HTTP error listing Filestore backups for project {self.project_id}: {e}"
                )
                raise e
        except Exception as e:
            _LOGGER.error(
                f"Error listing Filestore backups for project {self.project_id}: {e}"
            )
            raise e from e

    def _extract_location_from_backup_name(self, backup_name: str) -> str:
        """
        백업 이름에서 리전 정보를 추출합니다.

        Args:
            backup_name: 백업 이름
                (projects/{project}/locations/{location}/backups/{backup})

        Returns:
            리전 정보
        """
        try:
            # 예: projects/my-project/locations/us-central1/backups/my-backup
            parts = backup_name.split("/")
            if len(parts) >= 6 and parts[2] == "locations":
                return parts[3]
            return "unknown"
        except Exception:
            return "unknown"
