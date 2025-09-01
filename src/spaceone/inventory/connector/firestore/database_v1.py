import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["FirestoreDatabaseConnector"]
_LOGGER = logging.getLogger(__name__)


class FirestoreDatabaseConnector(GoogleCloudConnector):
    google_client_service = "firestore"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._admin_client = None

    def _get_admin_client(self):
        """Firestore Admin SDK 클라이언트를 lazy loading으로 초기화합니다."""
        if self._admin_client is None:
            try:
                from google.cloud import firestore

                # 동일한 credentials를 사용하여 Admin SDK 클라이언트 생성
                self._admin_client = firestore.Client(
                    project=self.project_id, credentials=self.credentials
                )
                _LOGGER.debug("Firestore Admin SDK client initialized")
            except ImportError:
                _LOGGER.error(
                    "google-cloud-firestore library not found. "
                    "Please install: pip install google-cloud-firestore"
                )
                raise
            except Exception as e:
                _LOGGER.error(f"Failed to initialize Firestore Admin SDK client: {e}")
                raise
        return self._admin_client

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

    def list_root_collections_with_admin_sdk(self, database_name):
        """Admin SDK를 사용하여 최상위 컬렉션 목록을 조회합니다.

        Args:
            database_name: 데이터베이스 이름 (예: projects/PROJECT/databases/DB_ID)

        Returns:
            List[str]: 최상위 컬렉션 ID 목록
        """
        try:
            admin_client = self._get_admin_client()

            # 데이터베이스 이름에서 database_id 추출
            if "/databases/" in database_name:
                database_id = database_name.split("/databases/")[-1]
            else:
                database_id = database_name

            # (default) 데이터베이스가 아닌 경우 database_id 지정
            if database_id != "(default)":
                # Admin SDK에서 특정 데이터베이스 지정 (v2.11.0+)
                try:
                    from google.cloud import firestore

                    admin_client = firestore.Client(
                        project=self.project_id,
                        database=database_id,
                        credentials=self.credentials,
                    )
                except Exception as e:
                    _LOGGER.warning(f"Failed to connect to database {database_id}: {e}")
                    return []

            # 최상위 컬렉션 조회
            collections = admin_client.collections()
            collection_ids = [collection.id for collection in collections]

            _LOGGER.debug(
                f"Found {len(collection_ids)} root collections: {collection_ids}"
            )
            return collection_ids

        except Exception as e:
            _LOGGER.warning(f"Failed to list root collections with Admin SDK: {e}")
            return []

    def list_collection_ids(self, database_name, parent="", **query):
        """지정된 부모 경로의 컬렉션 ID 목록을 조회합니다.

        Args:
            database_name: 데이터베이스 이름
            parent: 부모 문서 경로 (빈 문자열이면 최상위)
            **query: 추가 쿼리 파라미터

        Returns:
            List[str]: 컬렉션 ID 목록
        """
        # 최상위 컬렉션의 경우 Admin SDK 사용
        if not parent:
            _LOGGER.debug("Using Admin SDK for root collections")
            return self.list_root_collections_with_admin_sdk(database_name)

        # 문서 하위 컬렉션의 경우 REST API 사용
        _LOGGER.debug(f"Using REST API for subcollections under: {parent}")
        collection_ids = []
        parent_path = f"{database_name}/documents/{parent}"

        # 페이징을 위한 body 파라미터 설정
        body = {}
        if "pageSize" in query:
            body["pageSize"] = query.pop("pageSize")

        page_token = None

        while True:
            if page_token:
                body["pageToken"] = page_token

            # API 호출 시 parent는 URL 파라미터, 나머지는 body에 포함
            request = (
                self.client.projects()
                .databases()
                .documents()
                .listCollectionIds(parent=parent_path, body=body)
            )

            try:
                response = request.execute()
                collection_ids.extend(response.get("collectionIds", []))

                # 다음 페이지 토큰 확인
                page_token = response.get("nextPageToken")
                if not page_token:
                    break  # 더 이상 페이지가 없으면 종료

            except Exception as e:
                _LOGGER.error(
                    f"Failed to list collection IDs for parent '{parent}': {e}"
                )
                break

        return collection_ids

    def list_documents(self, database_name, collection_id, parent="", **query):
        """지정된 컬렉션의 문서 목록을 조회합니다.

        Args:
            database_name: 데이터베이스 이름
            collection_id: 컬렉션 ID
            parent: 부모 문서 경로
            **query: 추가 쿼리 파라미터

        Returns:
            List[dict]: 문서 목록
        """
        documents = []
        collection_path = (
            f"{database_name}/documents/{parent}/{collection_id}"
            if parent
            else f"{database_name}/documents/{collection_id}"
        )

        query.update({"parent": collection_path})

        request = self.client.projects().databases().documents().list(**query)
        while request is not None:
            response = request.execute()
            documents.extend(response.get("documents", []))
            request = (
                self.client.projects()
                .databases()
                .documents()
                .list_next(previous_request=request, previous_response=response)
            )

        return documents

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
