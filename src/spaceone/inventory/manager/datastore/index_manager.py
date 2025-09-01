import logging

from spaceone.inventory.connector.datastore.index_v1 import DatastoreIndexV1Connector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.datastore.index.cloud_service import (
    DatastoreIndexResource,
    DatastoreIndexResponse,
)
from spaceone.inventory.model.datastore.index.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.datastore.index.data import DatastoreIndexData

_LOGGER = logging.getLogger(__name__)


class DatastoreIndexManager(GoogleCloudManager):
    """
    Google Cloud Datastore Index Manager

    Datastore Index 리소스를 수집하고 처리하는 매니저 클래스
    - Index 목록 수집 (프로젝트 레벨)
    - Index 상세 정보 처리
    - 리소스 응답 생성

    주의: Datastore Admin API 한계로 인해 다중 데이터베이스 지원이 제한됨
    """

    connector_name = "DatastoreIndexV1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    index_conn = None

    def collect_cloud_service(self, params):
        """
        Datastore Index 리소스를 수집합니다.

        Args:
            params (dict): 수집 파라미터
                - secret_data: 인증 정보
                - options: 옵션 설정

        Returns:
            Tuple[List[DatastoreIndexResponse], List[ErrorResourceResponse]]:
                성공한 리소스 응답 리스트와 에러 응답 리스트
        """
        _LOGGER.debug("** Datastore Index START **")

        resource_responses = []
        error_responses = []

        try:
            # Connector 초기화
            self.index_conn: DatastoreIndexV1Connector = self.locator.get_connector(
                self.connector_name, **params
            )

            # 모든 index 조회 (프로젝트 레벨)
            indexes = self._list_indexes()

            # 각 index에 대해 리소스 생성
            for index_data in indexes:
                try:
                    resource_response = self._make_index_response(index_data, params)
                    resource_responses.append(resource_response)
                except Exception as e:
                    index_id = index_data.get("index_id", "unknown")
                    _LOGGER.error(f"Failed to process index {index_id}: {e}")
                    error_response = self.generate_error_response(
                        e, "Datastore", "Index", index_id
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(f"Failed to collect Datastore indexes: {e}")
            error_response = self.generate_error_response(e, "Datastore", "Index")
            error_responses.append(error_response)

        _LOGGER.debug("** Datastore Index END **")
        return resource_responses, error_responses

    def _list_indexes(self):
        """
        프로젝트의 모든 index를 조회합니다.

        Returns:
            List[dict]: index 정보 목록
        """
        indexes = []

        try:
            # 모든 index 조회 (프로젝트 레벨)
            raw_indexes = self.index_conn.list_indexes()

            for index in raw_indexes:
                # 각 index에 대해 추가 정보 수집
                index_data = self._process_index_data(index)
                if index_data:
                    indexes.append(index_data)

            _LOGGER.info(f"Found {len(indexes)} total indexes")

        except Exception as e:
            _LOGGER.error(f"Error listing indexes: {e}")
            raise e

        return indexes

    def _process_index_data(self, index):
        """
        Index 데이터를 처리하고 필요한 정보를 추가합니다.

        Args:
            index (dict): 원본 index 데이터

        Returns:
            dict: 처리된 index 데이터
        """
        try:
            # 기본 정보 추출
            index_id = index.get("indexId", "")
            kind = index.get("kind", "")
            ancestor = index.get("ancestor", "NONE")
            state = index.get("state", "")
            properties = index.get("properties", [])

            # Properties 분석
            property_count = len(properties)
            sorted_properties = []
            unsorted_properties = []

            for prop in properties:
                prop_name = prop.get("name", "")
                direction = prop.get("direction", "ASCENDING")
                if direction in ["ASCENDING", "DESCENDING"]:
                    sorted_properties.append(f"{prop_name} ({direction})")
                else:
                    unsorted_properties.append(prop_name)

            # 처리된 데이터 구성
            processed_data = {
                "index_id": index_id,
                "kind": kind,
                "ancestor": ancestor,
                "state": state,
                "properties": properties,
                "property_count": property_count,
                "sorted_properties": sorted_properties,
                "unsorted_properties": unsorted_properties,
                "project_id": self.index_conn.project_id,
                "display_name": f"{kind} Index ({index_id})"
                if kind
                else f"Index ({index_id})",
                # 원본 데이터도 포함
                "raw_data": index,
            }

            return processed_data

        except Exception as e:
            _LOGGER.error(f"Error processing index data: {e}")
            return None

    def _make_index_response(self, index_data, params):
        """
        Index 데이터를 기반으로 리소스 응답을 생성합니다.

        Args:
            index_data (dict): index 데이터
            params (dict): 수집 파라미터

        Returns:
            DatastoreIndexResponse: index 리소스 응답
        """
        index_id = index_data["index_id"]
        project_id = index_data["project_id"]

        # 리소스 ID 생성
        resource_id = f"{project_id}:{index_id}"

        # 리소스 데이터 생성
        index_data_obj = DatastoreIndexData(index_data, strict=False)

        # 리소스 생성
        resource = DatastoreIndexResource(
            {
                "name": index_data["display_name"],
                "account": project_id,
                "data": index_data_obj,
                "region_code": "global",
                "reference": ReferenceModel(
                    {
                        "resource_id": resource_id,
                        "external_link": f"https://console.cloud.google.com/datastore/indexes?project={project_id}",
                    }
                ),
            }
        )

        # 응답 생성
        return DatastoreIndexResponse({"resource": resource})
