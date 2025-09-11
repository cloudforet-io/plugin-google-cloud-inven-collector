import logging
import time
from typing import List, Tuple

from spaceone.inventory.connector.firestore.database_v1 import (
    FirestoreDatabaseConnector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.firestore.index.cloud_service import (
    IndexResource,
    IndexResponse,
)
from spaceone.inventory.model.firestore.index.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.firestore.index.data import FirestoreIndex

_LOGGER = logging.getLogger(__name__)


class FirestoreIndexManager(GoogleCloudManager):
    """
    Google Cloud Firestore Index Manager

    Firestore Index 리소스를 수집하고 처리하는 매니저 클래스
    - Index 목록 수집 (__로 시작하는 필드 제외)
    - Index 상세 정보 처리
    - 리소스 응답 생성
    """

    connector_name = "FirestoreDatabaseConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    firestore_conn = None

    def collect_cloud_service(self, params) -> Tuple[List[IndexResponse], List]:
        """
        Firestore Index 리소스를 수집합니다.

        Args:
            params (dict): 수집 파라미터
                - secret_data: 인증 정보
                - options: 옵션 설정

        Returns:
            Tuple[List[IndexResponse], List[ErrorResourceResponse]]:
                성공한 리소스 응답 리스트와 에러 응답 리스트
        """
        _LOGGER.debug("** Firestore Index START **")
        start_time = time.time()

        collected_cloud_services = []
        error_responses = []
        database_id = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        try:
            ##################################
            # 0. Gather All Related Resources
            ##################################
            self.firestore_conn: FirestoreDatabaseConnector = (
                self.locator.get_connector(self.connector_name, **params)
            )

            # 데이터베이스 목록 조회
            databases = self.firestore_conn.list_databases()
            _LOGGER.info(f"Found {len(databases)} Firestore databases")

            # 순차 처리: 데이터베이스별 인덱스 수집
            for database in databases:
                try:
                    ##################################
                    # 1. Set Basic Information
                    ##################################
                    database_name = database.get("name", "")
                    database_id = (
                        database_name.split("/")[-1]
                        if "/" in database_name
                        else database_name
                    )
                    region_code = database.get("locationId", "global")

                    ##################################
                    # 2. Make Base Data
                    ##################################
                    index_resources = self._create_index_resources_for_database(
                        database_name,
                        database_id,
                        project_id,
                        region_code,
                    )

                    ##################################
                    # 3. Make Return Resource & 5. Make Resource Response Object
                    ##################################
                    collected_cloud_services.extend(index_resources)

                    ##################################
                    # 4. Make Collected Region Code
                    ##################################
                    self.set_region_code(region_code)

                except Exception as e:
                    _LOGGER.error(
                        f"Failed to process database {database_id}: {e}",
                        exc_info=True,
                    )
                    error_response = self.generate_resource_error_response(
                        e, "Firestore", "Index", database_id
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(f"Failed to collect Firestore indexes: {e}")
            error_response = self.generate_resource_error_response(
                e, "Firestore", "Index"
            )
            error_responses.append(error_response)

        # 수집 완료 로깅
        _LOGGER.debug(
            f"** Firestore Index Finished {time.time() - start_time} Seconds **"
        )

        return collected_cloud_services, error_responses

    def _create_index_resources_for_database(
        self,
        database_name: str,
        database_id: str,
        project_id: str,
        region_code: str,
    ) -> List[IndexResponse]:
        """데이터베이스의 모든 인덱스 리소스를 생성합니다."""
        index_responses = []

        try:
            indexes = self.firestore_conn.list_indexes(database_name)

            for index in indexes:
                try:
                    index_name = index.get("name", "")
                    index_id = (
                        index_name.split("/")[-1] if "/" in index_name else index_name
                    )

                    # __로 시작하는 필드 제외
                    original_fields = index.get("fields", [])
                    filtered_fields = FirestoreIndex.filter_internal_fields(
                        original_fields
                    )

                    # 필터링 후 필드가 없으면 인덱스 제외
                    if not filtered_fields:
                        continue

                    # 컬렉션 그룹 추출
                    collection_group = ""
                    if "/collectionGroups/" in index_name:
                        collection_group = index_name.split("/collectionGroups/")[
                            1
                        ].split("/")[0]

                    # 필드를 문자열 요약으로 변환
                    field_strings = []
                    for field in filtered_fields:
                        field_path = field.get("fieldPath", "")
                        order = field.get("order", "")
                        if field_path:
                            field_string = (
                                f"{field_path} ({order})" if order else field_path
                            )
                            field_strings.append(field_string)

                    fields_summary = (
                        ", ".join(field_strings) if field_strings else "No fields"
                    )

                    index.update(
                        {
                            "name": index_id,
                            "full_name": index_name,
                            "database_id": database_id,
                            "fields_summary": fields_summary,
                            "collection_group": collection_group,
                            "project": project_id,
                        }
                    )

                    index_data = FirestoreIndex(index, strict=False)

                    index_resource = IndexResource(
                        {
                            "name": index_id,
                            "account": project_id,
                            "region_code": region_code,
                            "data": index_data,
                            "reference": ReferenceModel(index_data.reference()),
                        }
                    )
                    index_responses.append(IndexResponse({"resource": index_resource}))

                except Exception as index_error:
                    _LOGGER.warning(
                        f"Failed to process index {index.get('name', 'unknown')}: {index_error}"
                    )
                    continue

        except Exception as e:
            _LOGGER.warning(f"Failed to create index resources: {e}")

        return index_responses
