import logging
import time
from typing import List, Tuple, Union

from spaceone.inventory.connector.firestore.database_v1 import (
    FirestoreDatabaseConnector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel

# Backup
from spaceone.inventory.model.firestore.backup.cloud_service import (
    BackupResource,
    BackupResponse,
)
from spaceone.inventory.model.firestore.backup.cloud_service_type import (
    CLOUD_SERVICE_TYPES as BACKUP_CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.firestore.backup.data import Backup

# BackupSchedule
from spaceone.inventory.model.firestore.backup_schedule.cloud_service import (
    BackupScheduleResource,
    BackupScheduleResponse,
)
from spaceone.inventory.model.firestore.backup_schedule.cloud_service_type import (
    CLOUD_SERVICE_TYPES as BACKUP_SCHEDULE_CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.firestore.backup_schedule.data import BackupSchedule

# Collection (with documents)
from spaceone.inventory.model.firestore.collection.cloud_service import (
    CollectionResource,
    CollectionResponse,
)
from spaceone.inventory.model.firestore.collection.cloud_service_type import (
    CLOUD_SERVICE_TYPES as COLLECTION_CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.firestore.collection.data import (
    DocumentInfo,
    FirestoreCollection,
)

# Database
from spaceone.inventory.model.firestore.database.cloud_service import (
    DatabaseResource,
    DatabaseResponse,
)

# Cloud Service Types
from spaceone.inventory.model.firestore.database.cloud_service_type import (
    CLOUD_SERVICE_TYPES as DATABASE_CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.firestore.database.data import Database

# Index
from spaceone.inventory.model.firestore.index.cloud_service import (
    IndexResource,
    IndexResponse,
)
from spaceone.inventory.model.firestore.index.cloud_service_type import (
    CLOUD_SERVICE_TYPES as INDEX_CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.firestore.index.data import FirestoreIndex

_LOGGER = logging.getLogger(__name__)

# 최종 응답 타입 정의 (새로운 타입 추가)
FirestoreResponse = Union[
    DatabaseResponse,
    CollectionResponse,
    IndexResponse,
    BackupScheduleResponse,
    BackupResponse,
]


class FirestoreManager(GoogleCloudManager):
    connector_name = "FirestoreDatabaseConnector"
    cloud_service_types = (
        DATABASE_CLOUD_SERVICE_TYPES
        + COLLECTION_CLOUD_SERVICE_TYPES
        + INDEX_CLOUD_SERVICE_TYPES
        + BACKUP_SCHEDULE_CLOUD_SERVICE_TYPES
        + BACKUP_CLOUD_SERVICE_TYPES
    )

    def collect_cloud_service(self, params) -> Tuple[List[FirestoreResponse], List]:
        """최종 요구사항에 맞는 Firestore 리소스 수집

        1. Database (각 데이터베이스별로)
        2. Collection (각 컬렉션별로 + 포함된 문서들)
        3. Index (각 인덱스별로, __로 시작하는 필드 제외)
        4. BackupSchedule (각 데이터베이스별 백업 스케줄)
        5. Backup (각 위치별 백업 목록)

        Returns:
            Tuple[List[FirestoreResponse], List]: 5가지 응답 타입 혼합 리스트, 에러 리스트
        """
        _LOGGER.debug("** Firestore Final Collection START **")
        start_time = time.time()

        all_resources = []
        error_responses = []

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        # Connector 초기화
        firestore_conn: FirestoreDatabaseConnector = self.locator.get_connector(
            self.connector_name, **params
        )

        # 데이터베이스 목록 조회
        databases = firestore_conn.list_databases()

        # 순차 처리: 데이터베이스별 리소스 수집
        for database in databases:
            try:
                database_id = self._extract_database_id(database.get("name", ""))
                database_name = database.get("name", "")
                region_code = self._extract_location_id(database.get("locationId", ""))

                # 1. Database 리소스 생성 (각 데이터베이스별로)
                database_resource = self._create_database_resource(
                    database, project_id, region_code
                )
                all_resources.append(DatabaseResponse({"resource": database_resource}))

                # 2. Collection 리소스들 생성 (각 컬렉션별로 + 포함된 문서들)
                collection_resources = self._create_collection_resources_with_documents(
                    firestore_conn,
                    database_name,
                    database_id,
                    project_id,
                    region_code,
                )
                all_resources.extend(collection_resources)

                # 3. Index 리소스들 생성 (각 인덱스별로, __필드 제외)
                index_resources = self._create_filtered_index_resources(
                    firestore_conn,
                    database_name,
                    database_id,
                    project_id,
                    region_code,
                )
                all_resources.extend(index_resources)

                # 4. BackupSchedule 리소스들 생성 (각 데이터베이스별)
                backup_schedule_resources = self._create_backup_schedule_resources(
                    firestore_conn,
                    database_name,
                    database_id,
                    project_id,
                    region_code,
                )
                all_resources.extend(backup_schedule_resources)

                # 리전 코드 설정
                self.set_region_code(region_code)

            except Exception as e:
                _LOGGER.error(
                    f"[collect_cloud_service] database_id => {database_id}, error => {e}",
                    exc_info=True,
                )
                error_response = self.generate_resource_error_response(
                    e, "Firestore", "Database", database_id
                )
                error_responses.append(error_response)

        # 최적화: 모든 위치의 백업을 한 번에 수집
        try:
            # 5. Backup 리소스들 생성 (모든 위치에서 한 번에)
            backup_resources = self._create_all_backup_resources(
                firestore_conn,
                project_id,
            )
            all_resources.extend(backup_resources)

        except Exception as e:
            _LOGGER.error(
                f"[collect_cloud_service] Failed to collect backups from all locations, error => {e}",
                exc_info=True,
            )
            error_response = self.generate_resource_error_response(
                e, "Firestore", "Backup", "all-locations"
            )
            error_responses.append(error_response)

        _LOGGER.debug(
            f"** Firestore Final Collection Finished {time.time() - start_time} Seconds **"
        )
        return all_resources, error_responses

    def _create_database_resource(
        self, database: dict, project_id: str, region_code: str
    ) -> DatabaseResource:
        """Database 리소스 생성 (기존과 동일)"""
        database_id = self._extract_database_id(database.get("name", ""))

        database_data = Database(
            {
                "id": database_id,
                "name": database.get("name", ""),
                "project_id": project_id,
                "location_id": database.get("locationId", ""),
                "type": database.get("type", ""),
                "concurrency_mode": database.get("concurrencyMode", ""),
                "app_engine_integration_mode": database.get(
                    "appEngineIntegrationMode", ""
                ),
                "create_time": database.get("createTime"),
                "update_time": database.get("updateTime"),
                "etag": database.get("etag", ""),
                "uid": database.get("uid", ""),
                "delete_protection_state": database.get("deleteProtectionState", ""),
                "point_in_time_recovery_enablement": database.get(
                    "pointInTimeRecoveryEnablement", ""
                ),
                "version_retention_period": database.get("versionRetentionPeriod", ""),
                "earliest_version_time": database.get("earliestVersionTime"),
            }
        )

        return DatabaseResource(
            {
                "name": database_id,
                "account": project_id,
                "region_code": region_code,
                "data": database_data,
                "reference": ReferenceModel(database_data.reference()),
            }
        )

    def _create_collection_resources_with_documents(
        self,
        connector: FirestoreDatabaseConnector,
        database_name: str,
        database_id: str,
        project_id: str,
        region_code: str,
    ) -> List[CollectionResponse]:
        """각 컬렉션별로 리소스 생성 (포함된 문서들과 함께)"""
        collection_responses = []

        try:
            # 모든 컬렉션을 재귀적으로 수집
            all_collections = self._collect_all_collections_recursively(
                connector, database_name, "", 0
            )

            # 각 컬렉션별로 리소스 생성
            for collection_info in all_collections:
                collection_id = collection_info["id"]
                collection_path = collection_info["path"]
                documents = collection_info["documents"]
                depth_level = collection_info["depth_level"]
                parent_document_path = collection_info.get("parent_document_path", "")

                # 문서 정보 변환
                document_infos = []
                for doc in documents:
                    try:
                        doc_id = self._extract_document_id(doc.get("name", ""))

                        # 복잡한 fields 구조를 문자열 요약으로 변환
                        raw_fields = doc.get("fields", {})
                        fields_summary = (
                            ", ".join(
                                [
                                    f"{k}: {type(v).__name__}"
                                    for k, v in raw_fields.items()
                                ]
                            )
                            if raw_fields
                            else "No fields"
                        )

                        # DocumentInfo 객체로 복원하되 에러 처리 추가
                        document_info = DocumentInfo(
                            {
                                "id": doc_id,
                                "name": doc.get("name", ""),
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

                # 컬렉션 데이터 생성
                collection_data = FirestoreCollection(
                    {
                        "collection_id": collection_id,
                        "database_id": database_id,
                        "project_id": project_id,
                        "collection_path": collection_path,
                        "documents": document_infos,
                        "document_count": len(document_infos),
                        "depth_level": depth_level,
                        "parent_document_path": parent_document_path,
                    }
                )

                collection_resource = CollectionResource(
                    {
                        "name": f"{database_id}/{collection_path}",
                        "account": project_id,
                        "region_code": region_code,
                        "data": collection_data,
                        "reference": ReferenceModel(collection_data.reference()),
                    }
                )

                collection_responses.append(
                    CollectionResponse({"resource": collection_resource})
                )

        except Exception as e:
            _LOGGER.warning(f"Failed to create collection resources: {e}")

        return collection_responses

    def _collect_all_collections_recursively(
        self,
        connector: FirestoreDatabaseConnector,
        database_name: str,
        parent_document_path: str,
        depth_level: int,
    ) -> List[dict]:
        """모든 컬렉션을 재귀적으로 수집 (최적화: 중복 호출 제거)"""
        all_collections = []

        try:
            # 🎯 최적화: 컬렉션 ID + 문서들을 한 번에 조회 (중복 호출 제거)
            collections_with_docs = connector.list_collections_with_documents(
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
                            connector, database_name, document_path, depth_level + 1
                        )
                        all_collections.extend(sub_collections)

        except Exception as e:
            _LOGGER.warning(
                f"Failed to collect collections at depth {depth_level}: {e}"
            )

        return all_collections

    def _create_filtered_index_resources(
        self,
        connector: FirestoreDatabaseConnector,
        database_name: str,
        database_id: str,
        project_id: str,
        region_code: str,
    ) -> List[IndexResponse]:
        """Index 리소스들 생성 (__로 시작하는 필드 제외)"""
        index_responses = []

        try:
            indexes = connector.list_indexes(database_name)

            for index in indexes:
                # __로 시작하는 필드 제외
                original_fields = index.get("fields", [])
                filtered_fields = FirestoreIndex.filter_internal_fields(original_fields)

                # 필터링 후 필드가 없으면 인덱스 제외
                if not filtered_fields:
                    continue

                # 필드를 문자열 요약으로 변환 (더 단순한 스키마용)
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

                # 컬렉션 그룹 추출
                collection_group = ""
                index_name = index.get("name", "")
                if "/collectionGroups/" in index_name:
                    collection_group = index_name.split("/collectionGroups/")[1].split(
                        "/"
                    )[0]

                index_data = FirestoreIndex(
                    {
                        "name": index_name,
                        "database_id": database_id,
                        "project_id": project_id,
                        "query_scope": index.get("queryScope", ""),
                        "api_scope": index.get("apiScope", ""),
                        "state": index.get("state", ""),
                        "density": index.get("density", ""),
                        "fields_summary": fields_summary,  # 필터링된 필드 사용
                        "collection_group": collection_group,
                    }
                )

                index_resource = IndexResource(
                    {
                        "name": f"{database_id}/{collection_group}/index",
                        "account": project_id,
                        "region_code": region_code,
                        "data": index_data,
                        "reference": ReferenceModel(index_data.reference()),
                    }
                )

                index_responses.append(IndexResponse({"resource": index_resource}))

        except Exception as e:
            _LOGGER.warning(f"Failed to create index resources: {e}")

        return index_responses

    def _create_backup_schedule_resources(
        self,
        connector: FirestoreDatabaseConnector,
        database_name: str,
        database_id: str,
        project_id: str,
        region_code: str,
    ) -> List[BackupScheduleResponse]:
        """BackupSchedule 리소스들 생성 (순차 처리)"""
        backup_schedule_responses = []

        try:
            backup_schedules = connector.list_backup_schedules(database_name)
            _LOGGER.info(
                f"Found {len(backup_schedules)} backup schedules for database {database_id}"
            )

            for backup_schedule in backup_schedules:
                try:
                    # BackupSchedule 이름에서 ID 추출
                    backup_schedule_name = backup_schedule.get("name", "")

                    # recurrence 타입 결정
                    recurrence_type = self._determine_recurrence_type(backup_schedule)

                    backup_schedule_data = BackupSchedule(
                        {
                            "name": backup_schedule_name,
                            "database_id": database_id,
                            "project_id": project_id,
                            "retention": backup_schedule.get("retention", ""),
                            "recurrence_type": recurrence_type,
                            "create_time": backup_schedule.get("createTime"),
                            "update_time": backup_schedule.get("updateTime"),
                            "uid": backup_schedule.get("uid", ""),
                        }
                    )

                    backup_schedule_resource = BackupScheduleResource(
                        {
                            "name": f"{database_id}/backup-schedule/{backup_schedule_name.split('/')[-1]}",
                            "account": project_id,
                            "region_code": region_code,
                            "data": backup_schedule_data,
                            "reference": ReferenceModel(
                                backup_schedule_data.reference()
                            ),
                        }
                    )

                    backup_schedule_responses.append(
                        BackupScheduleResponse({"resource": backup_schedule_resource})
                    )

                except Exception as schedule_error:
                    _LOGGER.warning(
                        f"Failed to process backup schedule {backup_schedule.get('name', 'unknown')}: {schedule_error}"
                    )
                    continue

        except Exception as e:
            _LOGGER.warning(
                f"Failed to create backup schedule resources for {database_id}: {e}"
            )

        return backup_schedule_responses

    def _create_all_backup_resources(
        self,
        connector: FirestoreDatabaseConnector,
        project_id: str,
    ) -> List[BackupResponse]:
        """모든 위치의 Backup 리소스들 생성 (최적화된 단일 API 호출)"""
        backup_responses = []

        try:
            # location='-'를 사용하여 모든 위치의 백업을 한 번에 조회
            backups = connector.list_all_backups()
            _LOGGER.info(
                f"Found {len(backups)} backups across all locations for project {project_id}"
            )

            for backup in backups:
                try:
                    # Backup 이름에서 ID 추출
                    backup_name = backup.get("name", "")
                    backup_database = backup.get("database", "")

                    # 백업 이름에서 위치 ID 추출 (projects/{project}/locations/{location}/backups/{backup})
                    location_id = self._extract_location_from_backup_name(backup_name)

                    backup_data = Backup(
                        {
                            "name": backup_name,
                            "database": backup_database,
                            "project_id": project_id,
                            "location_id": location_id,
                            "state": backup.get("state", ""),
                            "create_time": backup.get("createTime"),
                            "expire_time": backup.get("expireTime"),
                            "version_time": backup.get("versionTime"),
                            "size_bytes": backup.get("sizeBytes", 0),
                            "uid": backup.get("uid", ""),
                        }
                    )

                    backup_resource = BackupResource(
                        {
                            "name": f"{location_id}/backup/{backup_name.split('/')[-1]}",
                            "account": project_id,
                            "region_code": location_id,
                            "data": backup_data,
                            "reference": ReferenceModel(backup_data.reference()),
                        }
                    )

                    backup_responses.append(
                        BackupResponse({"resource": backup_resource})
                    )

                except Exception as backup_error:
                    _LOGGER.warning(
                        f"Failed to process backup {backup.get('name', 'unknown')}: {backup_error}"
                    )
                    continue

        except Exception as e:
            _LOGGER.warning(
                f"Failed to create backup resources for project {project_id}: {e}"
            )

        return backup_responses

    def _determine_recurrence_type(self, backup_schedule: dict) -> str:
        """BackupSchedule의 recurrence 타입을 결정합니다.

        Args:
            backup_schedule: 백업 스케줄 딕셔너리

        Returns:
            str: "DAILY" 또는 "WEEKLY"
        """
        # dailyRecurrence 또는 weeklyRecurrence 필드 확인
        if backup_schedule.get("dailyRecurrence"):
            return "DAILY"
        elif backup_schedule.get("weeklyRecurrence"):
            return "WEEKLY"
        else:
            # 기본값 (알 수 없는 경우)
            return "DAILY"

    @staticmethod
    def _extract_location_from_backup_name(backup_name: str) -> str:
        """백업 이름에서 위치 ID 추출

        Args:
            backup_name: projects/{project}/locations/{location}/backups/{backup} 형식

        Returns:
            str: 위치 ID (예: us-central1)
        """
        if "/locations/" in backup_name and "/backups/" in backup_name:
            # projects/{project}/locations/{location}/backups/{backup} 형식에서 location 추출
            parts = backup_name.split("/locations/")[1].split("/backups/")[0]
            return parts
        return "global"

    @staticmethod
    def _extract_database_id(database_name: str) -> str:
        """데이터베이스 이름에서 ID 추출"""
        if "/databases/" in database_name:
            return database_name.split("/databases/")[-1]
        return database_name

    @staticmethod
    def _extract_location_id(location_id: str) -> str:
        """위치 ID를 리전 코드로 변환"""
        if not location_id:
            return "global"
        return location_id

    @staticmethod
    def _extract_document_path(document_name: str) -> str:
        """문서 이름에서 경로 추출"""
        if "/documents/" in document_name:
            return document_name.split("/documents/")[-1]
        return document_name

    @staticmethod
    def _extract_document_id(document_name: str) -> str:
        """문서 이름에서 ID만 추출"""
        document_path = FirestoreManager._extract_document_path(document_name)
        return document_path.split("/")[-1] if "/" in document_path else document_path
