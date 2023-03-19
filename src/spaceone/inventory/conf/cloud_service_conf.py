MAX_WORKER = 20
SUPPORTED_RESOURCE_TYPE = ['inventory.CloudService', 'inventory.CloudServiceType', 'inventory.Region',
                           'inventory.ErrorResource']
SUPPORTED_FEATURES = ['garbage_collection']
SUPPORTED_SCHEDULES = ['hours']
FILTER_FORMAT = []
CLOUD_SERVICE_GROUP_MAP = {
    'ComputeEngine': [
        'VMInstanceManager',
        'SnapshotManager',
        'MachineImageManager',
        'InstanceTemplateManager',
        'InstanceGroupManager',
        'DiskManager'
    ],
    'CloudSQL': [
        'CloudSQLManager'
    ],
    'BigQuery': [
        'SQLWorkspaceManager'
    ],
    'CloudStorage': [
        'StorageManager'
    ],
    'Networking': [
        'ExternalIPAddressManager',
        'FirewallManager',
        'LoadBalancingManager',
        'RouteManager',
        'VPCNetworkManager'
    ],
    'Pub/Sub': [
        'SchemaManager',
        'SnapshotManager',
        'SubscriptionManager',
        'TopicManager'
    ],
    'CloudFunctions': [
        'FunctionGen2Manager',
        'FunctionGen1Manager'
    ],
    'Recommender': [
        'InsightManager'
    ],
    'Recommender_v2': [
        'RecommendationManager'
    ]
}

ASSET_URL = 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud'

REGION_INFO = {
    "asia-east1": {"name": "Taiwan (Changhua County)",
                   "tags": {"latitude": "24.051196", "longitude": "120.516430", "continent": "asia_pacific"}},
    "asia-east2": {"name": "Hong Kong",
                   "tags": {"latitude": "22.283289", "longitude": "114.155851", "continent": "asia_pacific"}},
    "asia-northeast1": {"name": "Japan (Tokyo)",
                        "tags": {"latitude": "35.628391", "longitude": "139.417634", "continent": "asia_pacific"}},
    "asia-northeast2": {"name": "Japan (Osaka)",
                        "tags": {"latitude": "34.705403", "longitude": "135.490119", "continent": "asia_pacific"}},
    "asia-northeast3": {"name": "South Korea (Seoul)",
                        "tags": {"latitude": "37.499968", "longitude": "127.036376", "continent": "asia_pacific"}},
    "asia-south1": {"name": "India (Mumbai)",
                    "tags": {"latitude": "19.164951", "longitude": "72.851765", "continent": "asia_pacific"}},
    "asia-south2": {"name": "India (Delhi)",
                    "tags": {"latitude": "28.644800", "longitude": "77.216721", "continent": "asia_pacific"}},
    "asia-southeast1": {"name": "Singapore (Jurong West)",
                        "tags": {"latitude": "1.351376", "longitude": "103.709574", "continent": "asia_pacific"}},
    "asia-southeast2": {"name": "Indonesia (Jakarta)",
                        "tags": {"latitude": "-6.227851", "longitude": "106.808169", "continent": "asia_pacific"}},
    "australia-southeast1": {"name": "Australia (Sydney)", "tags": {"latitude": "-33.733694", "longitude": "150.969840",
                                                                    "continent": "asia_pacific"}},
    "australia-southeast2": {"name": "Australia (Melbourne)",
                             "tags": {"latitude": "-37.840935", "longitude": "144.946457",
                                      "continent": "asia_pacific"}},
    "europe-north1": {"name": "Finland (Hamina)",
                      "tags": {"latitude": "60.539504", "longitude": "27.113819", "continent": "europe"}},
    "europe-west1": {"name": "Belgium (St.Ghislain)",
                     "tags": {"latitude": "50.471248", "longitude": "3.825493", "continent": "europe"}},
    "europe-west2": {"name": "England, UK (London)",
                     "tags": {"latitude": "51.515998", "longitude": "-0.126918", "continent": "europe"}},
    "europe-west3": {"name": "Germany (Frankfurt)",
                     "tags": {"latitude": "50.115963", "longitude": "8.669625", "continent": "europe"}},
    "europe-west4": {"name": "Netherlands (Eemshaven)",
                     "tags": {"latitude": "53.427625", "longitude": "6.865703", "continent": "europe"}},
    "europe-west6": {"name": "Switzerland (Zürich)",
                     "tags": {"latitude": "47.365663", "longitude": "8.524881", "continent": "europe"}},
    "northamerica-northeast1": {"name": "Canada, Québec (Montréal)",
                                "tags": {"latitude": "45.501926", "longitude": "-73.570086",
                                         "continent": "north_america"}},
    "northamerica-northeast2": {"name": "Canada, Ontario (Toronto)",
                                "tags": {"latitude": "50.000000", "longitude": "-85.000000",
                                         "continent": "north_america"}},
    "southamerica-east1": {"name": "Brazil, São Paulo (Osasco)",
                           "tags": {"latitude": "43.8345", "longitude": "2.1972", "continent": "south_america"}},
    "southamerica-west1": {"name": "Chile (Santiago)",
                           "tags": {"latitude": "-33.447487", "longitude": "-70.673676", "continent": "south_america"}},
    "us-central1": {"name": "US, Iowa (Council Bluffs)",
                    "tags": {"latitude": "41.221419", "longitude": "-95.862676", "continent": "north_america"}},
    "us-east1": {"name": "US, South Carolina (Moncks Corner)",
                 "tags": {"latitude": "33.203394", "longitude": "-79.986329", "continent": "north_america"}},
    "us-east4": {"name": "US, Northern Virginia (Ashburn)",
                 "tags": {"latitude": "39.021075", "longitude": "-77.463569", "continent": "north_america"}},
    "us-west1": {"name": "US, Oregon (The Dalles)",
                 "tags": {"latitude": "45.631800", "longitude": "-121.200921", "continent": "north_america"}},
    "us-west2": {"name": "US, California (Los Angeles)",
                 "tags": {"latitude": "34.049329", "longitude": "-118.255265", "continent": "north_america"}},
    "us-west3": {"name": "US, Utah (Salt Lake City)",
                 "tags": {"latitude": "40.730109", "longitude": "-111.951386", "continent": "north_america"}},
    "us-west4": {"name": "US, Nevada (Las Vegas)",
                 "tags": {"latitude": "36.092498", "longitude": "-115.086073", "continent": "north_america"}},
    "global": {"name": "Global"}
}
