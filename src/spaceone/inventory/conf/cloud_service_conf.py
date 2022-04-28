MAX_WORKER = 20
SUPPORTED_RESOURCE_TYPE = ['inventory.Server', 'inventory.CloudService', 'inventory.CloudServiceType', 'inventory.Region', 'inventory.ErrorResource' ]
SUPPORTED_FEATURES = ['garbage_collection']
SUPPORTED_SCHEDULES = ['hours']
FILTER_FORMAT = []
CLOUD_SERVICE_GROUP_MAP = {
    'SQLWorkspace': 'SQLWorkspaceManager',
    'CloudSQL': 'CloudSQLManager',
    'Disk': 'DiskManager',
    'ExternalIPAddress': 'ExternalIPAddressManager',
    'Firewall': 'FirewallManager',
    'InstanceGroup': 'InstanceGroupManager',
    'InstanceTemplate': 'InstanceTemplateManager',
    'LoadBalancing': 'LoadBalancingManager',
    'MachineImage': 'MachineImageManager',
    'Route': 'RouteManager',
    'Snapshot': 'SnapshotManager',
    'Bucket': 'StorageManager',
    'VPCNetwork': 'VPCNetworkManager',
    'VMInstance': 'VMInstanceManager'
}
