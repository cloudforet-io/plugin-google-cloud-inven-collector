import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

_LOGGER = logging.getLogger(__name__)


class DatastoreNamespaceV1Connector(GoogleCloudConnector):
    """
    Google Cloud Datastore Namespace Connector

    Datastore Namespace 및 Kind 관련 API 호출을 담당하는 클래스
    - Namespace 목록 조회
    - Namespace별 Kind 목록 조회

    API 버전: v1
    참고: https://cloud.google.com/datastore/docs/reference/data/rest/v1/projects/runQuery
    """

    google_client_service = "datastore"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run_query(self, namespace_id=None, database_id="(default)", **query):
        """
        특정 데이터베이스의 특정 namespace에서 Kind 목록을 조회합니다.
        __kind__ Kind를 쿼리하여 해당 namespace의 모든 Kind를 가져옵니다.

        Args:
            namespace_id (str): 조회할 namespace ID
            database_id (str): 데이터베이스 ID (기본값: "(default)")
            **query: 추가 쿼리 파라미터

        Returns:
            dict: runQuery API 응답 (Kind 목록 포함)
        """
        try:
            # Kind 목록을 조회하기 위한 쿼리 구성
            query_body = {
                "query": {
                    "kind": [{"name": "__kind__"}],
                }
            }

            # API 호출 시 (default)를 빈 문자열로 변환
            api_database_id = "" if database_id == "(default)" else database_id
            api_namespace_id = (
                ""
                if namespace_id == "(default)" or namespace_id is None
                else namespace_id
            )

            # databaseId는 항상 포함 (빈 문자열이라도)
            query_body["databaseId"] = api_database_id

            # namespaceId는 항상 partitionId에 포함 (빈 문자열이라도)
            query_body["partitionId"] = {"namespaceId": api_namespace_id}

            # Named database를 위한 routing header 설정
            headers = {}
            if api_database_id:  # 빈 문자열이 아닌 경우 (named database)
                headers["x-goog-request-params"] = (
                    f"project_id={self.project_id}&database_id={api_database_id}"
                )

            request = self.client.projects().runQuery(
                projectId=self.project_id, body=query_body, **query
            )

            # 헤더가 있는 경우 추가
            if headers:
                request.headers.update(headers)

            response = request.execute()
            _LOGGER.debug(
                f"runQuery response for namespace '{namespace_id}' in database '{database_id}': {response}"
            )

            return response

        except Exception as e:
            _LOGGER.error(
                f"Error running query for namespace '{namespace_id}' in database '{database_id}': {e}"
            )
            raise e

    def list_namespaces(self, database_id="(default)", **query):
        """
        특정 데이터베이스의 모든 namespace를 조회합니다.
        __namespace__ Kind를 쿼리하여 namespace 목록을 가져옵니다.

        Args:
            database_id (str): 데이터베이스 ID (기본값: "(default)")
            **query: 추가 쿼리 파라미터

        Returns:
            dict: runQuery API 응답 (namespace 목록 포함)
        """
        try:
            # Namespace 목록을 조회하기 위한 쿼리 구성
            # __namespace__ 엔티티를 조회하여 해당 데이터베이스의 모든 namespace를 가져옴
            query_body = {
                "query": {
                    "kind": [{"name": "__namespace__"}],
                },
            }

            # API 호출 시 (default)를 빈 문자열로 변환
            api_database_id = "" if database_id == "(default)" else database_id

            # databaseId는 항상 포함 (빈 문자열이라도)
            query_body["databaseId"] = api_database_id

            # Named database를 위한 routing header 설정
            headers = {}
            if api_database_id:  # 빈 문자열이 아닌 경우 (named database)
                headers["x-goog-request-params"] = (
                    f"project_id={self.project_id}&database_id={api_database_id}"
                )

            request = self.client.projects().runQuery(
                projectId=self.project_id, body=query_body, **query
            )

            # 헤더가 있는 경우 추가
            if headers:
                request.headers.update(headers)

            response = request.execute()
            _LOGGER.debug(
                f"Namespace list response for database '{database_id}': {response}"
            )

            return response

        except Exception as e:
            _LOGGER.error(f"Error listing namespaces for database {database_id}: {e}")
            raise e

    def get_namespace_kinds(self, namespace_id=None, database_id="(default)"):
        """
        특정 데이터베이스의 특정 namespace에서 Kind 목록을 조회합니다.

        Args:
            namespace_id (str): 조회할 namespace ID
            database_id (str): 데이터베이스 ID (기본값: "(default)")

        Returns:
            list: Kind 이름 목록
        """
        try:
            response = self.run_query(
                namespace_id=namespace_id, database_id=database_id
            )

            # API 응답 구조에 따라 파싱
            if "batch" in response and "entityResults" in response["batch"]:
                entity_results = response["batch"]["entityResults"]

                # __로 시작하지 않는 kind만 필터링
                all_kinds = []
                for entity_result in entity_results:
                    if "entity" in entity_result and "key" in entity_result["entity"]:
                        key = entity_result["entity"]["key"]
                        if "path" in key and len(key["path"]) > 0:
                            # path의 첫 번째 요소에서 kind 이름 추출
                            path_element = key["path"][0]
                            kind_name = path_element.get("name", "")
                            if kind_name:
                                all_kinds.append(kind_name)

                # __로 시작하지 않는 kind만 필터링 (for문 전에 처리)
                kinds = list(filter(lambda kind: not kind.startswith("__"), all_kinds))
            else:
                kinds = []

            return kinds

        except Exception as e:
            _LOGGER.error(
                f"Error getting kinds for namespace '{namespace_id}' in database '{database_id}': {e}"
            )
            raise e

    def extract_namespaces_from_response(self, response):
        """
        runQuery API 응답에서 namespace 목록을 추출합니다.

        Args:
            response (dict): runQuery API 응답

        Returns:
            list: namespace ID 목록
        """
        namespaces = []

        try:
            if "batch" in response and "entityResults" in response["batch"]:
                for entity_result in response["batch"]["entityResults"]:
                    if "entity" in entity_result and "key" in entity_result["entity"]:
                        key = entity_result["entity"]["key"]
                        if "path" in key and len(key["path"]) > 0:
                            # path의 첫 번째 요소에서 namespace 정보 추출
                            path_element = key["path"][0]
                            namespace_name = path_element.get("name", "")
                            namespace_id = path_element.get("id", "")

                            if namespace_name:
                                # 실제 사용자가 생성한 namespace만 수집 (name 필드가 있음)
                                namespaces.append(namespace_name)
                                _LOGGER.debug(
                                    f"Found user-created namespace: '{namespace_name}'"
                                )
                            elif namespace_id == "1":
                                # 기본 namespace는 스킵 (GCP 자체 생성)
                                _LOGGER.debug(
                                    f"Skipping default namespace (id: {namespace_id})"
                                )
                            else:
                                # 기타 ID namespace (혹시 있다면)
                                namespaces.append(f"namespace-{namespace_id}")
                                _LOGGER.debug(
                                    f"Found namespace with ID: '{namespace_id}'"
                                )

                            _LOGGER.debug(
                                f"Found namespace - name: '{namespace_name}', id: '{namespace_id}'"
                            )

            return namespaces

        except Exception as e:
            _LOGGER.error(f"Error extracting namespaces from response: {e}")
            return []
