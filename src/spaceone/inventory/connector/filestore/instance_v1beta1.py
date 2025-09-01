import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

_LOGGER = logging.getLogger(__name__)


class FilestoreInstanceV1Beta1Connector(GoogleCloudConnector):
    """
    Google Cloud Filestore Instance v1beta1 Connector

    Filestore 파일 공유(shares) 관련 API 호출을 담당하는 클래스
    - 파일 공유 목록 조회 (v1beta1 API 사용)
    """

    google_client_service = "file"
    version = "v1beta1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_shares_for_instance(self, instance_name, **query):
        """
        특정 인스턴스의 파일 공유 목록을 조회합니다.
        Google Cloud Filestore v1beta1 API를 사용합니다.

        Args:
            instance_name (str): 인스턴스 이름
                (projects/{project}/locations/{location}/instances/{instance})
            **query: 추가 쿼리 파라미터

        Returns:
            list: 파일 공유 목록
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
            return []
