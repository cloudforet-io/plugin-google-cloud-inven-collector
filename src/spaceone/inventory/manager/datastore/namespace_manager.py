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

            # Database Manager를 사용하여 DATASTORE_MODE 데이터베이스 ID 목록 조회
            from spaceone.inventory.manager.datastore.database_manager import (
                DatastoreDatabaseManager,
            )

            database_manager = DatastoreDatabaseManager()
            database_ids = database_manager.get_datastore_database_ids(params)

            # 모든 데이터베이스의 namespace 조회
            namespaces = self._list_namespaces_for_databases(database_ids)

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

    def _list_namespaces_for_databases(self, database_ids):
        """
        여러 데이터베이스의 모든 namespace를 조회하고 각 namespace의 kind 목록을 포함하여 반환합니다.

        Args:
            database_ids (List[str]): 조회할 데이터베이스 ID 목록

        Returns:
            List[dict]: 모든 데이터베이스의 namespace 정보 목록
        """
        all_namespaces = []

        try:
            # 각 데이터베이스별로 네임스페이스 조회
            for database_id in database_ids:
                try:
                    # 모든 namespace 목록 조회
                    response = self.namespace_conn.list_namespaces(database_id)

                    # API 응답에서 namespace 목록 추출
                    namespace_ids = (
                        self.namespace_conn.extract_namespaces_from_response(response)
                    )

                    # 기본 namespace (빈 namespace) 처리
                    default_namespace_data = self._get_namespace_data(None, database_id)
                    if default_namespace_data:
                        all_namespaces.append(default_namespace_data)

                    # 각 namespace별로 상세 정보 조회
                    for namespace_id in namespace_ids:
                        namespace_data = self._get_namespace_data(
                            namespace_id, database_id
                        )
                        if namespace_data:
                            all_namespaces.append(namespace_data)

                    _LOGGER.info(
                        f"Found {len(namespace_ids) + 1} namespaces for database {database_id}"
                    )

                except Exception as e:
                    _LOGGER.error(
                        f"Error listing namespaces for database {database_id}: {e}"
                    )
                    # 에러가 발생해도 기본 namespace는 시도
                    try:
                        default_namespace_data = self._get_namespace_data(
                            None, database_id
                        )
                        if default_namespace_data:
                            all_namespaces.append(default_namespace_data)
                    except Exception as default_e:
                        _LOGGER.error(
                            f"Error getting default namespace for database {database_id}: {default_e}"
                        )
                    continue

            _LOGGER.info(
                f"Found {len(all_namespaces)} total namespaces across all databases"
            )

        except Exception as e:
            _LOGGER.error(f"Error listing namespaces for databases: {e}")
            raise e

        return all_namespaces

    def _list_namespaces(self):
        """
        기본 데이터베이스의 모든 namespace를 조회합니다. (하위 호환성을 위해 유지)

        Returns:
            List[dict]: namespace 정보 목록
        """
        return self._list_namespaces_for_databases(["(default)"])

    def _get_namespace_data(self, namespace_id, database_id="(default)"):
        """
        특정 데이터베이스의 특정 namespace에서 상세 정보와 kind 목록을 조회합니다.

        Args:
            namespace_id (str): namespace ID (None인 경우 기본 namespace)
            database_id (str): 데이터베이스 ID (기본값: "(default)")

        Returns:
            dict: namespace 데이터
        """
        try:
            kinds = self.namespace_conn.get_namespace_kinds(namespace_id, database_id)

            namespace_data = {
                "namespace_id": namespace_id
                or "(default)",  # 기본 namespace는 (default)
                "display_name": namespace_id or "Default Namespace",
                "kinds": kinds,
                "kind_count": len(kinds),
                "database_id": database_id,  # 데이터베이스 ID 추가
                "project_id": self.namespace_conn.project_id,
                "created_time": datetime.utcnow().strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ),  # Datastore API doesn't provide creation time
            }

            return namespace_data

        except Exception as e:
            _LOGGER.error(
                f"Error getting namespace data for '{namespace_id}' in database '{database_id}': {e}"
            )
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
        project_id = namespace_data["project_id"]

        # 리소스 데이터 생성
        namespace_data_obj = DatastoreNamespaceData(namespace_data, strict=False)

        # 리소스 생성
        resource = DatastoreNamespaceResource(
            {
                "name": namespace_data["display_name"],
                "account": project_id,
                "data": namespace_data_obj,
                "region_code": "global",
                "reference": ReferenceModel(namespace_data_obj.reference()),
            }
        )

        # 응답 생성
        return DatastoreNamespaceResponse({"resource": resource})
