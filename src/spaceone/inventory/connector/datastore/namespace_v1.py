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

    def run_query(self, namespace_id=None, **query):
        """
        Datastore runQuery API를 사용하여 Namespace별 Kind 목록을 조회합니다.

        API 응답 구조:
        {
          "batch": {
            "skippedResults": integer,
            "entityResultType": enum (ResultType),
            "entityResults": [
              {
                "entity": {
                  "key": {
                    "partitionId": {
                      "projectId": string,
                      "namespaceId": string
                    },
                    "path": [
                      {
                        "kind": string,
                        "id": string,
                        "name": string
                      }
                    ]
                  }
                }
              }
            ],
            "endCursor": string,
            "moreResults": enum (MoreResultsType)
          }
        }

        Args:
            namespace_id (str): 조회할 namespace ID (None인 경우 기본 namespace)
            **query: 추가 쿼리 파라미터

        Returns:
            dict: runQuery API 응답
        """
        try:
            # Kind 목록을 조회하기 위한 쿼리 구성
            # __kind__ 엔티티를 조회하여 해당 namespace의 Kind 목록을 가져옴
            query_body = {
                "query": {
                    "kind": [{"name": "__kind__"}],
                    "projection": [{"property": {"name": "__key__"}}],
                }
            }

            # namespace가 지정된 경우 partitionId에 추가
            if namespace_id:
                query_body["partitionId"] = {"namespaceId": namespace_id}
            else:
                query_body["partitionId"] = {}

            request = self.client.projects().runQuery(
                projectId=self.project_id, body=query_body, **query
            )

            response = request.execute()
            _LOGGER.debug(
                f"runQuery response for namespace '{namespace_id}': {response}"
            )

            return response

        except Exception as e:
            _LOGGER.error(f"Error running query for namespace '{namespace_id}': {e}")
            raise e

    def list_namespaces(self, **query):
        """
        Datastore의 모든 namespace를 조회합니다.
        __namespace__ Kind를 쿼리하여 namespace 목록을 가져옵니다.

        Args:
            **query: 추가 쿼리 파라미터

        Returns:
            dict: runQuery API 응답 (namespace 목록 포함)
        """
        try:
            # Namespace 목록을 조회하기 위한 쿼리 구성
            # __namespace__ 엔티티를 조회하여 프로젝트의 모든 namespace를 가져옴
            query_body = {
                "query": {
                    "kind": [{"name": "__namespace__"}],
                    "projection": [{"property": {"name": "__key__"}}],
                },
                "partitionId": {},
            }

            request = self.client.projects().runQuery(
                projectId=self.project_id, body=query_body, **query
            )

            response = request.execute()
            _LOGGER.debug(f"Namespace list query response: {response}")

            return response

        except Exception as e:
            _LOGGER.error(f"Error listing namespaces: {e}")
            raise e

    def get_namespace_kinds(self, namespace_id=None):
        """
        특정 namespace의 Kind 목록을 조회합니다.

        Args:
            namespace_id (str): 조회할 namespace ID

        Returns:
            list: Kind 이름 목록
        """
        try:
            response = self.run_query(namespace_id=namespace_id)
            kinds = []

            # API 응답 구조에 따라 파싱
            if "batch" in response and "entityResults" in response["batch"]:
                for entity_result in response["batch"]["entityResults"]:
                    if "entity" in entity_result and "key" in entity_result["entity"]:
                        key = entity_result["entity"]["key"]
                        if "path" in key and len(key["path"]) > 0:
                            # path의 첫 번째 요소에서 kind 이름 추출
                            path_element = key["path"][0]
                            kind_name = path_element.get("name", "")
                            if kind_name:
                                kinds.append(kind_name)

            return kinds

        except Exception as e:
            _LOGGER.error(f"Error getting kinds for namespace '{namespace_id}': {e}")
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
