import time
import logging

from datetime import datetime, timedelta
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.connector.cloud_storage.storage import StorageConnector
from spaceone.inventory.connector.cloud_storage.monitoring import MonitoringConnector
from spaceone.inventory.model.cloud_storage.bucket.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.cloud_storage.bucket.cloud_service import (
    StorageResource,
    StorageResponse,
)
from spaceone.inventory.model.cloud_storage.bucket.data import Storage

_LOGGER = logging.getLogger(__name__)


class StorageManager(GoogleCloudManager):
    connector_name = "StorageConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        _LOGGER.debug(f"** Storage START **")
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

        for bucket in buckets:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                bucket_name = bucket.get("name")
                bucket_id = bucket.get("id")

                _name = bucket.get("name", "")
                object_count = self._get_object_total_count(
                    monitoring_conn, bucket_name
                )
                object_size = self._get_bucket_total_size(monitoring_conn, bucket_name)
                iam_policy = storage_conn.list_iam_policy(bucket_name)
                st_class = bucket.get("storageClass").lower()
                region = self.get_matching_region(bucket)
                labels = self.convert_labels_format(bucket.get("labels", {}))

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
                            if bucket.get("defaultEventBasedHold")
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

                ##################################
                # 3. Make Return Resource
                ##################################
                bucket_resource = StorageResource(
                    {
                        "name": _name,
                        "account": project_id,
                        "tags": labels,
                        "region_code": region.get("region_code"),
                        "instance_type": "",
                        "instance_size": bucket_data.size,
                        "data": bucket_data,
                        "reference": ReferenceModel(bucket_data.reference()),
                    }
                )

                ##################################
                # 4. Make Collected Region Code
                ##################################
                self.set_region_code(region.get("region_code"))

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
        location = bucket.get("location", "").lower()
        location_type = bucket.get("locationType", "")
        region_code = "global" if location_type in location_type_ref else location
        return self.match_region_info(region_code)

    def get_location(self, bucket):
        location_type_ref = ["multi-region", "dual-region"]
        location = bucket.get("location", "").lower()
        location_type = bucket.get("locationType", "")

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
            _LOGGER.debug(f"[DEBUG] location : {location}")
            region = self.match_region_info(location)
            region_name = region.get("name", "")
            location_display = f"{location} | {region_name}"

        return {
            "location": location,
            "location_type": location_type.capitalize(),
            "location_display": location_display,
        }

    @staticmethod
    def _get_encryption(bucket):
        encryption = bucket.get("encryption", {})
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
        iam_config = bucket.get("iamConfiguration", {})
        bucket_policy_only = iam_config.get("bucketPolicyOnly", {})
        uniform_bucket_level = iam_config.get("uniformBucketLevelAccess", {})
        [
            binding_members.extend(s.get("members"))
            for s in iam_policy.get("bindings", [])
        ]

        if not bucket_policy_only.get("enabled") and not uniform_bucket_level.get(
            "enabled"
        ):
            public_access = public_access_map.get("soa")
        elif "error_flag" in iam_policy:
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
        billing = bucket.get("billing", {})
        if billing.get("requesterPays", False):
            pays = "ON"
        return pays

    @staticmethod
    def _get_access_control(bucket):
        access_control = "Fine-grained"
        iam_config = bucket.get("iamConfiguration", {})
        uniform = iam_config.get("uniformBucketLevelAccess", {})
        if uniform.get("enabled"):
            access_control = "Uniform"
        return access_control

    @staticmethod
    def _get_config_link(bucket):
        name = bucket.get("name")
        return {
            "link_url": f"https://console.cloud.google.com/storage/browser/{name}",
            "gsutil_link": f"gs://{name}",
        }

    @staticmethod
    def _get_lifecycle_rule(bucket):
        display = ""
        life_cycle = bucket.get("lifecycle", {})
        rules = life_cycle.get("rule", [])
        num_of_rule = len(rules)

        if num_of_rule == 0:
            display = "None"
        elif num_of_rule == 1:
            display = f"{num_of_rule} rule"
        else:
            display = f"{num_of_rule} rules"

        life_cycle_rule = []
        for rule in life_cycle.get("rule", []):
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
        if "bindings" in iam_policy:
            bindings = iam_policy.get("bindings")
            for binding in bindings:
                members = binding.get("members")
                role = binding.get("role", "")
                for member in members:
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
        policy = bucket.get("retentionPolicy")
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
        response = monitoring_conn.get_metric_data(bucket_name, metric, start, end)

        if response.get("points", []):
            object_total_count = (
                response.get("points", [])[0].get("value", {}).get("int64Value", "")
            )
        else:
            object_total_count = None

        return object_total_count

    @staticmethod
    def _get_bucket_total_size(monitoring_conn, bucket_name):
        metric = "storage.googleapis.com/storage/total_bytes"
        start = datetime.now() - timedelta(days=1)
        end = datetime.now()
        response = monitoring_conn.get_metric_data(bucket_name, metric, start, end)

        if response.get("points", []):
            object_total_size = (
                response.get("points", [])[0].get("value", {}).get("doubleValue", "")
            )
        else:
            object_total_size = None

        return object_total_size
