import logging
import time

from spaceone.inventory.connector.datastore.database_v1 import (
    DatastoreDatabaseV1Connector,
)
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
        start_time = time.time()

        collected_cloud_services = []
        error_responses = []
        namespace_id = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        try:
            ##################################
            # 0. Gather All Related Resources
            ##################################
            self.namespace_conn: DatastoreNamespaceV1Connector = (
                self.locator.get_connector(self.connector_name, **params)
            )

            # DATASTORE_MODE 데이터베이스 정보 조회 (ID + locationId)
            database_infos = self._get_datastore_database_infos(params)

            # 모든 데이터베이스의 namespace 조회
            namespaces = self._list_namespaces_for_databases(database_infos)

            # 각 namespace에 대해 리소스 생성
            for namespace in namespaces:
                try:
                    ##################################
                    # 1. Set Basic Information
                    ##################################
                    namespace_id = namespace.get("namespace_id", "(default)")
                    display_name = namespace_id or "Default Namespace"
                    region_code = namespace.get("location_id", "global")

                    ##################################
                    # 2. Make Base Data
                    ##################################
                    # 추가 처리된 정보 업데이트 (이미 _get_namespace_data에서 처리됨)
                    namespace.update(
                        {
                            "project": project_id,
                        }
                    )
                    namespace_data = DatastoreNamespaceData(namespace, strict=False)

                    ##################################
                    # 3. Make Return Resource
                    ##################################
                    namespace_resource = DatastoreNamespaceResource(
                        {
                            "name": display_name,
                            "account": project_id,
                            "data": namespace_data,
                            "region_code": region_code,
                            "reference": ReferenceModel(namespace_data.reference()),
                        }
                    )

                    ##################################
                    # 4. Make Collected Region Code
                    ##################################
                    self.set_region_code(region_code)

                    ##################################
                    # 5. Make Resource Response Object
                    ##################################
                    collected_cloud_services.append(
                        DatastoreNamespaceResponse({"resource": namespace_resource})
                    )

                except Exception as e:
                    _LOGGER.error(f"Failed to process namespace {namespace_id}: {e}")
                    error_response = self.generate_resource_error_response(
                        e, "Datastore", "Namespace", namespace_id
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(f"Failed to collect Datastore namespaces: {e}")
            error_response = self.generate_resource_error_response(
                e, "Datastore", "Namespace"
            )
            error_responses.append(error_response)

        # 수집 완료 로깅
        _LOGGER.debug(
            f"** Datastore Namespace Finished {time.time() - start_time} Seconds **"
        )
        return collected_cloud_services, error_responses

    def _list_namespaces_for_databases(self, database_infos):
        """
        여러 데이터베이스의 모든 namespace를 조회하고 각 namespace의 kind 목록을 포함하여 반환합니다.

        Args:
            database_infos (List[dict]): 조회할 데이터베이스 정보 목록 (database_id, location_id)

        Returns:
            List[dict]: 모든 데이터베이스의 namespace 정보 목록
        """
        all_namespaces = []

        try:
            # 각 데이터베이스별로 네임스페이스 조회
            for database_info in database_infos:
                database_id = database_info["database_id"]
                location_id = database_info["location_id"]
                try:
                    # 모든 namespace 목록 조회
                    response = self.namespace_conn.list_namespaces(database_id)

                    # API 응답에서 namespace 목록 추출 (사용자 생성 namespace만)
                    user_namespace_ids = (
                        self.namespace_conn.extract_namespaces_from_response(response)
                    )

                    # 전체 namespace 목록 생성 (기본 namespace + 사용자 생성 namespace)
                    all_namespace_ids = [
                        None
                    ] + user_namespace_ids  # None = 기본 namespace

                    # 모든 namespace에 대해 상세 정보 조회
                    for namespace_id in all_namespace_ids:
                        namespace_data = self._get_namespace_data(
                            namespace_id, database_id, location_id
                        )
                        if namespace_data:
                            all_namespaces.append(namespace_data)

                except Exception as e:
                    _LOGGER.error(
                        f"Error listing namespaces for database {database_id}: {e}"
                    )
                    # 에러가 발생해도 기본 namespace만이라도 시도
                    try:
                        default_namespace_data = self._get_namespace_data(
                            None, database_id, location_id
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

    def _get_datastore_database_infos(self, params):
        """
        DATASTORE_MODE 데이터베이스의 정보(ID + locationId)를 반환합니다.

        Args:
            params (dict): 수집 파라미터

        Returns:
            List[dict]: 데이터베이스 정보 목록 (database_id, location_id)
        """
        try:
            database_conn: DatastoreDatabaseV1Connector = self.locator.get_connector(
                "DatastoreDatabaseV1Connector", **params
            )

            # 데이터베이스 목록 조회
            datastore_databases = database_conn.list_databases()

            # 데이터베이스 정보 목록 생성
            database_infos = []
            for database in datastore_databases:
                name = database.get("name", "")
                database_id = name.split("/")[-1] if "/" in name else name
                location_id = database.get("locationId", "global")

                if database_id:  # 빈 문자열이 아닌 경우만 추가
                    database_infos.append(
                        {"database_id": database_id, "location_id": location_id}
                    )

            # 빈 목록인 경우 기본 데이터베이스 추가
            if not database_infos:
                database_infos.append(
                    {"database_id": "(default)", "location_id": "global"}
                )

            _LOGGER.info(f"Found {len(database_infos)} DATASTORE_MODE databases")
            return database_infos

        except Exception as e:
            _LOGGER.error(f"Error getting datastore database infos: {e}")
            return [
                {"database_id": "(default)", "location_id": "global"}
            ]  # 에러 발생 시 기본 데이터베이스 반환

    def _get_namespace_data(
        self, namespace_id, database_id="(default)", location_id="global"
    ):
        """
        특정 데이터베이스의 특정 namespace에서 상세 정보와 kind 목록을 조회합니다.

        Args:
            namespace_id (str): namespace ID (None인 경우 기본 namespace)
            database_id (str): 데이터베이스 ID (기본값: "(default)")
            location_id (str): 데이터베이스 위치 ID (기본값: "global")

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
                "location_id": location_id,  # 데이터베이스 위치 ID 추가
            }

            return namespace_data

        except Exception as e:
            _LOGGER.error(
                f"Error getting namespace data for '{namespace_id}' in database '{database_id}': {e}"
            )
            return None
