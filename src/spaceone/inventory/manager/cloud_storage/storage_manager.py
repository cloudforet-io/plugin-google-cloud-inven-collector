import logging
import time
from datetime import datetime, timedelta

from spaceone.inventory.connector.cloud_storage.monitoring import MonitoringConnector
from spaceone.inventory.connector.cloud_storage.storage import StorageConnector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.cloud_storage.bucket.cloud_service import (
    StorageResource,
    StorageResponse,
)
from spaceone.inventory.model.cloud_storage.bucket.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_storage.bucket.data import Storage

_LOGGER = logging.getLogger(__name__)


class StorageManager(GoogleCloudManager):
    connector_name = "StorageConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    @staticmethod
    def _safe_get(data, key, default=None):

        if isinstance(data, dict) and key in data:
            return data[key]
        return default
    
    @staticmethod
    def _safe_get_nested(data, keys, default=None):

        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current



    def collect_cloud_service(self, params):
        _LOGGER.debug("** Storage START **")
        start_time = time.time()
        """
        Args:
            params:
                - options
                - schema
                - secret_data
                - filter
                - zones
        Response:
            CloudServiceResponse/ErrorResourceResponse
        """
        collected_cloud_services = []
        error_responses = []
        bucket_id = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        storage_conn: StorageConnector = self.locator.get_connector(
            self.connector_name, **params
        )
        monitoring_conn: MonitoringConnector = self.locator.get_connector(
            "MonitoringConnector", **params
        )
        # Get lists that relate with snapshots through Google Cloud API
        buckets = storage_conn.list_buckets()

        # buckets가 None인 경우 처리
        if buckets is None:
            _LOGGER.warning("No buckets returned from storage connector")
            return collected_cloud_services, error_responses

        for bucket in buckets:
            try:
                # bucket 객체가 None인지 먼저 체크
                if bucket is None:
                    _LOGGER.warning("Skipping None bucket object")
                    continue

                ##################################
                # 1. Set Basic Information
                ##################################
                bucket_name = self._safe_get(bucket, "name")
                bucket_id = self._safe_get(bucket, "id")

                # bucket_name이 None인 경우 처리
                if bucket_name is None:
                    _LOGGER.warning("Skipping bucket with None name")
                    continue

                _name = self._safe_get(bucket, "name", "")
                is_payer_bucket = self._safe_get_nested(
                    bucket, ["billing", "requesterPays"], False
                )
                if is_payer_bucket:
                    print(f"Bucket Name: {bucket_name} is Payer Bucket")

                # IAM policy 조회 시 예외 처리
                try:
                    iam_policy = storage_conn.list_iam_policy(
                        bucket_name, is_payer_bucket
                    )
                    if iam_policy is None:
                        iam_policy = {}
                except Exception as iam_error:
                    _LOGGER.warning(
                        f"Failed to get IAM policy for bucket {bucket_name}: {iam_error}"
                    )
                    iam_policy = {"error_flag": "na"}  # Not Authorized

                # 모니터링 데이터 조회 시 예외 처리
                try:
                    object_count = self._get_object_total_count(
                        monitoring_conn, bucket_name
                    )
                except Exception as count_error:
                    _LOGGER.warning(
                        f"Failed to get object count for bucket {bucket_name}: {count_error}"
                    )
                    object_count = 0

                try:
                    object_size = self._get_bucket_total_size(
                        monitoring_conn, bucket_name
                    )
                except Exception as size_error:
                    _LOGGER.warning(
                        f"Failed to get bucket size for bucket {bucket_name}: {size_error}"
                    )
                    object_size = 0

                # storageClass가 None일 수 있으므로 안전하게 처리
                storage_class = self._safe_get(bucket, "storageClass")
                st_class = storage_class.lower() if storage_class else "standard"

                region = self.get_matching_region(bucket)
                labels = self.convert_labels_format(
                    self._safe_get(bucket, "labels", {})
                )

                ##################################
                # 2. Make Base Data
                ##################################

                bucket.update(
                    {
                        "project": secret_data["project_id"],
                        "encryption": self._get_encryption(bucket),
                        "requester_pays": self._get_requester_pays(bucket),
                        "retention_policy_display": self._get_retention_policy_display(
                            bucket
                        ),
                        "links": self._get_config_link(bucket),
                        "size": object_size,
                        "default_event_based_hold": (
                            "Enabled"
                            if self._safe_get(bucket, "defaultEventBasedHold")
                            else "Disabled"
                        ),
                        "iam_policy": iam_policy,
                        "iam_policy_binding": self._get_iam_policy_binding(iam_policy),
                        "object_count": object_count,
                        "object_total_size": object_size,
                        "lifecycle_rule": self._get_lifecycle_rule(bucket),
                        "location": self.get_location(bucket),
                        "default_storage_class": st_class.capitalize(),
                        "access_control": self._get_access_control(bucket),
                        "public_access": self._get_public_access(bucket, iam_policy),
                        "labels": labels,
                    }
                )

                bucket.update(
                    {
                        "google_cloud_logging": self.set_google_cloud_logging(
                            "CloudStorage", "Bucket", project_id, bucket_name
                        ),
                    }
                )

                bucket_data = Storage(bucket, strict=False)

                if region is None or region.get("region_code") is None:
                    region_code = "Global"
                else:
                    region_code = region.get("region_code")

                ##################################
                # 3. Make Return Resource
                ##################################
                bucket_resource = StorageResource(
                    {
                        "name": _name,
                        "account": project_id,
                        "tags": labels,
                        "region_code": region_code,
                        "instance_type": "",
                        "instance_size": bucket_data.size,
                        "data": bucket_data,
                        "reference": ReferenceModel(bucket_data.reference()),
                    }
                )

                ##################################
                # 4. Make Collected Region Code
                ##################################
                self.set_region_code(region_code)

                ##################################
                # 5. Make Resource Response Object
                # List of LoadBalancingResponse Object
                ##################################
                collected_cloud_services.append(
                    StorageResponse({"resource": bucket_resource})
                )
            except Exception as e:
                _LOGGER.error(f"[collect_cloud_service] => {e}", exc_info=True)
                error_response = self.generate_resource_error_response(
                    e, "Storage", "Bucket", bucket_id
                )
                error_responses.append(error_response)

        _LOGGER.debug(f"** Storage Finished {time.time() - start_time} Seconds **")
        return collected_cloud_services, error_responses

    def get_matching_region(self, bucket):
        location_type_ref = ["multi-region", "dual-region"]
        location = self._safe_get(bucket, "location", "").lower()
        location_type = self._safe_get(bucket, "locationType", "")
        region_code = "global" if location_type in location_type_ref else location
        return self.match_region_info(region_code)

    def get_location(self, bucket):
        location_type_ref = ["multi-region", "dual-region"]
        location = self._safe_get(bucket, "location", "").lower()
        location_type = self._safe_get(bucket, "locationType", "")

        if location_type in location_type_ref:
            # Multi
            # US (Multiple Regions in United States)
            # Europe (Multiple Regions in European Union)
            # Asia Pacific (Multiple Regions in Asia)
            if location_type == "multi-region":
                location_display = (
                    f"{location} (Multiple Regions in {location.capitalize()})"
                )
            else:
                # Dual - choices
                # Americas nam4 (lowa and South Carolina)
                # Europe eur4 (Netherlands and Finland)
                # Asia Pacific asia1 (Tokyo and Osaka)

                dual_map = {
                    "nam4": "(lowa and South Carolina)",
                    "eur4": "(Netherlands and Finland)",
                    "asia1": "(Tokyo and Osaka)",
                }
                map_str = dual_map.get(location, "")
                location_display = f"{location} {map_str}"

        else:
            region = self.match_region_info(location)
            region_name = region.get("name", "") if region else "Global"
            location_display = f"{location} | {region_name}"

        return {
            "location": location,
            "location_type": location_type.capitalize(),
            "location_display": location_display,
        }

    @staticmethod
    def _get_encryption(bucket):
        encryption = (
            bucket.get("encryption")
            if isinstance(bucket, dict) and "encryption" in bucket
            else None
        )
        return "Google-managed" if encryption == {} else "Customer-managed"

    @staticmethod
    def _get_public_access(bucket, iam_policy):
        public_access = None
        public_access_map = {
            "np": "Not public",
            "na": "Not Authorized",
            "pi": "Public to internet",
            "soa": "Subject to object ACLs",
        }

        binding_members = []
        iam_config = (
            bucket.get("iamConfiguration")
            if isinstance(bucket, dict) and "iamConfiguration" in bucket
            else None
        )
        if iam_config is None:
            bucket_policy_only = {}
            uniform_bucket_level = {}
        else:
            bucket_policy_only = iam_config.get("bucketPolicyOnly", {})
            uniform_bucket_level = iam_config.get("uniformBucketLevelAccess", {})

        # iam_policy가 None이 아니고 bindings가 있는 경우만 처리
        if iam_policy and "bindings" in iam_policy:
            bindings = (
                iam_policy.get("bindings", []) if isinstance(iam_policy, dict) else []
            )
            if isinstance(bindings, list):
                for binding in bindings:
                    if binding is None or not isinstance(binding, dict):
                        continue

                    if "members" in binding:
                        members = binding.get("members", [])
                        if members is None or not isinstance(members, list):
                            continue

                        binding_members.extend(members)

        if bucket_policy_only is None:
            bucket_policy_only = {}
        if uniform_bucket_level is None:
            uniform_bucket_level = {}

        if not bucket_policy_only.get("enabled") and not uniform_bucket_level.get(
            "enabled"
        ):
            public_access = public_access_map.get("soa")
        elif isinstance(iam_policy, dict) and "error_flag" in iam_policy:
            public_access = public_access_map.get(iam_policy.get("error_flag"))
        elif (
            "allUsers" in binding_members or "allAuthenticatedUsers" in binding_members
        ):
            public_access = public_access_map.get("pi")
        else:
            public_access = public_access_map.get("np")
        return public_access

    @staticmethod
    def _get_requester_pays(bucket):
        pays = "OFF"
        billing = (
            bucket.get("billing")
            if isinstance(bucket, dict) and "billing" in bucket
            else {}
        )
        if (
            billing is not None
            and isinstance(billing, dict)
            and billing.get("requesterPays", False)
        ):
            pays = "ON"
        return pays

    @staticmethod
    def _get_access_control(bucket):
        access_control = "Fine-grained"
        iam_config = (
            bucket.get("iamConfiguration")
            if isinstance(bucket, dict) and "iamConfiguration" in bucket
            else {}
        )
        if iam_config is None:
            uniform = {}
        else:
            uniform = iam_config.get("uniformBucketLevelAccess", {})

        if uniform is not None and uniform.get("enabled"):
            access_control = "Uniform"
        return access_control

    @staticmethod
    def _get_config_link(bucket):
        name = (
            bucket.get("name") if isinstance(bucket, dict) and "name" in bucket else ""
        )
        return {
            "link_url": f"https://console.cloud.google.com/storage/browser/{name}",
            "gsutil_link": f"gs://{name}",
        }

    @staticmethod
    def _get_lifecycle_rule(bucket):
        display = ""
        life_cycle = (
            bucket.get("lifecycle")
            if isinstance(bucket, dict) and "lifecycle" in bucket
            else {}
        )
        if life_cycle is None:
            life_cycle = {}
        rules = life_cycle.get("rule", [])
        num_of_rule = len(rules)

        if num_of_rule == 0:
            display = "None"
        elif num_of_rule == 1:
            display = f"{num_of_rule} rule"
        else:
            display = f"{num_of_rule} rules"

        life_cycle_rule = []
        rules = life_cycle.get("rule", []) if life_cycle else []

        for rule in rules:
            if rule is None:
                continue

            action_header = (
                "Set to" if rule.get("type") == "SetStorageClass" else "Delete"
            )
            action_footer = (
                rule.get("storage_class", "").capitalize()
                if rule.get("type") == "SetStorageClass"
                else "object"
            )

            condition_display = ""
            formatter = "%Y-%m-%d"
            condition_vo = rule.get("condition", {})
            if condition_vo is None:
                condition_vo = {}

            if "customTimeBefore" in condition_vo:
                f = "Object's custom time is on or before"
                target = datetime.strptime(
                    condition_vo.get("customTimeBefore"), formatter
                ) + timedelta(days=1)
                tar_date = target.strftime("%B %d, %Y")
                condition_display = f"{f} {tar_date}"

            elif "daysSinceCustomTime" in condition_vo:
                f = "days since object's custom time"
                target = condition_vo.get("daysSinceCustomTime")
                condition_display = f"{target}+ {f}"

            elif "matchesStorageClass" in condition_vo:
                f = "Storage Class matches"
                condition_target = [
                    s.title().replace("_", " ")
                    for s in condition_vo.get("matchesStorageClass", [])
                ]
                target = ", ".join(condition_target)
                condition_display = f"{f} {target}"

            elif "age" in condition_vo:
                f = "days since object was updated"
                target = condition_vo.get("age")
                condition_display = f"{target}+ {f}"

            elif "numNewerVersions" in condition_vo:
                f = "newer versions"
                target = condition_vo.get("numNewerVersions")
                condition_display = f"{target}+ {f}"

            elif "daysSinceNoncurrentTime" in condition_vo:
                f = "days since object became noncurrent"
                target = condition_vo.get("daysSinceNoncurrentTime")
                condition_display = f"{target}+ {f}"

            elif "createdBefore" in condition_vo:
                f = "Created on or before"
                target = datetime.strptime(
                    condition_vo.get("createdBefore"), formatter
                ) + timedelta(days=1)
                tar_date = target.strftime("%B %d, %Y")
                condition_display = f"{f} {tar_date}"

            elif "isLive" in condition_vo:
                f = "Object is"
                target = condition_vo.get("isLive")
                targets_str = "live" if condition_vo.get("isLive") else "noncurrent"
                condition_display = f"{f} {targets_str}"

            elif "noncurrentTimeBefore" in condition_vo:
                f = "Object became noncurrent on or before"
                target = datetime.strptime(
                    condition_vo.get("noncurrentTimeBefore"), formatter
                ) + timedelta(days=1)
                tar_date = target.strftime("%B %d, %Y")
                condition_display = f"{f} {tar_date}"

            rule.update(
                {
                    "action_display": f"{action_header} {action_footer}",
                    "condition_display": condition_display,
                }
            )
            life_cycle_rule.append(rule)

        return {"lifecycle_rule_display": display, "rule": life_cycle_rule}

    @staticmethod
    def _get_iam_policy_binding(iam_policy):
        iam_policy_binding = []

        # iam_policy가 None이거나 비어있는 경우 처리
        if not iam_policy or "bindings" not in iam_policy:
            return iam_policy_binding

        bindings = (
            iam_policy.get("bindings", []) if isinstance(iam_policy, dict) else []
        )
        if not isinstance(bindings, list):
            return iam_policy_binding

        for binding in bindings:
            # binding이 None이거나 딕셔너리가 아닌 경우 건너뛰기
            if binding is None or not isinstance(binding, dict):
                continue

            members = binding.get("members", [])
            role = binding.get("role", "")

            # members가 None이거나 리스트가 아닌 경우 처리
            if members is None or not isinstance(members, list):
                continue

            for member in members:
                if member:  # member가 None이 아닌 경우만 추가
                    iam_policy_binding.append(
                        {
                            "member": member,
                            "role": role,
                        }
                    )

        return iam_policy_binding

    @staticmethod
    def _get_retention_policy_display(bucket):
        display = ""
        policy = (
            bucket.get("retentionPolicy")
            if isinstance(bucket, dict) and "retentionPolicy" in bucket
            else None
        )
        if policy is None:
            return display
        if policy:
            retention_period = int(policy.get("retentionPeriod", 0))
            rp_in_days = retention_period / 86400
            day_month = "days" if rp_in_days < 91 else "months"
            period = rp_in_days if rp_in_days < 91 else rp_in_days / 31
            display = f"{str(int(period))} {day_month}"
        return display

    @staticmethod
    def _get_object_total_count(monitoring_conn, bucket_name):
        metric = "storage.googleapis.com/storage/object_count"
        start = datetime.now() - timedelta(days=1)
        end = datetime.now()
        if monitoring_conn is None:
            return 0

        response = monitoring_conn.get_metric_data(bucket_name, metric, start, end)

        if response is None:
            return 0

        points = response.get("points", [])
        if points is None:
            return 0

        if (
            points
            and len(points) > 0
            and points[0] is not None
            and isinstance(points[0], dict)
        ):
            value = points[0].get("value", {})
            object_total_count = (
                value.get("int64Value", 0) if isinstance(value, dict) else 0
            )
        else:
            object_total_count = 0

        return object_total_count

    @staticmethod
    def _get_bucket_total_size(monitoring_conn, bucket_name):
        metric = "storage.googleapis.com/storage/total_bytes"
        start = datetime.now() - timedelta(days=1)
        end = datetime.now()

        if monitoring_conn is None:
            return 0

        response = monitoring_conn.get_metric_data(bucket_name, metric, start, end)

        if response is None:
            return 0

        points = response.get("points", [])
        if points is None:
            return 0

        if (
            points
            and len(points) > 0
            and points[0] is not None
            and isinstance(points[0], dict)
        ):
            value = points[0].get("value", {})
            object_total_size = (
                value.get("doubleValue", 0) if isinstance(value, dict) else 0
            )
        else:
            object_total_size = 0

        return object_total_size
