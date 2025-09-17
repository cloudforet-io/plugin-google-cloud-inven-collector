import logging
import time
from typing import List, Tuple

from spaceone.inventory.connector.firestore.database_v1 import (
    FirestoreDatabaseConnector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.firestore.backup_schedule.cloud_service import (
    BackupScheduleResource,
    BackupScheduleResponse,
)
from spaceone.inventory.model.firestore.backup_schedule.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.firestore.backup_schedule.data import BackupSchedule

_LOGGER = logging.getLogger(__name__)


class FirestoreBackupScheduleManager(GoogleCloudManager):
    connector_name = "FirestoreDatabaseConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    firestore_conn = None

    def collect_cloud_service(
        self, params
    ) -> Tuple[List[BackupScheduleResponse], List]:
        _LOGGER.debug("** Firestore BackupSchedule START **")
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

            # Get database list
            databases = self.firestore_conn.list_databases()
            _LOGGER.info(f"Found {len(databases)} Firestore databases")

            # Sequential processing: collect backup schedules for each database
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
                    backup_schedule_resources = (
                        self._create_backup_schedule_resources_for_database(
                            database_name,
                            database_id,
                            project_id,
                            region_code,
                        )
                    )

                    ##################################
                    # 3. Make Return Resource & 5. Make Resource Response Object
                    ##################################
                    collected_cloud_services.extend(backup_schedule_resources)

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
                        e, "Firestore", "BackupSchedule", database_id
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(f"Failed to collect Firestore backup schedules: {e}")
            error_response = self.generate_resource_error_response(
                e, "Firestore", "BackupSchedule"
            )
            error_responses.append(error_response)

        _LOGGER.debug(
            f"** Firestore BackupSchedule Finished {time.time() - start_time} Seconds **"
        )

        return collected_cloud_services, error_responses

    def _create_backup_schedule_resources_for_database(
        self,
        database_name: str,
        database_id: str,
        project_id: str,
        region_code: str,
    ) -> List[BackupScheduleResponse]:
        """Create all backup schedule resources for the database"""
        backup_schedule_responses = []

        try:
            backup_schedules = self.firestore_conn.list_backup_schedules(database_name)
            _LOGGER.info(
                f"Found {len(backup_schedules)} backup schedules for database {database_id}"
            )

            for backup_schedule in backup_schedules:
                try:
                    backup_schedule_name = backup_schedule.get("name", "")
                    backup_schedule_id = (
                        backup_schedule_name.split("/")[-1]
                        if backup_schedule_name
                        else ""
                    )

                    recurrence_info = self._determine_recurrence_info(backup_schedule)

                    backup_schedule.update(
                        {
                            "name": backup_schedule_id,
                            "full_name": backup_schedule_name,
                            "database_id": database_id,
                            "project": project_id,
                            "recurrence_type": recurrence_info["type"],
                            "weekly_day": recurrence_info.get("weekly_day", ""),
                        }
                    )

                    backup_schedule_data = BackupSchedule(backup_schedule, strict=False)

                    backup_schedule_resource = BackupScheduleResource(
                        {
                            "name": backup_schedule_id,
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

    def _determine_recurrence_info(self, backup_schedule: dict) -> dict:
        # Check dailyRecurrence or weeklyRecurrence field
        if backup_schedule.get("dailyRecurrence"):
            return {"type": "DAILY"}
        elif weekly_recurrence := backup_schedule.get("weeklyRecurrence"):
            recurrence_info = {"type": "WEEKLY"}
            if day := weekly_recurrence.get("day"):
                recurrence_info["weekly_day"] = day
            return recurrence_info
        else:
            return {"type": "DAILY"}
