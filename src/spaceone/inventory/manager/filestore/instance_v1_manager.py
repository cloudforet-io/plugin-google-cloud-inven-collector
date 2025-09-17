import logging
import time
from typing import Any, Dict, List, Tuple

from spaceone.inventory.connector.filestore.instance_v1 import (
    FilestoreInstanceConnector,
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


class FilestoreInstanceManager(GoogleCloudManager):
    connector_name = "FilestoreInstanceConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    instance_conn = None

    def collect_cloud_service(
        self, params
    ) -> Tuple[List[FilestoreInstanceResponse], List]:
        _LOGGER.debug("** Filestore Instance START **")
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
            self.instance_conn: FilestoreInstanceConnector = self.locator.get_connector(
                self.connector_name, **params
            )

            # Get Filestore instances (v1 API)
            filestore_instances = self.instance_conn.list_instances()

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

                    ##################################
                    # 2. Make Base Data
                    ##################################
                    # Process file share information and calculate capacity
                    unified_file_shares, total_capacity_gb = (
                        self._process_file_shares_directly(
                            filestore_instance.get("fileShares", [])
                        )
                    )

                    labels = self.convert_labels_format(
                        filestore_instance.get("labels", {})
                    )

                    networks = self._process_networks(
                        filestore_instance.get("networks", [])
                    )

                    filestore_instance.update(
                        {
                            "project": project_id,
                            "name": instance_id,
                            "full_name": instance_name,
                            "instance_id": instance_id,
                            "location": location,
                            "networks": networks,
                            "unified_file_shares": unified_file_shares,
                            "labels": labels,
                            "stats": {
                                "total_capacity_gb": str(total_capacity_gb),
                                "file_share_count": str(len(unified_file_shares)),
                                "network_count": str(len(networks)),
                            },
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
                                "file.googleapis.com/nfs",
                                instance_id,
                                [
                                    {
                                        "key": "resource.labels.instance_name",
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
                            "instance_type": filestore_instance.get("tier", ""),
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
            _LOGGER.error(f"Failed to collect Filestore instances: {e}", exc_info=True)
            error_response = self.generate_resource_error_response(
                e, "Filestore", "Instance", "collection"
            )
            error_responses.append(error_response)

        _LOGGER.debug(
            f"** Filestore Instance Finished {time.time() - start_time} Seconds **"
        )
        return collected_cloud_services, error_responses

    def _process_networks(self, networks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process network information"""
        network_info = []
        for network in networks:
            network_info.append(
                {
                    "network": network.get("network", ""),
                    "modes": network.get("modes", []),
                    "reserved_ip_range": network.get("reservedIpRange", ""),
                    "connect_mode": network.get("connectMode", ""),
                }
            )
        return network_info

    def _process_file_shares_directly(
        self, file_shares: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Process file share information and calculate capacity"""
        unified_shares = []
        total_capacity_gb = 0

        for file_share in file_shares:
            capacity_gb = int(file_share.get("capacityGb", 0))
            total_capacity_gb += capacity_gb

            unified_shares.append(
                {
                    "name": file_share.get("name", ""),
                    "capacity_gb": str(capacity_gb),
                    "source_backup": file_share.get("sourceBackup", ""),
                    "nfs_export_options": file_share.get("nfsExportOptions", []),
                    "data_source": "Basic",
                }
            )

        return unified_shares, total_capacity_gb

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
