MAX_WORKER = 20
SUPPORTED_RESOURCE_TYPE = ['inventory.Server', 'inventory.CloudService', 'inventory.CloudServiceType', 'inventory.Region', 'inventory.ErrorResource' ]
SUPPORTED_FEATURES = ['garbage_collection']
SUPPORTED_SCHEDULES = ['hours']
FILTER_FORMAT = []
CLOUD_SERVICE_GROUP_MAP = {
    'ComputeEngine': ['VMInstanceManager',
                      'SnapshotManager',
                      'MachineImageManager',
                      'InstanceTemplateManager',
                      'InstanceGroupManager',
                      'DiskManager'],
    'CloudSQL': ['CloudSQLManager'],
    'BigQuery': ['SQLWorkspaceManager'],
    'CloudStorage': ['StorageManager'],
    'Networking': ['ExternalIPAddressManager',
                   'FirewallManager',
                   'LoadBalancingManager',
                   'RouteManager',
                   'VPCNetworkManager']
}
