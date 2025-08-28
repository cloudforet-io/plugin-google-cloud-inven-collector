import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["FirestoreDatabaseConnector"]
_LOGGER = logging.getLogger(__name__)


class FirestoreDatabaseConnector(GoogleCloudConnector):
    google_client_service = "firestore"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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

    def list_collection_ids(self, database_name, parent="", **query):
        """지정된 부모 경로의 컬렉션 ID 목록을 조회합니다.

        Args:
            database_name: 데이터베이스 이름
            parent: 부모 문서 경로 (빈 문자열이면 최상위)
            **query: 추가 쿼리 파라미터

        Returns:
            List[str]: 컬렉션 ID 목록
        """
        collection_ids = []
        parent_path = (
            f"{database_name}/documents/{parent}"
            if parent
            else f"{database_name}/documents"
        )

        query.update({"parent": parent_path})

        request = (
            self.client.projects().databases().documents().listCollectionIds(**query)
        )
        while request is not None:
            response = request.execute()
            collection_ids.extend(response.get("collectionIds", []))
            # 페이지네이션 처리 - listCollectionIds_next가 있는지 확인
            try:
                request = (
                    self.client.projects()
                    .databases()
                    .documents()
                    .listCollectionIds_next(
                        previous_request=request, previous_response=response
                    )
                )
            except AttributeError:
                # listCollectionIds_next가 없는 경우 첫 페이지만 처리
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
