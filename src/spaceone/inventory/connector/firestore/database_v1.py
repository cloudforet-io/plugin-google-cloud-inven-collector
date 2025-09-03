import logging
from typing import List

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["FirestoreDatabaseConnector"]
_LOGGER = logging.getLogger(__name__)


class FirestoreDatabaseConnector(GoogleCloudConnector):
    google_client_service = "firestore"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._database_clients = {}  # 데이터베이스별 클라이언트 캐시

    def _get_admin_client(self, database_id="(default)"):
        """Firestore Admin SDK 클라이언트를 lazy loading으로 초기화합니다.

        Args:
            database_id: 데이터베이스 ID (기본값: "(default)")

        Returns:
            Admin SDK 클라이언트 (데이터베이스별 캐시됨)
        """
        # 데이터베이스별 클라이언트 캐싱
        if database_id not in self._database_clients:
            try:
                from google.cloud import firestore

                # 데이터베이스별 클라이언트 생성
                if database_id == "(default)":
                    # 기본 데이터베이스 클라이언트
                    client = firestore.Client(
                        project=self.project_id, credentials=self.credentials
                    )
                else:
                    # 특정 데이터베이스 클라이언트
                    client = firestore.Client(
                        project=self.project_id,
                        database=database_id,
                        credentials=self.credentials,
                    )

                self._database_clients[database_id] = client

            except ImportError:
                _LOGGER.error(
                    "google-cloud-firestore library not found. "
                    "Please install: pip install google-cloud-firestore"
                )
                raise
            except Exception as e:
                _LOGGER.error(
                    f"Failed to initialize Firestore Admin SDK client for {database_id}: {e}"
                )
                raise

        return self._database_clients[database_id]

    def list_databases(self, **query):
        """Firestore 데이터베이스 목록을 조회합니다.

        Args:
            **query: 추가 쿼리 파라미터

        Returns:
            List[dict]: 데이터베이스 목록
        """
        database_list = []
        query.update({"parent": f"projects/{self.project_id}"})

        request = self.client.projects().databases().list(**query)
        while request is not None:
            response = request.execute()
            all_databases = response.get("databases", [])
            # FIRESTORE_NATIVE 타입만 필터링
            firestore_databases = list(
                filter(lambda db: db.get("type") == "FIRESTORE_NATIVE", all_databases)
            )
            database_list.extend(firestore_databases)
            # 페이지네이션 처리 - list_next가 있는지 확인
            try:
                request = (
                    self.client.projects()
                    .databases()
                    .list_next(previous_request=request, previous_response=response)
                )
            except AttributeError:
                # list_next가 없는 경우 첫 페이지만 처리
                break

        return database_list

    def list_indexes(self, database_name, **query):
        """데이터베이스의 인덱스 목록을 조회합니다.

        Args:
            database_name: 데이터베이스 이름
            **query: 추가 쿼리 파라미터

        Returns:
            List[dict]: 인덱스 목록
        """
        indexes = []
        parent = f"{database_name}/collectionGroups/-"

        query.update({"parent": parent})

        request = (
            self.client.projects()
            .databases()
            .collectionGroups()
            .indexes()
            .list(**query)
        )
        while request is not None:
            response = request.execute()
            indexes.extend(response.get("indexes", []))
            # 페이지네이션 처리 - list_next가 있는지 확인
            try:
                request = (
                    self.client.projects()
                    .databases()
                    .collectionGroups()
                    .indexes()
                    .list_next(previous_request=request, previous_response=response)
                )
            except AttributeError:
                # list_next가 없는 경우 첫 페이지만 처리
                break

        return indexes

    def list_collections_with_documents(self, database_name, parent="", **query):
        """컬렉션 ID와 각 컬렉션의 문서들을 한 번에 조회합니다. (최적화된 통합 메서드)

        이 메서드는 기존 list_collection_ids + list_documents의 중복 호출을 방지하여
        동일한 parent에 대한 admin_client.document() 호출을 최적화합니다.

        Args:
            database_name: 데이터베이스 이름
            parent: 부모 문서 경로 (빈 문자열이면 최상위)
            **query: 추가 쿼리 파라미터

        Returns:
            List[dict]: 컬렉션 정보와 문서들을 포함한 딕셔너리 목록
            [
                {
                    "collection_id": str,
                    "documents": List[dict],
                }
            ]
        """
        try:
            # 데이터베이스 ID 추출
            database_id = "(default)"
            if "/databases/" in database_name:
                database_id = database_name.split("/databases/")[-1]

            # 🎯 최적화: 데이터베이스별 캐시된 클라이언트 사용
            admin_client = self._get_admin_client(database_id)

            collections_with_docs = []
            page_size = query.get("pageSize", 100)

            if not parent:
                # 최상위 컬렉션들 처리
                collections = admin_client.collections()

                for collection in collections:
                    collection_id = collection.id

                    # 해당 컬렉션의 문서들 조회
                    documents = []
                    try:
                        docs_stream = collection.limit(page_size).stream()
                        for doc in docs_stream:
                            doc_dict = {
                                "name": doc.reference.path,
                                "fields": doc.to_dict(),
                                "createTime": doc.create_time.isoformat()
                                if doc.create_time
                                else None,
                                "updateTime": doc.update_time.isoformat()
                                if doc.update_time
                                else None,
                            }
                            documents.append(doc_dict)
                    except Exception as e:
                        _LOGGER.warning(
                            f"Failed to get documents for collection {collection_id}: {e}"
                        )

                    collections_with_docs.append(
                        {
                            "collection_id": collection_id,
                            "documents": documents,
                        }
                    )

            else:
                # 하위 컬렉션들 처리 (단일 document() 호출로 최적화)
                parent_doc_ref = admin_client.document(parent)  # 한 번만 호출!

                # 하위 컬렉션들 조회
                subcollections = parent_doc_ref.collections()

                for collection in subcollections:
                    collection_id = collection.id

                    # 해당 컬렉션의 문서들 조회 (이미 얻은 collection 참조 사용)
                    documents = []
                    try:
                        docs_stream = collection.limit(page_size).stream()
                        for doc in docs_stream:
                            doc_dict = {
                                "name": doc.reference.path,
                                "fields": doc.to_dict(),
                                "createTime": doc.create_time.isoformat()
                                if doc.create_time
                                else None,
                                "updateTime": doc.update_time.isoformat()
                                if doc.update_time
                                else None,
                            }
                            documents.append(doc_dict)
                    except Exception as e:
                        _LOGGER.warning(
                            f"Failed to get documents for subcollection {collection_id}: {e}"
                        )

                    collections_with_docs.append(
                        {
                            "collection_id": collection_id,
                            "documents": documents,
                        }
                    )

            _LOGGER.debug(
                f"Retrieved {len(collections_with_docs)} collections with documents"
            )
            return collections_with_docs

        except Exception as e:
            _LOGGER.error(
                f"Failed to list collections with documents using Admin SDK for parent '{parent}': {e}"
            )
            return []

    def list_backup_schedules(self, database_name: str, **query) -> List[dict]:
        """데이터베이스의 백업 스케줄 목록을 조회합니다.

        Args:
            database_name: 데이터베이스 이름 (projects/{project}/databases/{database} 형식)
            **query: 추가 쿼리 파라미터

        Returns:
            List[dict]: 백업 스케줄 목록
        """
        backup_schedules = []

        try:
            query.update({"parent": database_name})

            request = self.client.projects().databases().backupSchedules().list(**query)

            while request is not None:
                response = request.execute()
                backup_schedules.extend(response.get("backupSchedules", []))

                # 페이지네이션 처리
                try:
                    request = (
                        self.client.projects()
                        .databases()
                        .backupSchedules()
                        .list_next(previous_request=request, previous_response=response)
                    )
                except AttributeError:
                    # list_next가 없는 경우 첫 페이지만 처리
                    break

            _LOGGER.debug(
                f"Retrieved {len(backup_schedules)} backup schedules for {database_name}"
            )
            return backup_schedules

        except Exception as e:
            _LOGGER.error(f"Failed to list backup schedules for {database_name}: {e}")
            return []

    def list_all_backups(self, **query) -> List[dict]:
        """프로젝트의 모든 위치에서 백업 목록을 조회합니다.

        location='-'를 사용하여 모든 위치의 백업을 한 번에 효율적으로 조회합니다.

        Args:
            **query: 추가 쿼리 파라미터

        Returns:
            List[dict]: 모든 위치의 백업 목록
        """
        backups = []

        try:
            # location='-'를 사용하여 모든 위치의 백업을 한 번에 조회
            parent = f"projects/{self.project_id}/locations/-"
            query.update({"parent": parent})

            request = self.client.projects().locations().backups().list(**query)

            while request is not None:
                response = request.execute()
                backups.extend(response.get("backups", []))

                # 페이지네이션 처리
                try:
                    request = (
                        self.client.projects()
                        .locations()
                        .backups()
                        .list_next(previous_request=request, previous_response=response)
                    )
                except AttributeError:
                    # list_next가 없는 경우 첫 페이지만 처리
                    break

            _LOGGER.info(
                f"Retrieved {len(backups)} backups from all locations for project {self.project_id}"
            )
            return backups

        except Exception as e:
            _LOGGER.error(
                f"Failed to list backups from all locations for project {self.project_id}: {e}"
            )
            return []
