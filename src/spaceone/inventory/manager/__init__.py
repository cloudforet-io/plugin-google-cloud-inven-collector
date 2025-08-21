from spaceone.inventory.manager.cloud_sql.instance_manager import CloudSQLManager
from spaceone.inventory.manager.compute_engine.instance_group_manager import (
    InstanceGroupManager,
)
from spaceone.inventory.manager.compute_engine.instance_template_manager import (
    InstanceTemplateManager,
)
from spaceone.inventory.manager.compute_engine.machine_image_manager import (
    MachineImageManager,
)
from spaceone.inventory.manager.compute_engine.disk_manager import DiskManager
from spaceone.inventory.manager.compute_engine.snapshot_manager import SnapshotManager
from spaceone.inventory.manager.cloud_storage.storage_manager import StorageManager
from spaceone.inventory.manager.filestore.instance_manager import FilestoreInstanceManager
from spaceone.inventory.manager.networking.vpc_network_manager import VPCNetworkManager
from spaceone.inventory.manager.networking.external_ip_address_manager import (
    ExternalIPAddressManager,
)
from spaceone.inventory.manager.networking.firewall_manager import FirewallManager
from spaceone.inventory.manager.networking.route_manager import RouteManager
from spaceone.inventory.manager.networking.load_balancing_manager import (
    LoadBalancingManager,
)
from spaceone.inventory.manager.bigquery.sql_workspace_manager import (
    SQLWorkspaceManager,
)
from spaceone.inventory.manager.compute_engine.vm_instance_manager import (
    VMInstanceManager,
)
from spaceone.inventory.manager.pub_sub.schema_manager import SchemaManager
from spaceone.inventory.manager.pub_sub.snapshot_manager import SnapshotManager
from spaceone.inventory.manager.pub_sub.subscription_manager import SubscriptionManager
from spaceone.inventory.manager.pub_sub.topic_manager import TopicManager
from spaceone.inventory.manager.cloud_functions.function_gen2_manager import (
    FunctionGen2Manager,
)
from spaceone.inventory.manager.cloud_functions.function_gen1_manager import (
    FunctionGen1Manager,
)
from spaceone.inventory.manager.recommender.recommendation_manager import (
    RecommendationManager,
)
