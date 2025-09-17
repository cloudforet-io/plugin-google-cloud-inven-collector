import logging
import time
from typing import Any, Dict, List, Tuple

from spaceone.inventory.connector.filestore.instance_v1beta1 import (
    FilestoreInstanceV1Beta1Connector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.filestore.instance.cloud_service import (
    FilestoreInstanceResource,
    FilestoreInstanceResponse,
)
from spaceone.inventory.model.filestore.instance.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.filestore.instance.data import FilestoreInstanceData

_LOGGER = logging.getLogger(__name__)


class FilestoreInstanceV1Beta1Manager(GoogleCloudManager):
    """
    Google Cloud Filestore Instance Manager (v1beta1 API)
    """

    connector_name = "FilestoreInstanceV1Beta1Connector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    instance_v1beta1_conn = None

    def collect_cloud_service(self, params):
        _LOGGER.debug("** Filestore Instance (v1beta1) START **")
        start_time = time.time()

        collected_cloud_services = []
        error_responses = []
        instance_id = ""

        secret_data = params["secret_data"]
        project_id = secret_data["project_id"]

        try:
            ##################################
            # 0. Gather All Related Resources
            ##################################
            self.instance_v1beta1_conn: FilestoreInstanceV1Beta1Connector = (
                self.locator.get_connector(self.connector_name, **params)
            )

            # Filestore instance list (v1beta1 API)
            filestore_instances = self.instance_v1beta1_conn.list_instances()

            for filestore_instance in filestore_instances:
                try:
                    ##################################
                    # 1. Set Basic Information
                    ##################################
                    instance_name = filestore_instance.get("name", "")
                    instance_id = (
                        instance_name.split("/")[-1]
                        if "/" in instance_name
                        else instance_name
                    )
                    location = filestore_instance.get("location", "")
                    tier = filestore_instance.get("tier", "")
                    multishare_enabled = filestore_instance.get(
                        "multishareEnabled", False
                    )

                    ##################################
                    # 2. Make Base Data
                    ##################################
                    # Process file share information and calculate capacity
                    unified_file_shares, total_capacity_gb = (
                        self._process_file_shares_with_details(
                            filestore_instance.get("fileShares", []),
                            instance_name,
                            instance_id,
                            tier,
                            multishare_enabled,
                        )
                    )

                    labels = self.convert_labels_format(
                        filestore_instance.get("labels", {})
                    )

                    # Collect network and snapshot information
                    networks = self._process_networks(
                        filestore_instance.get("networks", [])
                    )
                    snapshots = self._collect_snapshots(instance_name, instance_id)

                    filestore_instance.update(
                        {
                            "project": project_id,
                            "name": instance_id,
                            "full_name": instance_name,
                            "instance_id": instance_id,
                            "location": location,
                            "tier": tier,
                            "networks": networks,
                            "unified_file_shares": unified_file_shares,
                            "snapshots": snapshots,
                            "labels": labels,
                            "create_time": filestore_instance.get("createTime", ""),
                            "stats": {
                                "total_capacity_gb": str(total_capacity_gb),
                                "file_share_count": str(len(unified_file_shares)),
                                "snapshot_count": str(len(snapshots)),
                                "network_count": str(len(networks)),
                            },
                            "protocol": filestore_instance.get("protocol") or None,
                            "custom_performance_supported": str(
                                filestore_instance.get(
                                    "customPerformanceSupported", False
                                )
                            ).lower()
                            if filestore_instance.get("customPerformanceSupported")
                            is not None
                            else None,
                            "performance_limits": self._process_performance_limits(
                                filestore_instance.get("performanceLimits", {})
                            ),
                            "google_cloud_monitoring": self.set_google_cloud_monitoring(
                                project_id,
                                "file.googleapis.com/instance",
                                instance_id,
                                [
                                    {
                                        "key": "resource.labels.instance_id",
                                        "value": instance_id,
                                    }
                                ],
                            ),
                            "google_cloud_logging": self.set_google_cloud_logging(
                                "Filestore", "Instance", project_id, instance_id
                            ),
                        }
                    )

                    instance_data = FilestoreInstanceData(
                        filestore_instance, strict=False
                    )

                    ##################################
                    # 3. Make Return Resource
                    ##################################
                    instance_resource = FilestoreInstanceResource(
                        {
                            "name": instance_id,
                            "account": project_id,
                            "instance_type": tier,
                            "instance_size": total_capacity_gb,
                            "tags": labels,
                            "region_code": location,
                            "data": instance_data,
                            "reference": ReferenceModel(instance_data.reference()),
                        }
                    )

                    ##################################
                    # 4. Make Collected Region Code
                    ##################################
                    self.set_region_code(location)

                    ##################################
                    # 5. Make Resource Response Object
                    ##################################
                    collected_cloud_services.append(
                        FilestoreInstanceResponse({"resource": instance_resource})
                    )

                except Exception as e:
                    _LOGGER.error(
                        f"Failed to process instance {instance_id}: {e}",
                        exc_info=True,
                    )
                    error_response = self.generate_resource_error_response(
                        e, "Filestore", "Instance", instance_id
                    )
                    error_responses.append(error_response)

        except Exception as e:
            _LOGGER.error(
                f"Failed to collect Filestore instances (v1beta1): {e}", exc_info=True
            )
            error_response = self.generate_resource_error_response(
                e, "Filestore", "Instance", "collection"
            )
            error_responses.append(error_response)

        _LOGGER.debug(
            f"** Filestore Instance (v1beta1) Finished {time.time() - start_time} Seconds **"
        )
        return collected_cloud_services, error_responses

    def _process_networks(self, networks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process network information"""
        return [
            {
                "network": network.get("network", ""),
                "modes": network.get("modes", []),
                "reserved_ip_range": network.get("reservedIpRange", ""),
                "connect_mode": network.get("connectMode", ""),
            }
            for network in networks
        ]

    def _process_file_shares_with_details(
        self,
        file_shares: List[Dict[str, Any]],
        instance_name: str,
        instance_id: str,
        tier: str,
        multishare_enabled: bool,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Process file share information with detailed information"""
        total_capacity_gb = sum(int(fs.get("capacityGb", 0)) for fs in file_shares)

        # Determine whether to collect detailed information
        should_collect_details = (
            tier in ["ENTERPRISE", "ENTERPRISE_TIER_1", "ENTERPRISE_TIER_2"]
            and multishare_enabled
        )

        if should_collect_details:
            detailed_shares = self._collect_detailed_shares(instance_name, instance_id)
            if detailed_shares:
                return self._create_detailed_unified_shares(
                    detailed_shares
                ), total_capacity_gb

        return self._create_basic_unified_shares(file_shares), total_capacity_gb

    def _create_basic_unified_shares(
        self, file_shares: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create unified share list with basic file share information"""
        return [
            {
                "name": fs.get("name", ""),
                "capacity_gb": str(int(fs.get("capacityGb", 0))),
                "source_backup": fs.get("sourceBackup", ""),
                "nfs_export_options": fs.get("nfsExportOptions", []),
                "data_source": "Basic",
            }
            for fs in file_shares
        ]

    def _process_performance_limits(
        self, performance_limits: Dict[str, Any]
    ) -> Dict[str, str]:
        """Process performance limit information"""
        if not performance_limits:
            return None

        return {
            "max_read_iops": performance_limits.get("maxReadIops") or None,
            "max_write_iops": performance_limits.get("maxWriteIops") or None,
            "max_read_throughput_bps": performance_limits.get("maxReadThroughputBps")
            or None,
            "max_write_throughput_bps": performance_limits.get("maxWriteThroughputBps")
            or None,
            "max_iops": performance_limits.get("maxIops") or None,
        }

    def _create_detailed_unified_shares(
        self, detailed_shares: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create unified share list with detailed file share information"""
        return [
            {
                "name": share.get("name", ""),
                "mount_name": share.get("mount_name", ""),
                "description": share.get("description", ""),
                "capacity_gb": share.get("capacity_gb", ""),
                "state": share.get("state", ""),
                "nfs_export_options": share.get("nfs_export_options", []),
                "data_source": "Detailed",
            }
            for share in detailed_shares
        ]

    def _collect_detailed_shares(
        self, instance_name: str, instance_id: str
    ) -> List[Dict[str, Any]]:
        try:
            detailed_shares = self.instance_v1beta1_conn.list_shares_for_instance(
                instance_name
            )
            processed_shares = []

            for share in detailed_shares:
                share.update(
                    {
                        "capacity_gb": str(int(share.get("capacityGb", 0))),
                        "mount_name": share.get("mountName", ""),
                    }
                )
                processed_shares.append(share)

            return processed_shares
        except Exception as e:
            error_message = str(e)
            instance_id_from_name = (
                instance_name.split("/")[-1] if "/" in instance_name else instance_name
            )

            if "ListShares operation is not supported" in error_message:
                _LOGGER.info(
                    f"ListShares operation is not supported for instance {instance_id_from_name}. "
                    "This may be due to instance tier limitations (Basic/Standard) or regional restrictions."
                )
            else:
                _LOGGER.warning(
                    f"Failed to collect detailed shares for {instance_id_from_name}: {e}"
                )

            return []

    def _collect_snapshots(
        self, instance_name: str, instance_id: str
    ) -> List[Dict[str, Any]]:
        snapshots = []
        try:
            instance_snapshots = self.instance_v1beta1_conn.list_snapshots_for_instance(
                instance_name
            )

            for snapshot in instance_snapshots:
                # (name, description, state, createTime, labels)
                name = snapshot.get("name", "")
                snapshot_id = name.split("/")[-1] if "/" in name else name
                snapshot.update(
                    {
                        "name": snapshot_id,
                        "full_name": name,
                        "create_time": snapshot.get("createTime", ""),
                        "labels": self.convert_labels_format(
                            snapshot.get("labels", {})
                        ),
                    }
                )
                snapshots.append(snapshot)

        except Exception as e:
            _LOGGER.warning(
                f"Failed to collect snapshots for instance {instance_id}: {e}"
            )

        return snapshots
