import logging
from typing import Any, Dict, List

from googleapiclient.errors import HttpError

from spaceone.inventory.libs.connector import GoogleCloudConnector

_LOGGER = logging.getLogger(__name__)


class FilestoreSnapshotConnector(GoogleCloudConnector):
    """
    Google Cloud Filestore Snapshot Connector (v1 API)

    Filestore 스냅샷 관련 API 호출을 담당하는 클래스
    - 모든 리전의 스냅샷 조회 (v1 API)
    - 특정 인스턴스의 스냅샷 조회 (v1 API)
    """

    google_client_service = "file"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_all_snapshots(self, **query) -> List[Dict[str, Any]]:
        """
        모든 리전의 Filestore 스냅샷 목록을 조회합니다.
        Google Cloud Filestore v1 API의 locations/- 와일드카드를 사용하여
        모든 리전의 스냅샷을 한 번에 조회합니다.

        Args:
            **query: 추가 쿼리 파라미터 (filter 등)

        Returns:
            Filestore 스냅샷 목록
        """
        try:
            # 모든 리전의 Filestore 스냅샷을 한 번에 조회
            # API 문서:
            # https://cloud.google.com/filestore/docs/reference/rest/v1/projects.locations.instances.snapshots/list
            snapshots = []

            # 먼저 모든 인스턴스 목록을 가져온 후, 각 인스턴스의 스냅샷을 조회
            instances = self._list_all_instances()

            for instance in instances:
                instance_name = instance.get("name", "")
                if instance_name:
                    instance_snapshots = self.list_snapshots_for_instance(
                        instance_name, **query
                    )
                    snapshots.extend(instance_snapshots)

            return snapshots

        except HttpError as e:
            if e.resp.status == 404:
                _LOGGER.warning(
                    f"Filestore service not available for project {self.project_id}"
                )
                return []
            elif e.resp.status == 403:
                _LOGGER.warning(
                    f"Filestore API not enabled or insufficient permissions for project {self.project_id}"
                )
                return []
            else:
                _LOGGER.error(
                    f"HTTP error listing Filestore snapshots for project {self.project_id}: {e}"
                )
                raise e
        except Exception as e:
            _LOGGER.error(
                f"Error listing Filestore snapshots for project {self.project_id}: {e}"
            )
            raise e from e

    def list_snapshots_for_instance(
        self, instance_name: str, **query
    ) -> List[Dict[str, Any]]:
        """
        특정 인스턴스의 스냅샷 목록을 조회합니다.
        Google Cloud Filestore v1 API를 사용합니다.

        Args:
            instance_name: 인스턴스 이름
                (projects/{project}/locations/{location}/instances/{instance})
            **query: 추가 쿼리 파라미터

        Returns:
            스냅샷 목록
        """
        try:
            snapshots = []
            request = (
                self.client.projects()
                .locations()
                .instances()
                .snapshots()
                .list(parent=instance_name, **query)
            )

            while request is not None:
                response = request.execute()

                # 응답에서 스냅샷 목록 추출
                if "snapshots" in response:
                    for snapshot in response["snapshots"]:
                        # 스냅샷에 인스턴스 정보 추가
                        snapshot["instance_name"] = instance_name
                        # 리전 정보 추출
                        location = self._extract_location_from_instance_name(
                            instance_name
                        )
                        snapshot["location"] = location
                        snapshots.append(snapshot)

                # 다음 페이지가 있는지 확인
                request = (
                    self.client.projects()
                    .locations()
                    .instances()
                    .snapshots()
                    .list_next(previous_request=request, previous_response=response)
                )

            return snapshots

        except HttpError as e:
            if e.resp.status == 404:
                _LOGGER.warning(
                    f"Filestore snapshot service not available for instance {instance_name}"
                )
                return []
            elif e.resp.status == 403:
                _LOGGER.warning(
                    f"Filestore API not enabled or insufficient permissions for instance {instance_name}"
                )
                return []
            else:
                _LOGGER.error(
                    f"HTTP error listing snapshots for instance {instance_name}: {e}"
                )
                raise e
        except Exception as e:
            _LOGGER.error(f"Error listing snapshots for instance {instance_name}: {e}")
            raise e from e

    def _list_all_instances(self, **query) -> List[Dict[str, Any]]:
        """
        모든 리전의 Filestore 인스턴스 목록을 조회합니다.
        (스냅샷 조회를 위한 헬퍼 메서드)

        Args:
            **query: 추가 쿼리 파라미터

        Returns:
            Filestore 인스턴스 목록
        """
        try:
            instances = []

            request = (
                self.client.projects()
                .locations()
                .instances()
                .list(
                    parent=f"projects/{self.project_id}/locations/-",
                    **query,
                )
            )

            while request is not None:
                response = request.execute()

                # 응답에서 인스턴스 목록 추출
                if "instances" in response:
                    instances.extend(response["instances"])

                # 다음 페이지가 있는지 확인
                request = (
                    self.client.projects()
                    .locations()
                    .instances()
                    .list_next(previous_request=request, previous_response=response)
                )

            return instances

        except HttpError as e:
            if e.resp.status in [404, 403]:
                return []
            else:
                raise e
        except Exception as e:
            raise e from e

    def _extract_location_from_instance_name(self, instance_name: str) -> str:
        """
        인스턴스 이름에서 리전 정보를 추출합니다.

        Args:
            instance_name: 인스턴스 이름
                (projects/{project}/locations/{location}/instances/{instance})

        Returns:
            리전 정보
        """
        try:
            # 예: projects/my-project/locations/us-central1/instances/my-instance
            parts = instance_name.split("/")
            if len(parts) >= 6 and parts[2] == "locations":
                return parts[3]
            return "unknown"
        except Exception:
            return "unknown"
