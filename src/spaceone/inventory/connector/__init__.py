from spaceone.inventory.connector.batch.batch_connector import BatchConnector
from spaceone.inventory.connector.bigquery.sql_workspace import SQLWorkspaceConnector
from spaceone.inventory.connector.cloud_functions.eventarc import EventarcConnector
from spaceone.inventory.connector.cloud_functions.function_gen1 import (
    FunctionGen1Connector,
)
from spaceone.inventory.connector.cloud_functions.function_gen2 import (
    FunctionGen2Connector,
)
from spaceone.inventory.connector.cloud_run.cloud_run_v1 import CloudRunV1Connector
from spaceone.inventory.connector.cloud_run.cloud_run_v2 import CloudRunV2Connector
from spaceone.inventory.connector.cloud_sql.instance import CloudSQLInstanceConnector
from spaceone.inventory.connector.cloud_storage.monitoring import MonitoringConnector
from spaceone.inventory.connector.cloud_storage.storage import StorageConnector
from spaceone.inventory.connector.compute_engine.disk import DiskConnector
from spaceone.inventory.connector.compute_engine.instance_group import (
    InstanceGroupConnector,
)
from spaceone.inventory.connector.compute_engine.instance_template import (
    InstanceTemplateConnector,
)
from spaceone.inventory.connector.compute_engine.machine_image import (
    MachineImageConnector,
)
from spaceone.inventory.connector.compute_engine.snapshot import SnapshotConnector
from spaceone.inventory.connector.compute_engine.vm_instance import VMInstanceConnector
from spaceone.inventory.connector.filestore.instance_v1 import (
    FilestoreInstanceConnector,
)
from spaceone.inventory.connector.filestore.instance_v1beta1 import (
    FilestoreInstanceV1Beta1Connector,
)
from spaceone.inventory.connector.firebase.project import FirebaseProjectConnector
from spaceone.inventory.connector.kubernetes_engine.cluster_v1 import (
    GKEClusterV1Connector,
)
from spaceone.inventory.connector.kubernetes_engine.cluster_v1beta import (
    GKEClusterV1BetaConnector,
)
from spaceone.inventory.connector.networking.external_ip_address import (
    ExternalIPAddressConnector,
)
from spaceone.inventory.connector.networking.firewall import FirewallConnector
from spaceone.inventory.connector.networking.load_balancing import (
    LoadBalancingConnector,
)
from spaceone.inventory.connector.networking.route import RouteConnector
from spaceone.inventory.connector.networking.vpc_network import VPCNetworkConnector
from spaceone.inventory.connector.pub_sub.schema import SchemaConnector
from spaceone.inventory.connector.pub_sub.snapshot import SnapshotConnector
from spaceone.inventory.connector.pub_sub.subscription import SubscriptionConnector
from spaceone.inventory.connector.pub_sub.topic import TopicConnector
from spaceone.inventory.connector.recommender.cloud_asset import CloudAssetConnector
from spaceone.inventory.connector.recommender.insight import InsightConnector
from spaceone.inventory.connector.recommender.recommendation import (
    RecommendationConnector,
)
from spaceone.inventory.connector.recommender.cloud_asset import CloudAssetConnector
from spaceone.inventory.connector.kubernetes_engine.cluster_v1 import GKEClusterV1Connector
from spaceone.inventory.connector.kubernetes_engine.cluster_v1beta import GKEClusterV1BetaConnector
from spaceone.inventory.connector.app_engine.application_v1 import AppEngineApplicationV1Connector
from spaceone.inventory.connector.app_engine.service_v1 import AppEngineServiceV1Connector
from spaceone.inventory.connector.app_engine.version_v1 import AppEngineVersionV1Connector
from spaceone.inventory.connector.app_engine.instance_v1 import AppEngineInstanceV1Connector
from spaceone.inventory.connector.datastore.index_v1 import DatastoreIndexV1Connector
from spaceone.inventory.connector.datastore.namespace_v1 import (
    DatastoreNamespaceV1Connector,
)
