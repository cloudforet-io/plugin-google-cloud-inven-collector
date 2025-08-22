import logging
from datetime import datetime

from spaceone.inventory.connector.datastore.namespace_v1 import (
    DatastoreNamespaceV1Connector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.datastore.namespace.cloud_service import (
    DatastoreNamespaceResource,
    DatastoreNamespaceResponse,
)
from spaceone.inventory.model.datastore.namespace.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.datastore.namespace.data import DatastoreNamespaceData

_LOGGER = logging.getLogger(__name__)


class DatastoreNamespaceManager(GoogleCloudManager):
    """
    Google Cloud Datastore Namespace Manager

    Datastore Namespace 및 Kind 리소스를 수집하고 처리하는 매니저 클래스
    - Namespace 목록 수집
    - Namespace별 Kind 목록 수집
    - 리소스 응답 생성
    """

    connector_name = "DatastoreNamespaceV1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    namespace_conn = None

    def collect_cloud_service(self, params):
        """
        Datastore Namespace 리소스를 수집합니다.

        Args:
            params (dict): 수집 파라미터
                - secret_data: 인증 정보
                - options: 옵션 설정

        Returns:
            Tuple[List[DatastoreNamespaceResponse], List[ErrorResourceResponse]]:
                성공한 리소스 응답 리스트와 에러 응답 리스트
        """
        _LOGGER.debug("** Datastore Namespace START **")

        resource_responses = []
        error_responses = []

        try:
            # Connector 초기화
            self.namespace_conn: DatastoreNamespaceV1Connector = (
                self.locator.get_connector(self.connector_name, **params)
            )

            # 모든 namespace 조회
            namespaces = self._list_namespaces()

            # 각 namespace에 대해 리소스 생성
            for namespace_data in namespaces:
                try:
                    resource_response = self._make_namespace_response(
                        namespace_data, params
                    )
                    resource_responses.append(resource_response)
                except Exception as e:
                    _LOGGER.error(
                        f"Failed to process namespace {namespace_data.get('namespace_id', 'default')}: {e}"
                    )
                    error_response = self.generate_error_response(
                        e,
                        "Datastore",
                        "Namespace",
                        namespace_data.get("namespace_id", "default"),
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(f"Failed to collect Datastore namespaces: {e}")
            error_response = self.generate_error_response(e, "Datastore", "Namespace")
            error_responses.append(error_response)

        _LOGGER.debug("** Datastore Namespace END **")
        return resource_responses, error_responses

    def _list_namespaces(self):
        """
        Datastore의 모든 namespace를 조회하고 각 namespace의 kind 목록을 포함하여 반환합니다.

        Returns:
            List[dict]: namespace 정보 목록
        """
        namespaces = []

        try:
            # 먼저 기본 namespace (빈 namespace) 처리
            default_namespace_data = self._get_namespace_data(None)
            if default_namespace_data:
                namespaces.append(default_namespace_data)

            # 모든 namespace 조회
            response = self.namespace_conn.list_namespaces()

            # API 응답에서 namespace 목록 추출
            namespace_ids = self.namespace_conn.extract_namespaces_from_response(
                response
            )

            for namespace_id in namespace_ids:
                namespace_data = self._get_namespace_data(namespace_id)
                if namespace_data:
                    namespaces.append(namespace_data)

            _LOGGER.info(f"Found {len(namespaces)} namespaces")

        except Exception as e:
            _LOGGER.error(f"Error listing namespaces: {e}")
            # 에러가 발생해도 기본 namespace는 시도
            try:
                default_namespace_data = self._get_namespace_data(None)
                if default_namespace_data:
                    namespaces.append(default_namespace_data)
            except Exception as default_e:
                _LOGGER.error(f"Error getting default namespace: {default_e}")

        return namespaces

    def _get_namespace_data(self, namespace_id):
        """
        특정 namespace의 상세 정보와 kind 목록을 조회합니다.

        Args:
            namespace_id (str): namespace ID (None인 경우 기본 namespace)

        Returns:
            dict: namespace 데이터
        """
        try:
            kinds = self.namespace_conn.get_namespace_kinds(namespace_id)

            namespace_data = {
                "namespace_id": namespace_id or "(default)",
                "display_name": namespace_id or "Default Namespace",
                "kinds": kinds,
                "kind_count": len(kinds),
                "project_id": self.namespace_conn.project_id,
                "created_time": datetime.utcnow().strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ),  # Datastore API doesn't provide creation time
            }

            return namespace_data

        except Exception as e:
            _LOGGER.error(f"Error getting namespace data for '{namespace_id}': {e}")
            return None

    def _make_namespace_response(self, namespace_data, params):
        """
        Namespace 데이터를 기반으로 리소스 응답을 생성합니다.

        Args:
            namespace_data (dict): namespace 데이터
            params (dict): 수집 파라미터

        Returns:
            DatastoreNamespaceResponse: namespace 리소스 응답
        """
        namespace_id = namespace_data["namespace_id"]
        project_id = namespace_data["project_id"]

        # 리소스 ID 생성
        resource_id = f"{project_id}:{namespace_id}"

        # 리소스 데이터 생성
        namespace_data_obj = DatastoreNamespaceData(namespace_data, strict=False)

        # 리소스 생성
        resource = DatastoreNamespaceResource(
            {
                "name": namespace_data["display_name"],
                "account": project_id,
                "data": namespace_data_obj,
                "region_code": "global",
                "reference": ReferenceModel(
                    {
                        "resource_id": resource_id,
                        "external_link": f"https://console.cloud.google.com/datastore/entities;kind=__namespace__;ns={namespace_id}/query/kind?project={project_id}",
                    }
                ),
            }
        )

        # 응답 생성
        return DatastoreNamespaceResponse({"resource": resource})
