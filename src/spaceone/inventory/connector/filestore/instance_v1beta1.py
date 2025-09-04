import logging
from typing import Any, Dict, List

from spaceone.inventory.libs.connector import GoogleCloudConnector

_LOGGER = logging.getLogger(__name__)


class FilestoreInstanceV1Beta1Connector(GoogleCloudConnector):
    """
    Google Cloud Filestore Instance Connector (v1beta1 API)

    Filestore 인스턴스 및 파일 공유 관련 API 호출을 담당하는 클래스
    - 인스턴스 목록 조회 (v1beta1 API)
    - 파일 공유 목록 조회 (v1beta1 API)
    - 스냅샷 목록 조회 (v1beta1 API)
    """

    google_client_service = "file"
    version = "v1beta1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_instances(self, **query) -> List[Dict[str, Any]]:
        """
        Filestore 인스턴스 목록을 조회합니다 (v1beta1 API).
        멀티쉐어 기능을 지원하는 인스턴스 정보를 포함합니다.

        Args:
            **query: 추가 쿼리 파라미터 (location, filter 등)

        Returns:
            Filestore 인스턴스 목록 (v1beta1 API 응답)
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
                    for instance in response["instances"]:
                        # 인스턴스 이름에서 리전 정보 추출
                        location = self._extract_location_from_instance_name(
                            instance.get("name", "")
                        )
                        instance["location"] = location
                        instances.append(instance)

                # 다음 페이지가 있는지 확인
                request = (
                    self.client.projects()
                    .locations()
                    .instances()
                    .list_next(previous_request=request, previous_response=response)
                )

            return instances

        except Exception as e:
            _LOGGER.error(f"Error listing Filestore instances (v1beta1): {e}")
            raise e from e

    def list_shares_for_instance(
        self, instance_name: str, **query
    ) -> List[Dict[str, Any]]:
        """
        특정 인스턴스의 파일 공유 목록을 조회합니다.
        Google Cloud Filestore v1beta1 API를 사용합니다.

        Args:
            instance_name: 인스턴스 이름
                (projects/{project}/locations/{location}/instances/{instance})
            **query: 추가 쿼리 파라미터

        Returns:
            파일 공유 목록
        """
        try:
            shares = []
            request = (
                self.client.projects()
                .locations()
                .instances()
                .shares()
                .list(parent=instance_name, **query)
            )

            while request is not None:
                response = request.execute()

                # 응답에서 파일 공유 목록 추출
                if "shares" in response:
                    shares.extend(response["shares"])

                # 다음 페이지가 있는지 확인
                request = (
                    self.client.projects()
                    .locations()
                    .instances()
                    .shares()
                    .list_next(previous_request=request, previous_response=response)
                )

            return shares

        except Exception as e:
            _LOGGER.error(f"Error listing shares for instance {instance_name}: {e}")
            raise e from e

    def list_snapshots_for_instance(
        self, instance_name: str, **query
    ) -> List[Dict[str, Any]]:
        """
        특정 인스턴스의 스냅샷 목록을 조회합니다 (v1beta1 API).

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
                    snapshots.extend(response["snapshots"])

                # 다음 페이지가 있는지 확인
                request = (
                    self.client.projects()
                    .locations()
                    .instances()
                    .snapshots()
                    .list_next(previous_request=request, previous_response=response)
                )

            return snapshots

        except Exception as e:
            _LOGGER.error(f"Error listing snapshots for instance {instance_name}: {e}")
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
