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

        collected_cloud_services = []
        error_responses = []
        index_id = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        try:
            ##################################
            # 0. Gather All Related Resources
            ##################################
            index_conn: DatastoreIndexV1Connector = self.locator.get_connector(
                self.connector_name, **params
            )

            # 모든 index 조회 (프로젝트 레벨)
            indexes = index_conn.list_indexes()
            _LOGGER.info(f"Found {len(indexes)} total indexes")

            # 각 index에 대해 리소스 생성
            for index in indexes:
                try:
                    ##################################
                    # 1. Set Basic Information
                    ##################################
                    index_id = index.get("indexId", "")

                    ##################################
                    # 2. Make Base Data
                    ##################################
                    # Properties 분석
                    properties = index.get("properties", [])
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

                    # 추가 처리된 정보 업데이트
                    index.update(
                        {
                            "property_count": property_count,
                            "sorted_properties": sorted_properties,
                            "unsorted_properties": unsorted_properties,
                            "project": project_id,
                        }
                    )

                    index_data = DatastoreIndexData(index, strict=False)

                    ##################################
                    # 3. Make Return Resource
                    ##################################
                    index_resource = DatastoreIndexResource(
                        {
                            "name": index_id,
                            "account": project_id,
                            "data": index_data,
                            "region_code": "global",
                            "reference": ReferenceModel(index_data.reference()),
                        }
                    )

                    ##################################
                    # 4. Make Collected Region Code
                    ##################################
                    self.set_region_code("global")

                    ##################################
                    # 5. Make Resource Response Object
                    ##################################
                    collected_cloud_services.append(
                        DatastoreIndexResponse({"resource": index_resource})
                    )

                except Exception as e:
                    _LOGGER.error(f"Failed to process index {index_id}: {e}")
                    error_response = self.generate_resource_error_response(
                        e, "Datastore", "Index", index_id
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(f"Failed to collect Datastore indexes: {e}")
            error_response = self.generate_resource_error_response(
                e, "Datastore", "Index"
            )
            error_responses.append(error_response)

        _LOGGER.debug("** Datastore Index END **")
        return collected_cloud_services, error_responses
