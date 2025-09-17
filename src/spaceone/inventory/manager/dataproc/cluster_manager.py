import logging
from typing import Any, Dict, List, Tuple

from spaceone.inventory.connector.dataproc.cluster_connector import (
    DataprocClusterConnector,
)
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.dataproc.cluster.cloud_service import (
    DataprocClusterResource,
    DataprocClusterResponse,
)
from spaceone.inventory.model.dataproc.cluster.cloud_service_type import (
    CLOUD_SERVICE_TYPES,
)
from spaceone.inventory.model.dataproc.cluster.data import (
    DataprocCluster,
)

logger = logging.getLogger(__name__)


class DataprocClusterManager(GoogleCloudManager):
    connector_name = "DataprocClusterConnector"
    cloud_service_types = CLOUD_SERVICE_TYPES
    cloud_service_group = "Dataproc"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_clusters(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Retrieve a list of Dataproc clusters.

        Args:
            params: Parameters to pass to the connector
                - secret_data: Google Cloud authentication information
                - options: Additional options

        Returns:
            List of Dataproc cluster resources

        Raises:
            Exception: When connector initialization fails
        """
        if not params or "secret_data" not in params:
            raise ValueError("secret_data is required in params")

        cluster_connector: DataprocClusterConnector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            clusters = cluster_connector.list_clusters()
            logger.info(
                f"📊 Successfully found {len(clusters)} Dataproc clusters "
                f"(parallel processing enabled)"
            )
            return clusters
        except Exception as e:
            logger.error(f"Failed to list Dataproc clusters: {e}")
            return []

    def get_cluster(
        self, cluster_name: str, region: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Retrieve specific Dataproc cluster information.

        Args:
            cluster_name (str): The name of the cluster.
            region (str): The region where the cluster is located.
            params (dict): Parameters to pass to the connector.

        Returns:
            dict: Cluster resource if found, otherwise empty dictionary.
        """
        cluster_connector: DataprocClusterConnector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            cluster = cluster_connector.get_cluster(cluster_name, region)
            if cluster:
                logger.info("Retrieved Dataproc cluster successfully")
            return cluster or {}
        except Exception as e:
            logger.error(f"Failed to get Dataproc cluster: {e}")
            return {}

    def list_jobs(
        self,
        region: str = None,
        cluster_name: str = None,
        params: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve a list of Dataproc jobs.

        Args:
            region (str, optional): Region to filter jobs.
            cluster_name (str, optional): Name of the cluster to filter jobs.
            params (dict, optional): Parameters to pass to the connector.

        Returns:
            list: List of Dataproc job resources.
        """
        if params is None:
            params = {}

        cluster_connector: DataprocClusterConnector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            jobs = cluster_connector.list_jobs(region=region, cluster_name=cluster_name)
            logger.info(
                f"⚡ Found {len(jobs)} Dataproc jobs "
                f"(parallel processing with optimized timeouts)"
            )
            return jobs
        except Exception as e:
            logger.error(f"Failed to list Dataproc jobs: {e}")
            return []

    def list_workflow_templates(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Retrieve a list of Dataproc workflow templates.

        Args:
            params (dict): Parameters to pass to the connector.

        Returns:
            list: List of Dataproc workflow template resources.
        """
        cluster_connector: DataprocClusterConnector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            templates = cluster_connector.list_workflow_templates()
            logger.info(f"Found {len(templates)} Dataproc workflow templates")
            return templates
        except Exception as e:
            logger.error(f"Failed to list Dataproc workflow templates: {e}")
            return []

    def list_autoscaling_policies(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Retrieve a list of Dataproc autoscaling policies.

        Args:
            params (dict): Parameters to pass to the connector.

        Returns:
            list: List of Dataproc autoscaling policy resources.
        """
        cluster_connector: DataprocClusterConnector = self.locator.get_connector(
            self.connector_name, **params
        )

        try:
            policies = cluster_connector.list_autoscaling_policies()
            logger.info(f"Found {len(policies)} Dataproc autoscaling policies")
            return policies
        except Exception as e:
            logger.error(f"Failed to list Dataproc autoscaling policies: {e}")
            return []

    def collect_cloud_service(
        self, params: Dict[str, Any]
    ) -> Tuple[List[DataprocClusterResponse], List[Dict[str, Any]]]:
        """
        Collect Dataproc cluster information and convert to Cloud Service resources.

        Args:
            params: Parameters for the collection process
                - secret_data: Google Cloud authentication information
                - options: Additional collection options

        Returns:
            Tuple of collected Cloud Service response list and error response list

        Raises:
            ValueError: When required parameters are missing
        """
        logger.debug("** Dataproc Cluster START **")

        if not params or "secret_data" not in params:
            raise ValueError("secret_data is required in params")

        collected_cloud_services = []
        error_responses = []

        secret_data = params["secret_data"]
        project_id = secret_data.get("project_id")

        if not project_id:
            raise ValueError("project_id is required in secret_data")

        # Retrieve Dataproc cluster list
        try:
            clusters = self.list_clusters(params)
            if not clusters:
                logger.info("No Dataproc clusters found")
                return collected_cloud_services, error_responses
        except Exception as e:
            logger.error(f"Failed to retrieve cluster list: {e}")
            error_responses.append(
                self.generate_error_response(e, self.cloud_service_group, "Cluster")
            )
            return collected_cloud_services, error_responses

        for cluster in clusters:
            try:
                # Extract cluster location information
                location = cluster.get("labels", {}).get("goog-dataproc-location", "")

                # Extract cluster name
                cluster_name = cluster.get("clusterName", "")
                cluster_uuid = cluster.get("clusterUuid", "")

                # Set up monitoring filters for Dataproc Cluster
                google_cloud_monitoring_filters = [
                    {
                        "key": "resource.labels.cluster_uuid",
                        "value": cluster_uuid,
                    },
                ]

                # Prepare basic cluster data
                cluster_data = {
                    "name": str(cluster.get("clusterName", "")),  # Map to name field
                    "cluster_name": str(cluster.get("clusterName", "")),
                    "project_id": str(project_id),  # Explicitly set project_id
                    "cluster_uuid": cluster_uuid,
                    "status": cluster.get("status", {}),
                    "labels": self._get_labels(labels=cluster.get("labels", {})),
                    "location": location,
                    "google_cloud_monitoring": self.set_google_cloud_monitoring(
                        project_id,
                        "dataproc.googleapis.com",
                        cluster_uuid,
                        google_cloud_monitoring_filters,
                    ),
                    "google_cloud_logging": self.set_google_cloud_logging(
                        "Dataproc", "Cluster", project_id, cluster_name
                    ),
                }

                # Add configuration information
                config = cluster.get("config", {})
                cluster_data["config"] = {
                    "config_bucket": str(config.get("configBucket", "")),
                    "temp_bucket": str(config.get("tempBucket", "")),
                }

                # GCE cluster configuration
                if "gceClusterConfig" in config:
                    gce_config = config["gceClusterConfig"]
                    cluster_data["config"]["gce_cluster_config"] = {
                        "zone_uri": str(gce_config.get("zoneUri", "")),
                        "network_uri": str(gce_config.get("networkUri", "")),
                        "subnetwork_uri": str(gce_config.get("subnetworkUri", "")),
                        "internal_ip_only": str(gce_config.get("internalIpOnly", "")),
                        "service_account": str(gce_config.get("serviceAccount", "")),
                        "service_account_scopes": gce_config.get(
                            "serviceAccountScopes", []
                        ),
                    }

                # Instance group configuration
                if "instanceGroupConfig" in config:
                    instance_config = config["instanceGroupConfig"]
                    cluster_data["config"]["instanceGroupConfig"] = {
                        "numInstances": str(instance_config.get("numInstances", "")),
                        "instanceNames": instance_config.get("instanceNames", []),
                        "imageUri": str(instance_config.get("imageUri", "")),
                        "machineTypeUri": str(
                            instance_config.get("machineTypeUri", "")
                        ),
                        "diskConfig": instance_config.get("diskConfig", {}),
                    }

                # Master configuration
                master_config = config.get("masterConfig", {})
                if master_config:
                    # Fix disk_config mapping
                    disk_config = master_config.get("diskConfig", {})
                    mapped_disk_config = {
                        "boot_disk_size_gb": disk_config.get("bootDiskSizeGb"),
                        "boot_disk_type": disk_config.get("bootDiskType"),
                    }

                    cluster_data["config"]["master_config"] = {
                        "num_instances": str(master_config.get("numInstances", "")),
                        "instance_names": master_config.get("instanceNames", []),
                        "image_uri": str(master_config.get("imageUri", "")),
                        "machine_type_uri": str(
                            master_config.get("machineTypeUri", "")
                        ),
                        "disk_config": mapped_disk_config,
                        "min_cpu_platform": str(
                            master_config.get("minCpuPlatform", "")
                        ),
                        "preemptibility": str(
                            master_config.get("preemptibility", "NON_PREEMPTIBLE")
                        ),
                    }
                else:
                    cluster_data["config"]["master_config"] = {
                        "num_instances": "",
                        "instance_names": [],
                        "image_uri": "",
                        "machine_type_uri": "",
                        "disk_config": {
                            "boot_disk_size_gb": None,
                            "boot_disk_type": None,
                        },
                        "min_cpu_platform": "",
                        "preemptibility": "NON_PREEMPTIBLE",
                    }

                # Worker configuration
                worker_config = config.get("workerConfig", {})
                if worker_config:
                    # Fix disk_config mapping
                    disk_config = worker_config.get("diskConfig", {})
                    mapped_disk_config = {
                        "boot_disk_size_gb": disk_config.get("bootDiskSizeGb"),
                        "boot_disk_type": disk_config.get("bootDiskType"),
                    }

                    cluster_data["config"]["worker_config"] = {
                        "num_instances": str(worker_config.get("numInstances", "")),
                        "instance_names": worker_config.get("instanceNames", []),
                        "image_uri": str(worker_config.get("imageUri", "")),
                        "machine_type_uri": str(
                            worker_config.get("machineTypeUri", "")
                        ),
                        "disk_config": mapped_disk_config,
                        "min_cpu_platform": str(
                            worker_config.get("minCpuPlatform", "")
                        ),
                        "is_preemptible": worker_config.get("isPreemptible", False),
                        "preemptibility": str(
                            worker_config.get("preemptibility", "NON_PREEMPTIBLE")
                        ),
                    }
                else:
                    cluster_data["config"]["worker_config"] = {
                        "num_instances": "",
                        "instance_names": [],
                        "image_uri": "",
                        "machine_type_uri": "",
                        "disk_config": {
                            "boot_disk_size_gb": None,
                            "boot_disk_type": None,
                        },
                        "min_cpu_platform": "",
                        "is_preemptible": False,
                        "preemptibility": "NON_PREEMPTIBLE",
                    }

                # Software configuration
                software_config = config.get("softwareConfig", {})
                if software_config:
                    cluster_data["config"]["software_config"] = {
                        "image_version": str(software_config.get("imageVersion", "")),
                        "properties": software_config.get("properties", {}),
                        "optional_components": software_config.get(
                            "optionalComponents", []
                        ),
                    }
                else:
                    cluster_data["config"]["software_config"] = {
                        "image_version": "",
                        "properties": {},
                        "optional_components": [],
                    }

                # Lifecycle Config (Scheduled Deletion)
                lifecycle_config = config.get("lifecycleConfig", {})
                if lifecycle_config:
                    cluster_data["config"]["lifecycle_config"] = {
                        "auto_delete_time": str(
                            lifecycle_config.get("autoDeleteTime", "")
                        ),
                        "auto_delete_ttl": str(
                            lifecycle_config.get("autoDeleteTtl", "")
                        ),
                        "idle_delete_ttl": str(
                            lifecycle_config.get("idleDeleteTtl", "")
                        ),
                    }
                else:
                    cluster_data["config"]["lifecycle_config"] = {
                        "auto_delete_time": "",
                        "auto_delete_ttl": "",
                        "idle_delete_ttl": "",
                    }

                # Add metrics information
                if "metrics" in cluster:
                    cluster_data["metrics"] = cluster["metrics"]

                # Optimize job information collection - collect selectively for performance improvement
                cluster_data["jobs"] = []
                # Job collection is performed only when there is a separate option (performance optimization)
                if params.get("options", {}).get("include_jobs", False):
                    try:
                        # Extract region from cluster location
                        cluster_region = (
                            location.rsplit("-", 1)[0]
                            if location and "-" in location
                            else location
                        )
                        if cluster_region:
                            jobs = self.list_jobs(
                                region=cluster_region,
                                cluster_name=cluster_name,
                                params=params,
                            )
                            if jobs:
                                # Collect recent jobs (limited for performance optimization)
                                job_limit = min(5, len(jobs))  # Reduce to maximum 5
                                for job in jobs[:job_limit]:
                                    job_data = {
                                        "reference": job.get("reference", {}),
                                        "placement": job.get("placement", {}),
                                        "status": job.get("status", {}),
                                        "labels": job.get("labels", {}),
                                        "jobUuid": job.get("jobUuid", ""),
                                    }
                                    cluster_data["jobs"].append(job_data)
                    except Exception as e:
                        logger.warning(f"Failed to collect jobs for cluster: {e}")
                        # jobs is already initialized as empty array
                else:
                    # Skip job collection - performance optimization
                    logger.debug("Job collection skipped for performance optimization")

                # Create DataprocCluster model
                dataproc_cluster_data = DataprocCluster(cluster_data, strict=False)

                # Create DataprocClusterResource
                cluster_resource = DataprocClusterResource(
                    {
                        "name": cluster_data.get("name"),
                        "data": dataproc_cluster_data,
                        "region_code": location,
                        "account": project_id,
                        "reference": ReferenceModel(dataproc_cluster_data.reference()),
                    }
                )

                ##################################
                # 4. Make Collected Region Code
                ##################################
                self.set_region_code(location)

                # Create DataprocClusterResponse
                cluster_response = DataprocClusterResponse(
                    {"resource": cluster_resource}
                )

                collected_cloud_services.append(cluster_response)

            except Exception as e:
                logger.error(f"[collect_cloud_service] => {e}", exc_info=True)
                error_responses.append(
                    self.generate_error_response(e, self.cloud_service_group, "Cluster")
                )

        logger.debug("** Dataproc Cluster END **")
        return collected_cloud_services, error_responses

    @staticmethod
    def _get_labels(labels):
        changed_labels = []
        for label_key, label_value in labels.items():
            changed_labels.append({"key": label_key, "value": label_value})
        return changed_labels
