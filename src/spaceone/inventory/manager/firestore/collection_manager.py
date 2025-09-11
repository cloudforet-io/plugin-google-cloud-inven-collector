import logging
import time
from typing import List, Tuple

from spaceone.inventory.connector.firestore.database_v1 import (
    FirestoreDatabaseConnector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.firestore.collection.cloud_service import (
    CollectionResource,
    CollectionResponse,
)
from spaceone.inventory.model.firestore.collection.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.firestore.collection.data import (
    DocumentInfo,
    FirestoreCollection,
)

_LOGGER = logging.getLogger(__name__)


class FirestoreCollectionManager(GoogleCloudManager):
    """
    Google Cloud Firestore Collection Manager

    Firestore Collection 리소스를 수집하고 처리하는 매니저 클래스
    - Collection 목록 수집 (재귀적으로 하위 컬렉션까지)
    - Collection별 문서 정보 수집
    - 리소스 응답 생성
    """

    connector_name = "FirestoreDatabaseConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    firestore_conn = None

    def collect_cloud_service(self, params) -> Tuple[List[CollectionResponse], List]:
        """
        Firestore Collection 리소스를 수집합니다.

        Args:
            params (dict): 수집 파라미터
                - secret_data: 인증 정보
                - options: 옵션 설정

        Returns:
            Tuple[List[CollectionResponse], List[ErrorResourceResponse]]:
                성공한 리소스 응답 리스트와 에러 응답 리스트
        """
        _LOGGER.debug("** Firestore Collection START **")
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

            # 순차 처리: 데이터베이스별 컬렉션 수집
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
                    collection_resources = (
                        self._create_collection_resources_for_database(
                            database_name,
                            database_id,
                            project_id,
                            region_code,
                        )
                    )

                    ##################################
                    # 3. Make Return Resource & 5. Make Resource Response Object
                    ##################################
                    collected_cloud_services.extend(collection_resources)

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
                        e, "Firestore", "Collection", database_id
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(f"Failed to collect Firestore collections: {e}")
            error_response = self.generate_resource_error_response(
                e, "Firestore", "Collection"
            )
            error_responses.append(error_response)

        # 수집 완료 로깅
        _LOGGER.debug(
            f"** Firestore Collection Finished {time.time() - start_time} Seconds **"
        )

        return collected_cloud_services, error_responses

    def _create_collection_resources_for_database(
        self,
        database_name: str,
        database_id: str,
        project_id: str,
        region_code: str,
    ) -> List[CollectionResponse]:
        """데이터베이스의 모든 컬렉션 리소스를 생성합니다."""
        collection_responses = []

        try:
            # 모든 컬렉션을 재귀적으로 수집
            all_collections = self._collect_all_collections_recursively(
                database_name, "", 0
            )

            # 각 컬렉션별로 리소스 생성
            for collection_info in all_collections:
                try:
                    collection_id = collection_info["id"]
                    collection_path = collection_info["path"]
                    documents = collection_info["documents"]
                    depth_level = collection_info["depth_level"]
                    parent_document_path = collection_info.get(
                        "parent_document_path", ""
                    )
                    display_name = f"{database_id}/{collection_path}"

                    # 문서 정보 변환
                    document_infos = self._process_documents(documents)

                    collection_data_dict = {
                        "name": collection_id,
                        "project": project_id,
                        "full_name": display_name,
                        "database_id": database_id,
                        "collection_path": collection_path,
                        "documents": document_infos,
                        "document_count": len(document_infos),
                        "depth_level": depth_level,
                        "parent_document_path": parent_document_path,
                    }

                    collection_data = FirestoreCollection(
                        collection_data_dict, strict=False
                    )

                    collection_resource = CollectionResource(
                        {
                            "name": collection_id,
                            "account": project_id,
                            "region_code": region_code,
                            "data": collection_data,
                            "reference": ReferenceModel(collection_data.reference()),
                        }
                    )

                    collection_responses.append(
                        CollectionResponse({"resource": collection_resource})
                    )

                except Exception as collection_error:
                    _LOGGER.warning(
                        f"Failed to process collection {collection_info.get('id', 'unknown')}: {collection_error}"
                    )
                    continue

        except Exception as e:
            _LOGGER.warning(f"Failed to create collection resources: {e}")

        return collection_responses

    def _process_documents(self, documents: List[dict]) -> List[DocumentInfo]:
        """문서 정보를 처리합니다."""
        document_infos = []
        for doc in documents:
            try:
                doc_id = self._extract_document_id(doc.get("name", ""))

                # 복잡한 fields 구조를 문자열 요약으로 변환
                raw_fields = doc.get("fields", {})
                fields_summary = (
                    ", ".join(
                        [f"{k}: {type(v).__name__}" for k, v in raw_fields.items()]
                    )
                    if raw_fields
                    else "No fields"
                )

                document_info = DocumentInfo(
                    {
                        "document_id": doc_id,
                        "document_name": doc.get("name", ""),
                        "fields_summary": fields_summary,
                        "create_time": doc.get("createTime", ""),
                        "update_time": doc.get("updateTime", ""),
                    }
                )
                document_infos.append(document_info)
            except Exception as doc_error:
                _LOGGER.warning(
                    f"Failed to process document {doc.get('name', 'unknown')}: {doc_error}"
                )
                continue
        return document_infos

    def _collect_all_collections_recursively(
        self,
        database_name: str,
        parent_document_path: str,
        depth_level: int,
    ) -> List[dict]:
        """모든 컬렉션을 재귀적으로 수집 (최적화: 중복 호출 제거)"""
        all_collections = []

        try:
            # 컬렉션 ID + 문서들을 한 번에 조회 (중복 호출 제거)
            collections_with_docs = self.firestore_conn.list_collections_with_documents(
                database_name, parent_document_path
            )

            for collection_info in collections_with_docs:
                collection_id = collection_info["collection_id"]
                documents = collection_info["documents"]

                # 컬렉션 경로 생성
                if parent_document_path:
                    collection_path = f"{parent_document_path}/{collection_id}"
                else:
                    collection_path = collection_id

                collection_data = {
                    "id": collection_id,
                    "path": collection_path,
                    "documents": documents,
                    "depth_level": depth_level,
                    "parent_document_path": parent_document_path,
                }
                all_collections.append(collection_data)

                # 각 문서에 대해 하위 컬렉션 확인 (재귀)
                for document in documents:
                    document_path = self._extract_document_path(
                        document.get("name", "")
                    )

                    # 깊이 제한 (무한 재귀 방지)
                    if depth_level < 10:
                        sub_collections = self._collect_all_collections_recursively(
                            database_name, document_path, depth_level + 1
                        )
                        all_collections.extend(sub_collections)

        except Exception as e:
            _LOGGER.warning(
                f"Failed to collect collections at depth {depth_level}: {e}"
            )

        return all_collections

    @staticmethod
    def _extract_document_path(document_name: str) -> str:
        """문서 이름에서 경로 추출"""
        if "/documents/" in document_name:
            return document_name.split("/documents/")[-1]
        return document_name

    @staticmethod
    def _extract_document_id(document_name: str) -> str:
        """문서 이름에서 ID만 추출"""
        document_path = FirestoreCollectionManager._extract_document_path(document_name)
        return document_path.split("/")[-1] if "/" in document_path else document_path
